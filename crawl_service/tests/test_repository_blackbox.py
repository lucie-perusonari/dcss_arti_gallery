from __future__ import annotations

import unittest

from crawl_service.repository import (
    CrawlUserRecord,
    FETCH_STATUS_FETCHED,
    MongoCrawlRepository,
    RawMorgueFileRecord,
    raw_text_hash,
)


class _Cursor(list):
    pass


class _Collection:
    def __init__(self) -> None:
        self.documents: list[dict] = []
        self.indexes: list[tuple[object, dict]] = []

    def create_index(self, spec, **kwargs) -> None:
        self.indexes.append((spec, kwargs))

    def update_one(self, selector, update, upsert=False) -> None:
        for document in self.documents:
            if _matches(document, selector):
                document.update(update["$set"])
                return
        if upsert:
            self.documents.append(dict(update["$set"]))

    def find(self, query):
        return _Cursor([dict(document) for document in self.documents if _matches(document, query)])


class RepositoryBlackBoxTest(unittest.TestCase):
    def test_repository_upserts_raw_files_and_returns_duplicate_check_records(self) -> None:
        raw_files = _Collection()
        repository = MongoCrawlRepository(raw_file_collection=raw_files)
        first = RawMorgueFileRecord.fetched(
            player="WiiWiWi",
            name="morgue-wiiwiwi-20260101-000001.txt",
            url="https://example.test/old.txt",
            extension="txt",
            text="old raw",
            fetched_at="2026-01-01T00:00:00+00:00",
        )
        second = RawMorgueFileRecord.fetched(
            player="wiiwiwi",
            name="morgue-wiiwiwi-20260101-000001.txt",
            url="https://example.test/new.txt",
            extension="txt",
            text="new raw",
            fetched_at="2026-01-01T00:00:01+00:00",
        )

        repository.save_raw_morgue_file(first)
        repository.save_raw_morgue_file(second)
        records = repository.list_raw_morgue_file_records_for_player_files(
            "WIIWIWI",
            ["morgue-wiiwiwi-20260101-000001.txt", "missing.txt"],
        )

        self.assertEqual(len(raw_files.documents), 1)
        self.assertEqual(list(records), ["morgue-wiiwiwi-20260101-000001.txt"])
        record = records["morgue-wiiwiwi-20260101-000001.txt"]
        self.assertEqual(record.text, "new raw")
        self.assertEqual(record.content_hash, raw_text_hash("new raw"))
        self.assertEqual(record.fetch_status, FETCH_STATUS_FETCHED)

    def test_repository_returns_user_records_needed_for_modified_at_skip(self) -> None:
        crawl_users = _Collection()
        repository = MongoCrawlRepository(crawl_user_collection=crawl_users)

        repository.save_crawl_user_record(
            CrawlUserRecord(
                player="WiiWiWi",
                url="https://example.test/morgue/wiiwiwi/",
                observed_at="2026-Jan-02 00:00",
                status="completed",
                stored_files=2,
            )
        )
        records = repository.list_crawl_user_records(["wiiwiwi", "missing"])

        self.assertEqual(list(records), ["wiiwiwi"])
        self.assertEqual(records["wiiwiwi"].stored_files, 2)


def _matches(document: dict, selector: dict) -> bool:
    for key, expected in selector.items():
        actual = document.get(key)
        if isinstance(expected, dict) and "$in" in expected:
            if actual not in expected["$in"]:
                return False
            continue
        if actual != expected:
            return False
    return True


if __name__ == "__main__":
    unittest.main()
