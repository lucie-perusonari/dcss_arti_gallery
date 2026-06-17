from __future__ import annotations

import unittest

from crawl_service.repository import (
    CrawlErrorRecord,
    DEFAULT_MONGO_CRAWL_ERRORS_COLLECTION,
    DEFAULT_MONGO_RAW_FILES_COLLECTION,
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

    def replace_one(self, selector, replacement, upsert=False) -> None:
        for existing in self.documents:
            if _matches(existing, selector):
                existing.clear()
                existing.update(replacement)
                return
        if upsert:
            self.documents.append(dict(replacement))

    def insert_one(self, document) -> None:
        self.documents.append(dict(document))

    def find(self, query):
        return _Cursor([dict(document) for document in self.documents if _matches(document, query)])


class _Database(dict):
    def __getitem__(self, name):
        if name not in self:
            self[name] = _Collection()
        return super().__getitem__(name)


class RepositoryBlackBoxTest(unittest.TestCase):
    def test_repository_replaces_raw_files_and_returns_duplicate_check_records(self) -> None:
        database = _Database()
        raw_files = database[DEFAULT_MONGO_RAW_FILES_COLLECTION]
        repository = MongoCrawlRepository(database)
        first = RawMorgueFileRecord(
            player="WiiWiWi",
            name="morgue-WiiWiWi-20260101-000001.txt",
            url="https://example.test/old.txt",
            extension="txt",
            text="old raw",
            fetched_at="2026-01-01T00:00:00+00:00",
        )
        second = RawMorgueFileRecord(
            player="WiiWiWi",
            name="morgue-WiiWiWi-20260101-000001.txt",
            url="https://example.test/new.txt",
            extension="txt",
            text="new raw",
            fetched_at="2026-01-01T00:00:01+00:00",
        )

        repository.save_raw_morgue_file(first)
        repository.save_raw_morgue_file(second)
        records = repository.list_raw_morgue_file_records_for_files(
            ["morgue-WiiWiWi-20260101-000001.txt", "missing.txt"]
        )

        self.assertEqual(len(raw_files.documents), 1)
        self.assertEqual(list(records), ["morgue-WiiWiWi-20260101-000001.txt"])
        record = records["morgue-WiiWiWi-20260101-000001.txt"]
        self.assertEqual(record.text, "new raw")
        self.assertEqual(record.content_hash, raw_text_hash("new raw"))
        self.assertEqual(record.fetch_status, FETCH_STATUS_FETCHED)

    def test_repository_appends_crawl_errors(self) -> None:
        database = _Database()
        crawl_errors = database[DEFAULT_MONGO_CRAWL_ERRORS_COLLECTION]
        repository = MongoCrawlRepository(database)

        repository.save_crawl_error_record(
            CrawlErrorRecord(
                player="bad",
                name="morgue-bad-20260101-000001.txt",
                url="https://example.test/bad.txt",
                extension="txt",
                stage="fetch_file",
                message="network down",
                error_type="RuntimeError",
                user_url="https://example.test/morgue/bad/",
                occurred_at="2026-01-01T00:00:00+00:00",
            )
        )

        self.assertEqual(len(crawl_errors.documents), 1)
        self.assertEqual(crawl_errors.documents[0]["stage"], "fetch_file")
        self.assertEqual(crawl_errors.documents[0]["message"], "network down")

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
