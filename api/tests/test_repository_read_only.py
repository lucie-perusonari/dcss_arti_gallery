from __future__ import annotations

import unittest

from api.repository import MongoArtifactReadRepository


class _ReadOnlyCollection:
    def create_index(self, *_args, **_kwargs) -> None:
        raise AssertionError("Gallery API repository must not create indexes")

    def find(self, _query):
        return []

    def find_one(self, _query):
        return None

    def distinct(self, _field):
        return ["weapon"]


class MongoArtifactReadRepositoryTest(unittest.TestCase):
    def test_repository_does_not_perform_index_ddl_during_reads(self) -> None:
        repository = MongoArtifactReadRepository(_ReadOnlyCollection())

        self.assertEqual(repository.list_artifacts(), [])
        self.assertIsNone(repository.get_artifact("missing-artifact"))
        self.assertEqual(repository.list_artifact_types(), ["all", "weapon"])


if __name__ == "__main__":
    unittest.main()
