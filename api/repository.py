"""Gallery API MongoDB read repository."""

from __future__ import annotations

import os
from typing import Any, Protocol

from api.models import ArtifactDocument
from api.presenter import present_artifact_document


DEFAULT_MONGO_URI = "mongodb://localhost:27017"
DEFAULT_MONGO_DATABASE = "dcss_arti_gallery"
DEFAULT_MONGO_COLLECTION = "artifacts"


class ArtifactReadRepository(Protocol):
    """Storage operations owned by the Gallery API."""

    def list_artifacts(
        self,
        query: str | None = None,
        item_type: str | None = None,
        player: str | None = None,
    ) -> list[ArtifactDocument]:
        ...

    def get_artifact(self, artifact_id: str) -> ArtifactDocument | None:
        ...

    def list_artifact_types(self) -> list[str]:
        ...


class MongoArtifactReadRepository:
    """MongoDB-backed read repository for the Gallery API."""

    def __init__(self, collection) -> None:
        self.collection = collection
        self._indexes_ensured = False

    def list_artifacts(
        self,
        query: str | None = None,
        item_type: str | None = None,
        player: str | None = None,
    ) -> list[ArtifactDocument]:
        self._ensure_indexes()
        mongo_filter: dict[str, Any] = {}
        if item_type and item_type != "all":
            mongo_filter["item_class"] = item_type
        if player and player.strip():
            mongo_filter["source.player"] = {
                "$regex": f"^{_escape_regex(player.strip().lower())}$",
                "$options": "i",
            }

        documents = [_document_from_mongo(document) for document in self.collection.find(mongo_filter)]
        if query:
            normalized_query = query.strip().lower()
            if normalized_query:
                documents = [
                    artifact
                    for artifact in documents
                    if normalized_query in _search_text(artifact)
                ]
        return sorted(documents, key=lambda artifact: artifact.evaluation.total, reverse=True)

    def get_artifact(self, artifact_id: str) -> ArtifactDocument | None:
        self._ensure_indexes()
        document = self.collection.find_one({"id": artifact_id})
        return _document_from_mongo(document) if document else None

    def list_artifact_types(self) -> list[str]:
        self._ensure_indexes()
        types = sorted(type_name for type_name in self.collection.distinct("item_class") if type_name)
        return ["all", *types]

    def _ensure_indexes(self) -> None:
        if self._indexes_ensured:
            return
        if hasattr(self.collection, "create_index"):
            self.collection.create_index("id", unique=True)
            self.collection.create_index("source.player")
            self.collection.create_index("item_class")
        self._indexes_ensured = True


def repository_from_env() -> MongoArtifactReadRepository:
    """Create the Gallery API MongoDB repository from its environment."""

    return create_mongo_read_repository(
        uri=os.environ.get("MONGODB_URI", DEFAULT_MONGO_URI),
        database=os.environ.get("MONGODB_DATABASE", DEFAULT_MONGO_DATABASE),
        collection=os.environ.get("MONGODB_COLLECTION", DEFAULT_MONGO_COLLECTION),
    )


def create_mongo_read_repository(
    uri: str = DEFAULT_MONGO_URI,
    database: str = DEFAULT_MONGO_DATABASE,
    collection: str = DEFAULT_MONGO_COLLECTION,
    client_factory: Any | None = None,
) -> MongoArtifactReadRepository:
    """Create a MongoDB-backed Gallery API read repository."""

    if client_factory is None:
        from pymongo import MongoClient

        client_factory = MongoClient
    client = client_factory(uri)
    return MongoArtifactReadRepository(client[database][collection])


def _document_from_mongo(document: dict) -> ArtifactDocument:
    return present_artifact_document(document)


def _search_text(artifact: ArtifactDocument) -> str:
    return " ".join(
        [
            artifact.name,
            artifact.baseItem,
            artifact.subtype,
            artifact.origin,
            artifact.allAttributeText,
            artifact.randomAttributeText,
        ]
    ).lower()


def _escape_regex(value: str) -> str:
    import re

    return re.escape(value)
