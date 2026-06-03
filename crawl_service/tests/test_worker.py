from __future__ import annotations

import unittest
from datetime import date
from types import SimpleNamespace
from unittest.mock import patch

from crawl_service.tests.domain.documents.helpers import artifact_document
from crawl_service.morgue.types import MorgueFile, MorgueUser
from crawl_service.processor import (
    CURRENT_PARSER_VERSION,
    CURRENT_SCORING_VERSION,
    process_pending_raw_morgue_files,
)
from crawl_service.repository import (
    CrawlFileRecord,
    CrawlUserRecord,
    FETCH_STATUS_FAILED,
    FETCH_STATUS_FETCHED,
    PROCESS_STATUS_FAILED,
    PROCESS_STATUS_PROCESSED,
    RawMorgueFileRecord,
)
from crawl_service.worker import (
    CrawlWorker,
    CrawlWorkerConfig,
    RequestThrottle,
    USER_SKIP_MODE_MODIFIED_AT,
    config_from_env,
)


class FakeRepository:
    def __init__(self) -> None:
        self.artifacts = []
        self.file_records: dict[tuple[str, str], CrawlFileRecord] = {}
        self.user_records: dict[str, CrawlUserRecord] = {}
        self.raw_records: dict[tuple[str, str], RawMorgueFileRecord] = {}
        self.replaced_sources: list[tuple[str, str, int]] = []

    def replace_artifacts_for_source(self, player, source_file, artifacts):
        self.replaced_sources.append((player, source_file, len(artifacts)))
        self.artifacts = [
            artifact
            for artifact in self.artifacts
            if not (
                artifact.source.player.lower() == player.lower()
                and artifact.source.file == source_file
            )
        ]
        self.artifacts.extend(artifacts)

    def get_crawl_file_record(self, player, source_file):
        return self.file_records.get((player.lower(), source_file))

    def save_crawl_file_record(self, record):
        self.file_records[(record.player.lower(), record.name)] = record

    def get_crawl_user_record(self, player):
        return self.user_records.get(player.lower())

    def save_crawl_user_record(self, record):
        self.user_records[record.player.lower()] = record

    def get_raw_morgue_file(self, player, source_file):
        return self.raw_records.get((player.lower(), source_file))

    def save_raw_morgue_file(self, record):
        self.raw_records[(record.player.lower(), record.name)] = record

    def list_raw_morgue_files_for_processing(self, *, parser_version, scoring_version, limit):
        records = [
            record
            for record in self.raw_records.values()
            if record.fetch_status == FETCH_STATUS_FETCHED
            and (
                record.process_status in {"pending", PROCESS_STATUS_FAILED}
                or record.parser_version != parser_version
                or record.scoring_version != scoring_version
            )
        ]
        return records[:limit]


class CrawlWorkerTest(unittest.TestCase):
    def test_worker_scans_unchanged_users_by_default(self) -> None:
        repository = FakeRepository()
        repository.save_crawl_user_record(
            CrawlUserRecord(
                player="same",
                url="https://example.test/morgue/same/",
                observed_at="2026-Jan-02 00:00",
                status="completed",
            )
        )
        list_files_calls: list[str] = []

        worker = CrawlWorker(
            repository,
            config=_config(),
            throttle=RequestThrottle(0, sleep=lambda _seconds: None),
            list_users=lambda *args, **kwargs: [
                MorgueUser("same", "https://example.test/morgue/same/", "2026-Jan-02 00:00")
            ],
            list_files=lambda url, **kwargs: list_files_calls.append(url) or [],
        )

        summary = worker.run_once()

        self.assertEqual(summary.users_skipped_unchanged, 0)
        self.assertEqual(summary.users_scanned, 1)
        self.assertEqual(list_files_calls, ["https://example.test/morgue/same/"])

    def test_worker_can_skip_old_and_unchanged_users_by_modified_at(self) -> None:
        repository = FakeRepository()
        repository.save_crawl_user_record(
            CrawlUserRecord(
                player="same",
                url="https://example.test/morgue/same/",
                observed_at="2026-Jan-02 00:00",
                status="completed",
            )
        )
        list_files_calls: list[str] = []

        worker = CrawlWorker(
            repository,
            config=_config(user_skip_mode=USER_SKIP_MODE_MODIFIED_AT),
            throttle=RequestThrottle(0, sleep=lambda _seconds: None),
            list_users=lambda *args, **kwargs: [
                MorgueUser("old", "https://example.test/morgue/old/", "2025-Dec-31 23:59"),
                MorgueUser("same", "https://example.test/morgue/same/", "2026-Jan-02 00:00"),
                MorgueUser("changed", "https://example.test/morgue/changed/", "2026-Jan-03 00:00"),
            ],
            list_files=lambda url, **kwargs: list_files_calls.append(url) or [],
        )

        summary = worker.run_once()

        self.assertEqual(summary.users_skipped_by_date, 1)
        self.assertEqual(summary.users_skipped_unchanged, 1)
        self.assertEqual(summary.users_scanned, 1)
        self.assertEqual(list_files_calls, ["https://example.test/morgue/changed/"])
        self.assertEqual(repository.user_records["changed"].observed_at, "2026-Jan-03 00:00")

    def test_worker_stores_only_files_on_or_after_start_date(self) -> None:
        repository = FakeRepository()
        fetched_urls: list[str] = []
        sleeps: list[float] = []

        def fetch_file_text(url: str, **kwargs):
            fetched_urls.append(url)
            return "Inventory:\n a - the ring \"Miracles\" {rCorr AC+4}\n   Skills:"

        worker = CrawlWorker(
            repository,
            config=_config(request_delay_seconds=1),
            throttle=RequestThrottle(1, sleep=sleeps.append),
            list_users=lambda *args, **kwargs: [
                MorgueUser("wiiwiwi", "https://example.test/morgue/wiiwiwi/", "2026-Jan-02 00:00")
            ],
            list_files=lambda *args, **kwargs: [
                MorgueFile(
                    "morgue-wiiwiwi-20251231-235959.txt",
                    "https://example.test/old.txt",
                ),
                MorgueFile(
                    "morgue-wiiwiwi-20260101-000001.txt",
                    "https://example.test/new.txt",
                ),
            ],
            fetch_file_text=fetch_file_text,
        )

        summary = worker.run_once()

        self.assertEqual(fetched_urls, ["https://example.test/new.txt"])
        self.assertEqual(repository.replaced_sources, [])
        self.assertEqual(
            repository.file_records[("wiiwiwi", "morgue-wiiwiwi-20260101-000001.txt")].status,
            "completed",
        )
        self.assertEqual(
            repository.file_records[
                ("wiiwiwi", "morgue-wiiwiwi-20260101-000001.txt")
            ].artifact_count,
            0,
        )
        raw_record = repository.raw_records[("wiiwiwi", "morgue-wiiwiwi-20260101-000001.txt")]
        self.assertEqual(raw_record.fetch_status, FETCH_STATUS_FETCHED)
        self.assertEqual(raw_record.process_status, "pending")
        self.assertEqual(raw_record.parser_version, None)
        self.assertEqual(raw_record.scoring_version, None)
        self.assertEqual(repository.user_records["wiiwiwi"].status, "completed")
        self.assertEqual(summary.files_processed, 1)
        self.assertEqual(summary.artifacts_imported, 0)
        self.assertEqual(len(sleeps), 3)

    def test_worker_stores_txt_and_lst_raw_files(self) -> None:
        repository = FakeRepository()

        def fetch_file_text(url: str, **kwargs):
            return f"raw body for {url}"

        worker = CrawlWorker(
            repository,
            config=_config(),
            throttle=RequestThrottle(0, sleep=lambda _seconds: None),
            list_users=lambda *args, **kwargs: [
                MorgueUser("wiiwiwi", "https://example.test/morgue/wiiwiwi/", "2026-Jan-02 00:00")
            ],
            list_files=lambda *args, **kwargs: [
                MorgueFile(
                    "morgue-wiiwiwi-20260101-000001.txt",
                    "https://example.test/new.txt",
                ),
                MorgueFile(
                    "morgue-wiiwiwi-20260101-000001.lst",
                    "https://example.test/new.lst",
                ),
            ],
            fetch_file_text=fetch_file_text,
        )

        summary = worker.run_once()

        txt_record = repository.raw_records[("wiiwiwi", "morgue-wiiwiwi-20260101-000001.txt")]
        lst_record = repository.raw_records[("wiiwiwi", "morgue-wiiwiwi-20260101-000001.lst")]
        self.assertEqual(txt_record.extension, "txt")
        self.assertEqual(txt_record.text, "raw body for https://example.test/new.txt")
        self.assertEqual(txt_record.fetch_status, FETCH_STATUS_FETCHED)
        self.assertEqual(txt_record.process_status, "pending")
        self.assertEqual(lst_record.extension, "lst")
        self.assertEqual(lst_record.text, "raw body for https://example.test/new.lst")
        self.assertEqual(lst_record.fetch_status, FETCH_STATUS_FETCHED)
        self.assertEqual(lst_record.process_status, "pending")
        self.assertEqual(summary.files_processed, 2)
        self.assertEqual(summary.artifacts_imported, 0)

    def test_worker_records_fetch_failure_without_processing_failure(self) -> None:
        repository = FakeRepository()

        def fetch_file_text(url: str, **kwargs):
            raise RuntimeError("network down")

        worker = CrawlWorker(
            repository,
            config=_config(),
            throttle=RequestThrottle(0, sleep=lambda _seconds: None),
            list_users=lambda *args, **kwargs: [
                MorgueUser("bad", "https://example.test/morgue/bad/", "2026-Jan-02 00:00")
            ],
            list_files=lambda *args, **kwargs: [
                MorgueFile(
                    "morgue-bad-20260101-000001.txt",
                    "https://example.test/bad.txt",
                )
            ],
            fetch_file_text=fetch_file_text,
        )

        summary = worker.run_once()

        raw_record = repository.raw_records[("bad", "morgue-bad-20260101-000001.txt")]
        self.assertEqual(summary.users_failed, 1)
        self.assertEqual(raw_record.fetch_status, FETCH_STATUS_FAILED)
        self.assertEqual(raw_record.process_status, "pending")
        self.assertEqual(raw_record.fetch_error, "network down")
        self.assertIsNone(raw_record.process_error)

    def test_worker_continues_after_user_failure(self) -> None:
        repository = FakeRepository()

        def list_files(url: str, **kwargs):
            if url.endswith("/bad/"):
                raise RuntimeError("directory failed")
            return []

        worker = CrawlWorker(
            repository,
            config=_config(),
            throttle=RequestThrottle(0, sleep=lambda _seconds: None),
            list_users=lambda *args, **kwargs: [
                MorgueUser("bad", "https://example.test/morgue/bad/", "2026-Jan-02 00:00"),
                MorgueUser("good", "https://example.test/morgue/good/", "2026-Jan-03 00:00"),
            ],
            list_files=list_files,
        )

        summary = worker.run_once()

        self.assertEqual(summary.users_failed, 1)
        self.assertEqual(summary.users_scanned, 1)
        self.assertEqual(repository.user_records["bad"].status, "failed")
        self.assertEqual(repository.user_records["good"].status, "completed")

    def test_worker_retries_failed_user_even_when_observed_date_is_unchanged(self) -> None:
        repository = FakeRepository()
        repository.save_crawl_user_record(
            CrawlUserRecord(
                player="retry",
                url="https://example.test/morgue/retry/",
                observed_at="2026-Jan-02 00:00",
                status="failed",
            )
        )
        list_files_calls: list[str] = []

        worker = CrawlWorker(
            repository,
            config=_config(),
            throttle=RequestThrottle(0, sleep=lambda _seconds: None),
            list_users=lambda *args, **kwargs: [
                MorgueUser("retry", "https://example.test/morgue/retry/", "2026-Jan-02 00:00")
            ],
            list_files=lambda url, **kwargs: list_files_calls.append(url) or [],
        )

        summary = worker.run_once()

        self.assertEqual(summary.users_skipped_unchanged, 0)
        self.assertEqual(summary.users_scanned, 1)
        self.assertEqual(list_files_calls, ["https://example.test/morgue/retry/"])

    def test_worker_skips_fetched_raw_files(self) -> None:
        repository = FakeRepository()
        repository.save_raw_morgue_file(
            RawMorgueFileRecord.fetched(
                player="wiiwiwi",
                name="morgue-wiiwiwi-20260101-000001.txt",
                url="https://example.test/new.txt",
                extension="txt",
                text="raw text",
                fetched_at="2026-01-01T00:00:00+00:00",
            )
        )
        fetch_file_text = SimpleNamespace(calls=0)

        def fake_fetch(url: str, **kwargs):
            fetch_file_text.calls += 1
            return ""

        worker = CrawlWorker(
            repository,
            config=_config(),
            throttle=RequestThrottle(0, sleep=lambda _seconds: None),
            list_users=lambda *args, **kwargs: [
                MorgueUser("wiiwiwi", "https://example.test/morgue/wiiwiwi/", "2026-Jan-02 00:00")
            ],
            list_files=lambda *args, **kwargs: [
                MorgueFile(
                    "morgue-wiiwiwi-20260101-000001.txt",
                    "https://example.test/new.txt",
                )
            ],
            fetch_file_text=fake_fetch,
        )

        summary = worker.run_once()

        self.assertEqual(fetch_file_text.calls, 0)
        self.assertEqual(summary.files_processed, 0)
        self.assertEqual(summary.files_skipped_existing_raw, 1)

    def test_worker_does_not_skip_when_only_crawl_file_cache_exists(self) -> None:
        repository = FakeRepository()
        repository.save_crawl_file_record(
            CrawlFileRecord(
                player="wiiwiwi",
                name="morgue-wiiwiwi-20260101-000001.txt",
                url="https://example.test/new.txt",
                status="completed",
                artifact_count=1,
                processed_at="2026-01-01T00:00:00+00:00",
                error=None,
            )
        )
        fetch_file_text = SimpleNamespace(calls=0)

        def fake_fetch(url: str, **kwargs):
            fetch_file_text.calls += 1
            return "raw text"

        worker = CrawlWorker(
            repository,
            config=_config(),
            throttle=RequestThrottle(0, sleep=lambda _seconds: None),
            list_users=lambda *args, **kwargs: [
                MorgueUser("wiiwiwi", "https://example.test/morgue/wiiwiwi/", "2026-Jan-02 00:00")
            ],
            list_files=lambda *args, **kwargs: [
                MorgueFile(
                    "morgue-wiiwiwi-20260101-000001.txt",
                    "https://example.test/new.txt",
                )
            ],
            fetch_file_text=fake_fetch,
        )

        summary = worker.run_once()

        raw_record = repository.raw_records[("wiiwiwi", "morgue-wiiwiwi-20260101-000001.txt")]
        self.assertEqual(fetch_file_text.calls, 1)
        self.assertEqual(raw_record.text, "raw text")
        self.assertEqual(raw_record.fetch_status, FETCH_STATUS_FETCHED)
        self.assertEqual(summary.files_processed, 1)

    def test_worker_pass_processes_pending_raw_files_after_ingest(self) -> None:
        repository = FakeRepository()
        calls: list[int] = []

        def process_pending(repository_arg, *, limit: int):
            self.assertIs(repository_arg, repository)
            calls.append(limit)
            return 7

        worker = CrawlWorker(
            repository,
            config=_config(process_limit=12),
            throttle=RequestThrottle(0, sleep=lambda _seconds: None),
            list_users=lambda *args, **kwargs: [],
            process_pending=process_pending,
        )

        summary = worker.run_pass()

        self.assertEqual(calls, [12])
        self.assertEqual(summary.crawl.users_seen, 0)
        self.assertEqual(summary.process.artifacts_imported, 7)
        self.assertFalse(summary.process.failed)

    def test_worker_pass_records_processing_failure_without_raising(self) -> None:
        repository = FakeRepository()

        def process_pending(repository_arg, *, limit: int):
            raise RuntimeError("parser failed")

        worker = CrawlWorker(
            repository,
            config=_config(),
            throttle=RequestThrottle(0, sleep=lambda _seconds: None),
            list_users=lambda *args, **kwargs: [],
            process_pending=process_pending,
        )

        summary = worker.run_pass()

        self.assertTrue(summary.process.failed)
        self.assertEqual(summary.process.error, "parser failed")

    def test_worker_pass_skips_processing_when_limit_is_zero(self) -> None:
        repository = FakeRepository()
        calls = SimpleNamespace(count=0)

        def process_pending(repository_arg, *, limit: int):
            calls.count += 1
            return 1

        worker = CrawlWorker(
            repository,
            config=_config(process_limit=0),
            throttle=RequestThrottle(0, sleep=lambda _seconds: None),
            list_users=lambda *args, **kwargs: [],
            process_pending=process_pending,
        )

        summary = worker.run_pass()

        self.assertEqual(calls.count, 0)
        self.assertEqual(summary.process.artifacts_imported, 0)

    def test_config_from_env_reads_process_limit(self) -> None:
        with patch.dict("os.environ", {"CRAWL_PROCESS_LIMIT": "25"}, clear=False):
            self.assertEqual(config_from_env().process_limit, 25)

    def test_process_pending_raw_files_rebuilds_artifacts_without_fetching(self) -> None:
        repository = FakeRepository()
        repository.save_raw_morgue_file(
            RawMorgueFileRecord.fetched(
                player="wiiwiwi",
                name="morgue-wiiwiwi-20260101-000001.txt",
                url="https://example.test/new.txt",
                extension="txt",
                text="Inventory:\n a - the ring \"Miracles\" {rCorr AC+4}\n   Skills:",
                fetched_at="2026-01-01T00:00:00+00:00",
            )
        )
        document = artifact_document(
            name='the ring "Miracles" {rCorr AC+4}',
            source_name="morgue-wiiwiwi-20260101-000001.txt",
            attributes=["rCorr", "AC+4"],
        )

        with patch("crawl_service.processor.artifact_documents_from_raw_text", return_value=[document]):
            artifact_count = process_pending_raw_morgue_files(repository)

        raw_record = repository.raw_records[("wiiwiwi", "morgue-wiiwiwi-20260101-000001.txt")]
        self.assertEqual(artifact_count, 1)
        self.assertEqual(repository.replaced_sources, [("wiiwiwi", raw_record.name, 1)])
        self.assertEqual(raw_record.process_status, PROCESS_STATUS_PROCESSED)
        self.assertEqual(raw_record.parser_version, CURRENT_PARSER_VERSION)
        self.assertEqual(raw_record.scoring_version, CURRENT_SCORING_VERSION)


def _config(
    request_delay_seconds: float = 0,
    user_skip_mode: str = "conservative",
    process_limit: int = 100,
) -> CrawlWorkerConfig:
    return CrawlWorkerConfig(
        base_url="https://example.test/morgue/",
        start_date=date(2026, 1, 1),
        request_delay_seconds=request_delay_seconds,
        loop_interval_seconds=10_800,
        user_skip_mode=user_skip_mode,
        process_limit=process_limit,
    )


if __name__ == "__main__":
    unittest.main()
