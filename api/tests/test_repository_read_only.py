from __future__ import annotations

import unittest

from api.repository import MongoArtifactReadRepository


class _ReadOnlyCollection:
    def __init__(self) -> None:
        self.find_queries: list[dict] = []

    def create_index(self, *_args, **_kwargs) -> None:
        raise AssertionError("Gallery API repository must not create indexes")

    def find(self, query):
        self.find_queries.append(query)
        return []

    def find_one(self, _query):
        return None

    def distinct(self, _field):
        return ["weapon"]


class MongoArtifactReadRepositoryTest(unittest.TestCase):
    def test_repository_does_not_perform_index_ddl_during_reads(self) -> None:
        collection = _ReadOnlyCollection()
        repository = MongoArtifactReadRepository(collection)

        self.assertEqual(repository.list_artifacts(), [])
        self.assertIsNone(repository.get_artifact("missing-artifact"))
        self.assertEqual(repository.list_artifact_types(), ["all", "weapon"])

    def test_player_filter_reads_representative_and_evidence_sources(self) -> None:
        collection = _ReadOnlyCollection()
        repository = MongoArtifactReadRepository(collection)

        repository.list_artifacts(player="WiiWiwi", since_days=None)

        self.assertEqual(
            collection.find_queries[0],
            {
                "$or": [
                    {"source.player": {"$regex": "^wiiwiwi$", "$options": "i"}},
                    {"sources.player": {"$regex": "^wiiwiwi$", "$options": "i"}},
                ]
            },
        )


if __name__ == "__main__":
    unittest.main()
