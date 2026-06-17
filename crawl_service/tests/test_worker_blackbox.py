from __future__ import annotations

import unittest
from unittest.mock import patch

from crawl_service.fetcher import MorgueFile, MorgueUser
from crawl_service.repository import (
    CrawlErrorRecord,
    FETCH_STATUS_FETCHED,
    RawMorgueFileRecord,
)
from crawl_service.worker import (
    CrawlWorker,
)


class _Repository:
    def __init__(self) -> None:
        self.crawl_errors: list[CrawlErrorRecord] = []
        self.raw_files: dict[tuple[str, str], RawMorgueFileRecord] = {}

    def save_crawl_error_record(self, record: CrawlErrorRecord) -> None:
        self.crawl_errors.append(record)

    def list_raw_morgue_file_records_for_files(
        self,
        source_files: list[str],
    ) -> dict[str, RawMorgueFileRecord]:
        names = set(source_files)
        return {
            name: record
            for (_, name), record in self.raw_files.items()
            if name in names
        }

    def save_raw_morgue_file(self, record: RawMorgueFileRecord) -> None:
        self.raw_files[(record.player, record.name)] = record


class WorkerBlackBoxTest(unittest.TestCase):
    def test_worker_fetches_only_new_eligible_files_and_records_summary(self) -> None:
        repository = _Repository()
        existing = RawMorgueFileRecord(
            player="WiiWiWi",
            name="morgue-WiiWiWi-20260101-000001.txt",
            url="https://example.test/existing.txt",
            extension="txt",
            text="existing",
            fetched_at="2026-01-01T00:00:00+00:00",
        )
        repository.save_raw_morgue_file(existing)
        fetched_urls: list[str] = []

        with (
            patch("crawl_service.worker.time.sleep"),
            patch(
                "crawl_service.worker.fetch_morgue_users",
                return_value=[
                    MorgueUser(
                        "WiiWiWi",
                        "https://example.test/morgue/WiiWiWi/",
                        "2026-Jan-02 00:00",
                    )
                ],
            ),
            patch(
                "crawl_service.worker.fetch_morgue_files",
                return_value=[
                    MorgueFile("morgue-WiiWiWi-20251231-235959.txt", "https://example.test/old.txt"),
                    MorgueFile(
                        "morgue-WiiWiWi-20260101-000001.txt",
                        "https://example.test/existing.txt",
                    ),
                    MorgueFile("morgue-WiiWiWi-20260102-000001.lst", "https://example.test/new.lst"),
                ],
            ),
            patch(
                "crawl_service.worker.fetch_morgue_file_text",
                side_effect=lambda url, **kwargs: fetched_urls.append(url) or "new raw",
            ),
        ):
            worker = CrawlWorker(repository, base_url="https://example.test/morgue")
            worker.run_once()

        self.assertEqual(fetched_urls, ["https://example.test/new.lst"])
        new_record = repository.raw_files[("WiiWiWi", "morgue-WiiWiWi-20260102-000001.lst")]
        self.assertEqual(new_record.text, "new raw")
        self.assertEqual(new_record.fetch_status, FETCH_STATUS_FETCHED)

    def test_worker_skips_existing_fetched_raw_files(self) -> None:
        repository = _Repository()
        repository.save_raw_morgue_file(
            RawMorgueFileRecord(
                player="WiiWiWi",
                name="morgue-WiiWiWi-20260101-000001.txt",
                url="https://example.test/existing.txt",
                extension="txt",
                text="existing",
                fetched_at="2026-01-01T00:00:00+00:00",
            )
        )
        fetched_urls: list[str] = []

        with (
            patch("crawl_service.worker.time.sleep"),
            patch(
                "crawl_service.worker.fetch_morgue_users",
                return_value=[
                    MorgueUser(
                        "WiiWiWi",
                        "https://example.test/morgue/WiiWiWi/",
                        "2026-Jan-02 00:00",
                    )
                ],
            ),
            patch(
                "crawl_service.worker.fetch_morgue_files",
                return_value=[
                    MorgueFile(
                        "morgue-WiiWiWi-20260101-000001.txt",
                        "https://example.test/existing.txt",
                    )
                ],
            ),
            patch(
                "crawl_service.worker.fetch_morgue_file_text",
                side_effect=lambda url, **kwargs: fetched_urls.append(url) or "raw",
            ),
        ):
            worker = CrawlWorker(repository, base_url="https://example.test/morgue")
            worker.run_once()

        self.assertEqual(fetched_urls, [])

    def test_worker_records_fetch_failures(self) -> None:
        repository = _Repository()

        def fail_fetch(*args, **kwargs):
            raise RuntimeError("network down")

        with (
            patch("crawl_service.worker.time.sleep"),
            patch(
                "crawl_service.worker.fetch_morgue_users",
                return_value=[
                    MorgueUser(
                        "bad",
                        "https://example.test/morgue/bad/",
                        "2026-Jan-02 00:00",
                    )
                ],
            ),
            patch(
                "crawl_service.worker.fetch_morgue_files",
                return_value=[
                    MorgueFile("morgue-bad-20260101-000001.txt", "https://example.test/bad.txt")
                ],
            ),
            patch("crawl_service.worker.fetch_morgue_file_text", side_effect=fail_fetch),
        ):
            worker = CrawlWorker(repository, base_url="https://example.test/morgue")
            worker.run_once()

        self.assertNotIn(("bad", "morgue-bad-20260101-000001.txt"), repository.raw_files)
        self.assertEqual(len(repository.crawl_errors), 1)
        self.assertEqual(repository.crawl_errors[0].player, "bad")
        self.assertEqual(repository.crawl_errors[0].name, "morgue-bad-20260101-000001.txt")
        self.assertEqual(repository.crawl_errors[0].stage, "fetch_file")
        self.assertEqual(repository.crawl_errors[0].message, "network down")

if __name__ == "__main__":
    unittest.main()
