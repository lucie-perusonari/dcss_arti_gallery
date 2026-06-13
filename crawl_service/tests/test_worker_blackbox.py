from __future__ import annotations

import unittest
from datetime import date

from crawl_service.fetcher import MorgueFile, MorgueUser
from crawl_service.repository import (
    CrawlFileRecord,
    CrawlUserRecord,
    FETCH_STATUS_FAILED,
    FETCH_STATUS_FETCHED,
    RawMorgueFileRecord,
)
from crawl_service.worker import (
    CrawlWorker,
    CrawlWorkerConfig,
    RequestThrottle,
    USER_SKIP_MODE_MODIFIED_AT,
)


class _Repository:
    def __init__(self) -> None:
        self.crawl_files: dict[tuple[str, str], CrawlFileRecord] = {}
        self.crawl_users: dict[str, CrawlUserRecord] = {}
        self.raw_files: dict[tuple[str, str], RawMorgueFileRecord] = {}

    def save_crawl_file_record(self, record: CrawlFileRecord) -> None:
        self.crawl_files[(record.player.lower(), record.name)] = record

    def list_crawl_user_records(self, players: list[str]) -> dict[str, CrawlUserRecord]:
        keys = {player.lower() for player in players}
        return {key: record for key, record in self.crawl_users.items() if key in keys}

    def save_crawl_user_record(self, record: CrawlUserRecord) -> None:
        self.crawl_users[record.player.lower()] = record

    def list_raw_morgue_file_records_for_player_files(
        self,
        player: str,
        source_files: list[str],
    ) -> dict[str, RawMorgueFileRecord]:
        names = set(source_files)
        return {
            name: record
            for (record_player, name), record in self.raw_files.items()
            if record_player == player.lower() and name in names
        }

    def save_raw_morgue_file(self, record: RawMorgueFileRecord) -> None:
        self.raw_files[(record.player.lower(), record.name)] = record


class WorkerBlackBoxTest(unittest.TestCase):
    def test_worker_fetches_only_new_eligible_files_and_records_summary(self) -> None:
        repository = _Repository()
        existing = RawMorgueFileRecord.fetched(
            player="wiiwiwi",
            name="morgue-wiiwiwi-20260101-000001.txt",
            url="https://example.test/existing.txt",
            extension="txt",
            text="existing",
            fetched_at="2026-01-01T00:00:00+00:00",
        )
        repository.save_raw_morgue_file(existing)
        fetched_urls: list[str] = []

        worker = CrawlWorker(
            repository,
            config=_config(),
            throttle=RequestThrottle(0, sleep=lambda _seconds: None),
            list_users=lambda *args, **kwargs: [
                MorgueUser("wiiwiwi", "https://example.test/morgue/wiiwiwi/", "2026-Jan-02 00:00")
            ],
            list_files=lambda *args, **kwargs: [
                MorgueFile("morgue-wiiwiwi-20251231-235959.txt", "https://example.test/old.txt"),
                MorgueFile("morgue-wiiwiwi-20260101-000001.txt", "https://example.test/existing.txt"),
                MorgueFile("morgue-wiiwiwi-20260102-000001.lst", "https://example.test/new.lst"),
                MorgueFile("morgue-wiiwiwi-20260102-000001.lst", "https://example.test/duplicate.lst"),
            ],
            fetch_file_text=lambda url, **kwargs: fetched_urls.append(url) or "new raw",
        )

        summary = worker._crawl_once()

        self.assertEqual(fetched_urls, ["https://example.test/new.lst"])
        self.assertEqual(summary.users_seen, 1)
        self.assertEqual(summary.users_scanned, 1)
        self.assertEqual(summary.files_processed, 1)
        self.assertEqual(summary.files_skipped_existing_raw, 2)
        new_record = repository.raw_files[("wiiwiwi", "morgue-wiiwiwi-20260102-000001.lst")]
        self.assertEqual(new_record.text, "new raw")
        self.assertEqual(new_record.fetch_status, FETCH_STATUS_FETCHED)
        self.assertEqual(repository.crawl_users["wiiwiwi"].stored_files, 1)

    def test_worker_skips_unchanged_user_when_modified_at_mode_is_enabled(self) -> None:
        repository = _Repository()
        repository.save_crawl_user_record(
            CrawlUserRecord(
                player="wiiwiwi",
                url="https://example.test/morgue/wiiwiwi/",
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
                MorgueUser("wiiwiwi", "https://example.test/morgue/wiiwiwi/", "2026-Jan-02 00:00")
            ],
            list_files=lambda url, **kwargs: list_files_calls.append(url) or [],
        )

        summary = worker._crawl_once()

        self.assertEqual(list_files_calls, [])
        self.assertEqual(summary.users_skipped_unchanged, 1)
        self.assertEqual(summary.users_scanned, 0)

    def test_worker_records_fetch_failures(self) -> None:
        repository = _Repository()

        def fail_fetch(*args, **kwargs):
            raise RuntimeError("network down")

        worker = CrawlWorker(
            repository,
            config=_config(),
            throttle=RequestThrottle(0, sleep=lambda _seconds: None),
            list_users=lambda *args, **kwargs: [
                MorgueUser("bad", "https://example.test/morgue/bad/", "2026-Jan-02 00:00")
            ],
            list_files=lambda *args, **kwargs: [
                MorgueFile("morgue-bad-20260101-000001.txt", "https://example.test/bad.txt")
            ],
            fetch_file_text=fail_fetch,
        )

        summary = worker._crawl_once()

        raw_record = repository.raw_files[("bad", "morgue-bad-20260101-000001.txt")]
        file_record = repository.crawl_files[("bad", "morgue-bad-20260101-000001.txt")]
        self.assertEqual(raw_record.fetch_status, FETCH_STATUS_FAILED)
        self.assertIn("network down", raw_record.fetch_error or "")
        self.assertEqual(file_record.status, "failed")
        self.assertEqual(summary.users_failed, 1)


def _config(user_skip_mode: str = "conservative") -> CrawlWorkerConfig:
    return CrawlWorkerConfig(
        base_url="https://example.test/morgue",
        start_date=date(2026, 1, 1),
        request_delay_seconds=0,
        loop_interval_seconds=0,
        timeout=1,
        user_agent="test-agent",
        user_skip_mode=user_skip_mode,
    )


if __name__ == "__main__":
    unittest.main()
