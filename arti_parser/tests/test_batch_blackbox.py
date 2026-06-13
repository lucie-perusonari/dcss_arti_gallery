from __future__ import annotations

import unittest

from arti_parser.batch import ArtifactProcessingBatchProcessor
from arti_parser.repository import (
    MongoArtifactProcessingRepository,
    PROCESSING_STATUS_COMPLETED,
    PROCESSING_STATUS_FAILED,
    FETCH_STATUS_FETCHED,
    RawMorgueSource,
)


class _DeleteResult:
    def __init__(self, deleted_count: int) -> None:
        self.deleted_count = deleted_count


class _Cursor(list):
    def sort(self, spec):
        for key, direction in reversed(spec):
            self.sort_in_place(key, reverse=direction < 0)
        return self

    def sort_in_place(self, key: str, reverse: bool) -> None:
        super().sort(key=lambda document: _value_at(document, key), reverse=reverse)

    def batch_size(self, _size: int):
        return self


class _Collection:
    def __init__(self) -> None:
        self.documents: list[dict] = []
        self.indexes: list[tuple[object, dict]] = []
        self.find_queries: list[dict] = []

    def create_index(self, spec, **kwargs) -> None:
        self.indexes.append((spec, kwargs))

    def find(self, query, projection=None):
        self.find_queries.append(dict(query))
        documents = [dict(document) for document in self.documents if _matches(document, query)]
        if projection is not None:
            documents = [_project(document, projection) for document in documents]
        return _Cursor(documents)

    def update_one(self, selector, update, upsert=False) -> None:
        for document in self.documents:
            if _matches(document, selector):
                document.update(update["$set"])
                for key in update.get("$unset", {}):
                    document.pop(key, None)
                return
        if upsert:
            self.documents.append(dict(update["$set"]))

    def bulk_write(self, operations, ordered=False) -> None:
        for operation in operations:
            self.update_one(operation._filter, operation._doc, upsert=operation._upsert)

    def delete_many(self, selector) -> _DeleteResult:
        kept = [document for document in self.documents if not _matches(document, selector)]
        deleted_count = len(self.documents) - len(kept)
        self.documents = kept
        return _DeleteResult(deleted_count)


class ArtifactProcessingBlackBoxTest(unittest.TestCase):
    def test_repository_lists_only_unprocessed_changed_or_failed_raw_files(self) -> None:
        raw_files = _Collection()
        processing = _Collection()
        repository = MongoArtifactProcessingRepository(
            raw_file_collection=raw_files,
            processing_collection=processing,
        )
        raw_files.documents.extend(
            [
                _raw_record("wiiwiwi", "done.txt", "done", "done-hash").to_dict(),
                _raw_record("wiiwiwi", "changed.txt", "changed", "new-hash").to_dict(),
                _raw_record("wiiwiwi", "failed-before.txt", "retry", "retry-hash").to_dict(),
                _raw_record("wiiwiwi", "new.txt", "new", "new-file-hash").to_dict(),
                RawMorgueSource(
                    player="wiiwiwi",
                    name="bad.txt",
                    url="https://example.test/bad.txt",
                    extension="txt",
                    text="",
                    content_hash="",
                    fetch_status="failed",
                    fetch_error="network",
                ).to_dict(),
            ]
        )
        processing.documents.extend(
            [
                _processing_record("wiiwiwi", "done.txt", "done-hash", PROCESSING_STATUS_COMPLETED),
                _processing_record("wiiwiwi", "changed.txt", "old-hash", PROCESSING_STATUS_COMPLETED),
                _processing_record("wiiwiwi", "failed-before.txt", "retry-hash", PROCESSING_STATUS_FAILED),
            ]
        )

        pending = repository.list_pending_raw_files(
            limit=10,
            scan_batch_size=2,
        )

        self.assertEqual(
            [record.name for record in pending],
            ["changed.txt", "failed-before.txt", "new.txt"],
        )

    def test_batch_upserts_artifacts_deletes_stale_and_records_processing_state(self) -> None:
        raw_files = _Collection()
        artifacts = _Collection()
        processing = _Collection()
        repository = MongoArtifactProcessingRepository(
            raw_file_collection=raw_files,
            artifacts_collection=artifacts,
            processing_collection=processing,
        )
        raw = _raw_record(
            "wiiwiwi",
            "morgue-wiiwiwi-20260101-000001.txt",
            "\n".join(
                [
                    "Inventory:",
                    ' a - the +6 broad axe "Axe" {heavy Slay+3 rF+ *Slow}',
                    "   Skills:",
                ]
            ),
            "hash-1",
        )
        raw_files.documents.append(raw.to_dict())
        artifacts.documents.append(
            {
                "id": "stale-artifact",
                "source": {
                    "player": "wiiwiwi",
                    "file": raw.name,
                },
            }
        )

        summary = ArtifactProcessingBatchProcessor(repository).process_batch(limit=10)

        self.assertEqual(summary.raw_files_seen, 1)
        self.assertEqual(summary.raw_files_processed, 1)
        self.assertEqual(summary.artifacts_written, 1)
        self.assertEqual(summary.stale_artifacts_deleted, 1)
        self.assertEqual(len(artifacts.documents), 1)
        artifact = artifacts.documents[0]
        self.assertEqual(artifact["base_item"], "broad axe")
        self.assertEqual(artifact["source"]["player"], "wiiwiwi")
        self.assertEqual(artifact["source_content_hash"], "hash-1")
        self.assertNotIn("parser_version", artifact)
        self.assertNotIn("scoring_version", artifact)
        self.assertEqual(processing.documents[0]["status"], PROCESSING_STATUS_COMPLETED)
        self.assertEqual(processing.documents[0]["artifact_count"], 1)
        self.assertNotIn("parser_version", processing.documents[0])
        self.assertNotIn("scoring_version", processing.documents[0])

        second_summary = ArtifactProcessingBatchProcessor(repository).process_batch(limit=10)

        self.assertEqual(second_summary.raw_files_seen, 0)
        self.assertEqual(len(artifacts.documents), 1)

    def test_batch_merges_same_signature_artifacts_into_canonical_document(self) -> None:
        raw_files = _Collection()
        artifacts = _Collection()
        processing = _Collection()
        repository = MongoArtifactProcessingRepository(
            raw_file_collection=raw_files,
            artifacts_collection=artifacts,
            processing_collection=processing,
        )
        raw_files.documents.extend(
            [
                _raw_record(
                    "wiiwiwi",
                    "morgue-wiiwiwi-20260101-000001.txt",
                    "\n".join(
                        [
                            "Inventory:",
                            ' a - the +6 broad axe "Axe" {heavy Slay+3 rF+ *Slow}',
                            "   Skills:",
                        ]
                    ),
                    "hash-1",
                ).to_dict(),
                _raw_record(
                    "other",
                    "morgue-other-20260102-000001.txt",
                    "\n".join(
                        [
                            "Inventory:",
                            ' a - the +6 broad axe "Axe" {rF+ heavy *Slow Slay+3}',
                            "   Skills:",
                        ]
                    ),
                    "hash-2",
                ).to_dict(),
            ]
        )

        summary = ArtifactProcessingBatchProcessor(repository).process_batch(limit=10)

        self.assertEqual(summary.raw_files_processed, 2)
        self.assertEqual(summary.artifacts_written, 2)
        self.assertEqual(len(artifacts.documents), 1)
        artifact = artifacts.documents[0]
        self.assertEqual(artifact["source_count"], 2)
        self.assertEqual(len(artifact["sources"]), 2)
        self.assertEqual(len(artifact["occurrence_ids"]), 2)
        self.assertEqual({source["player"] for source in artifact["sources"]}, {"wiiwiwi", "other"})
        self.assertNotEqual(artifact["id"], artifact["occurrence_id"])

    def test_batch_records_processing_failure_without_stopping_batch(self) -> None:
        raw_files = _Collection()
        processing = _Collection()
        repository = MongoArtifactProcessingRepository(
            raw_file_collection=raw_files,
            processing_collection=processing,
        )
        raw_files.documents.append(_raw_record("bad", "morgue-bad-20260101-000001.html", "", "hash").to_dict())

        summary = ArtifactProcessingBatchProcessor(repository).process_batch(limit=10)

        self.assertEqual(summary.raw_files_seen, 1)
        self.assertEqual(summary.raw_files_failed, 1)
        self.assertEqual(processing.documents[0]["status"], PROCESSING_STATUS_FAILED)
        self.assertIn("unsupported morgue raw extension", processing.documents[0]["error"])

    def test_stale_source_lookup_is_limited_to_current_raw_file(self) -> None:
        raw_files = _Collection()
        artifacts = _Collection()
        processing = _Collection()
        repository = MongoArtifactProcessingRepository(
            raw_file_collection=raw_files,
            artifacts_collection=artifacts,
            processing_collection=processing,
        )
        raw = _raw_record(
            "wiiwiwi",
            "morgue-wiiwiwi-20260101-000001.txt",
            "\n".join(
                [
                    "Inventory:",
                    ' a - the +6 broad axe "Axe" {heavy Slay+3 rF+ *Slow}',
                    "   Skills:",
                ]
            ),
            "hash-1",
        )
        raw_files.documents.append(raw.to_dict())
        artifacts.documents.extend(
            [
                {
                    "id": "stale-current-source",
                    "source": {"player": "wiiwiwi", "file": raw.name},
                },
                {
                    "id": "other-source",
                    "source": {"player": "other", "file": "morgue-other-20260101-000001.txt"},
                },
            ]
        )

        ArtifactProcessingBatchProcessor(repository).process_batch(limit=10)

        self.assertIn(
            {
                "$or": [
                    {"sources": {"$elemMatch": {"player": "wiiwiwi", "file": raw.name}}},
                    {"source.player": "wiiwiwi", "source.file": raw.name},
                ]
            },
            artifacts.find_queries,
        )
        self.assertTrue(any(document["id"] == "other-source" for document in artifacts.documents))


def _raw_record(
    player: str,
    name: str,
    text: str,
    content_hash: str,
) -> RawMorgueSource:
    return RawMorgueSource(
        player=player,
        name=name,
        url=f"https://example.test/{name}",
        extension=name.rsplit(".", 1)[-1],
        text=text,
        content_hash=content_hash,
        fetch_status=FETCH_STATUS_FETCHED,
        fetched_at="2026-01-01T00:00:00+00:00",
    )


def _processing_record(
    player: str,
    name: str,
    content_hash: str,
    status: str,
) -> dict:
    return {
        "player": player,
        "name": name,
        "content_hash": content_hash,
        "status": status,
        "artifact_count": 1,
    }


def _matches(document: dict, selector: dict) -> bool:
    for key, expected in selector.items():
        if key == "$or":
            if not any(_matches(document, candidate) for candidate in expected):
                return False
            continue
        actual = _value_at(document, key)
        if isinstance(expected, dict):
            if "$elemMatch" in expected:
                if not isinstance(actual, list):
                    return False
                if not any(_matches(item, expected["$elemMatch"]) for item in actual):
                    return False
                continue
            if "$in" in expected and actual not in expected["$in"]:
                return False
            if "$nin" in expected and actual in expected["$nin"]:
                return False
            continue
        if actual != expected:
            return False
    return True


def _project(document: dict, projection: dict) -> dict:
    if not any(value for value in projection.values()):
        return dict(document)
    projected: dict = {}
    for key, enabled in projection.items():
        if enabled and key in document:
            projected[key] = document[key]
    return projected


def _value_at(document: dict, dotted_key: str):
    value = document
    for part in dotted_key.split("."):
        if not isinstance(value, dict):
            return None
        value = value.get(part)
    return value


if __name__ == "__main__":
    unittest.main()
