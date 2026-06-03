from __future__ import annotations

import unittest

from crawl_service.repository import (
    FETCH_STATUS_FETCHED,
    PROCESS_STATUS_PENDING,
    PROCESS_STATUS_PROCESSED,
    MongoCrawlArtifactRepository,
    RawMorgueFileRecord,
    raw_text_hash,
)


class FakeCursor(list):
    def limit(self, limit: int):
        return FakeCursor(self[:limit])


class FakeCollection:
    def __init__(self) -> None:
        self.documents: list[dict] = []
        self.indexes = []

    def create_index(self, spec, **kwargs) -> None:
        self.indexes.append((spec, kwargs))

    def update_one(self, selector, update, upsert=False) -> None:
        for document in self.documents:
            if _matches_selector(document, selector):
                document.update(update["$set"])
                return
        if upsert:
            self.documents.append(dict(update["$set"]))

    def find_one(self, selector):
        for document in self.documents:
            if _matches_selector(document, selector):
                return dict(document)
        return None

    def find(self, query):
        return FakeCursor([dict(document) for document in self.documents if _matches_query(document, query)])


class MongoCrawlArtifactRepositoryTest(unittest.TestCase):
    def test_raw_morgue_files_are_saved_and_queried_for_processing(self) -> None:
        raw_collection = FakeCollection()
        repository = MongoCrawlArtifactRepository(
            FakeCollection(),
            raw_file_collection=raw_collection,
        )
        repository.save_raw_morgue_file(
            RawMorgueFileRecord.fetched(
                player="WiiWiWi",
                name="morgue-wiiwiwi-20260101-000001.txt",
                url="https://example.test/new.txt",
                extension="txt",
                text="raw text",
                fetched_at="2026-01-01T00:00:00+00:00",
            )
        )
        repository.save_raw_morgue_file(
            RawMorgueFileRecord.fetched(
                player="WiiWiWi",
                name="morgue-wiiwiwi-20260101-000001.lst",
                url="https://example.test/new.lst",
                extension="lst",
                text="raw lst text",
                fetched_at="2026-01-01T00:00:01+00:00",
            )
        )
        repository.save_raw_morgue_file(
            RawMorgueFileRecord.fetched(
                player="WiiWiWi",
                name="morgue-wiiwiwi-20260101-000001.lst",
                url="https://example.test/new.lst",
                extension="lst",
                text="updated raw lst text",
                fetched_at="2026-01-01T00:00:02+00:00",
            )
        )
        repository.save_raw_morgue_file(
            RawMorgueFileRecord(
                player="other",
                name="morgue-other-20260101-000001.txt",
                url="https://example.test/other.txt",
                extension="txt",
                text="other raw text",
                content_hash=raw_text_hash("other raw text"),
                fetch_status=FETCH_STATUS_FETCHED,
                process_status=PROCESS_STATUS_PROCESSED,
                parser_version="current-parser",
                scoring_version="old-scoring",
            )
        )
        repository.save_raw_morgue_file(
            RawMorgueFileRecord(
                player="done",
                name="morgue-done-20260101-000001.txt",
                url="https://example.test/done.txt",
                extension="txt",
                text="done raw text",
                content_hash=raw_text_hash("done raw text"),
                fetch_status=FETCH_STATUS_FETCHED,
                process_status=PROCESS_STATUS_PROCESSED,
                parser_version="current-parser",
                scoring_version="current-scoring",
            )
        )

        raw_file = repository.get_raw_morgue_file("wiiwiwi", "morgue-wiiwiwi-20260101-000001.txt")
        lst_file = repository.get_raw_morgue_file("wiiwiwi", "morgue-wiiwiwi-20260101-000001.lst")
        processable = repository.list_raw_morgue_files_for_processing(
            parser_version="current-parser",
            scoring_version="current-scoring",
            limit=10,
        )

        self.assertIsNotNone(raw_file)
        assert raw_file is not None
        self.assertEqual(raw_file.player, "wiiwiwi")
        self.assertEqual(raw_file.content_hash, raw_text_hash("raw text"))
        self.assertEqual(raw_file.process_status, PROCESS_STATUS_PENDING)
        self.assertIsNotNone(lst_file)
        assert lst_file is not None
        self.assertEqual(lst_file.extension, "lst")
        self.assertEqual(lst_file.text, "updated raw lst text")
        self.assertEqual(lst_file.content_hash, raw_text_hash("updated raw lst text"))
        self.assertEqual(len(raw_collection.documents), 4)
        self.assertEqual(
            [record.name for record in processable],
            [
                "morgue-wiiwiwi-20260101-000001.txt",
                "morgue-wiiwiwi-20260101-000001.lst",
                "morgue-other-20260101-000001.txt",
            ],
        )


def _matches_selector(document: dict, selector: dict) -> bool:
    return all(document.get(key) == value for key, value in selector.items())


def _matches_query(document: dict, query: dict) -> bool:
    if document.get("fetch_status") != query["fetch_status"]:
        return False
    return any(_matches_condition(document, condition) for condition in query["$or"])


def _matches_condition(document: dict, condition: dict) -> bool:
    key, expected = next(iter(condition.items()))
    if isinstance(expected, dict) and "$in" in expected:
        return document.get(key) in expected["$in"]
    if isinstance(expected, dict) and "$ne" in expected:
        return document.get(key) != expected["$ne"]
    return document.get(key) == expected


if __name__ == "__main__":
    unittest.main()
