"""Gallery API MongoDB read repository."""

from __future__ import annotations

import os
import re
from datetime import UTC, datetime, timedelta
from typing import Any, Protocol

from api.display_category import (
    display_category_filter,
    display_category_for_document,
    display_category_sort_key,
)
from api.models import ArtifactDocument
from api.presenter import present_artifact_document


DEFAULT_MONGO_URI = "mongodb://localhost:27018"
DEFAULT_MONGO_DATABASE = "dcss_arti_gallery"
DEFAULT_MONGO_COLLECTION = "artifacts"
DEFAULT_ARTIFACT_LIMIT = 200
MAX_ARTIFACT_LIMIT = 1000
DEFAULT_RECENT_DAYS = 30


class ArtifactReadRepository(Protocol):
    """Storage operations owned by the Gallery API."""

    def list_artifacts(
        self,
        query: str | None = None,
        item_type: str | None = None,
        display_category: str | None = None,
        player: str | None = None,
        since_days: int | None = DEFAULT_RECENT_DAYS,
        limit: int = DEFAULT_ARTIFACT_LIMIT,
        offset: int = 0,
    ) -> list[ArtifactDocument]:
        ...

    def get_artifact(self, artifact_id: str) -> ArtifactDocument | None:
        ...

    def list_artifact_types(self) -> list[str]:
        ...

    def list_display_categories(self) -> dict[str, list[str]]:
        ...


class MongoArtifactReadRepository:
    """MongoDB-backed read repository for the Gallery API."""

    def __init__(self, collection) -> None:
        self.collection = collection

    def list_artifacts(
        self,
        query: str | None = None,
        item_type: str | None = None,
        display_category: str | None = None,
        player: str | None = None,
        since_days: int | None = DEFAULT_RECENT_DAYS,
        limit: int = DEFAULT_ARTIFACT_LIMIT,
        offset: int = 0,
    ) -> list[ArtifactDocument]:
        mongo_filter = _artifact_query_filter(
            query=query,
            item_type=item_type,
            display_category=display_category,
            player=player,
            since_days=since_days,
        )
        bounded_limit = _bounded_limit(limit)
        bounded_offset = max(offset, 0)
        cursor = self.collection.find(mongo_filter)
        cursor = _apply_cursor_options(cursor, limit=bounded_limit, offset=bounded_offset)
        return [_document_from_mongo(document) for document in cursor]

    def get_artifact(self, artifact_id: str) -> ArtifactDocument | None:
        document = self.collection.find_one({"id": artifact_id})
        return _document_from_mongo(document) if document else None

    def list_artifact_types(self) -> list[str]:
        types = sorted(type_name for type_name in self.collection.distinct("item_class") if type_name)
        return ["all", *types]

    def list_display_categories(self) -> dict[str, list[str]]:
        projection = {
            "_id": False,
            "display_category": True,
            "item_class": True,
            "item_subtype": True,
            "base_item": True,
            "weapon_subtype": True,
            "armour_slot": True,
            "jewellery_slot": True,
        }
        categories: dict[str, set[str]] = {}
        for document in self.collection.find({}, projection):
            item_class = str(document.get("item_class") or "").strip()
            category = display_category_for_document(document)
            if item_class and category:
                categories.setdefault(item_class, set()).add(category)
        return {
            item_class: sorted(
                values,
                key=lambda category: display_category_sort_key(item_class, category),
            )
            for item_class, values in sorted(categories.items())
        }


def _artifact_query_filter(
    *,
    query: str | None,
    item_type: str | None,
    display_category: str | None,
    player: str | None,
    since_days: int | None,
) -> dict[str, Any]:
    conditions: list[dict[str, Any]] = []

    if item_type and item_type != "all":
        conditions.append({"item_class": item_type})

    if display_category and display_category.strip() and display_category != "all":
        conditions.append(display_category_filter(display_category))

    if since_days is not None:
        cutoff = datetime.now(UTC) - timedelta(days=max(since_days, 0))
        conditions.append({"latest_game_ended_at": {"$gte": cutoff.isoformat()}})

    if player and player.strip():
        player_filter = player.strip()
        conditions.append(
            {
                "$or": [
                    {"source.player": player_filter},
                    {"sources.player": player_filter},
                ]
            }
        )

    if query and query.strip():
        text_filter = {"$regex": _escape_regex(query.strip()), "$options": "i"}
        conditions.append(
            {
                "$or": [
                    {"name": text_filter},
                    {"base_item": text_filter},
                    {"item_subtype": text_filter},
                    {"random_attributes": text_filter},
                ]
            }
        )

    if not conditions:
        return {}
    if len(conditions) == 1:
        return conditions[0]
    return {"$and": conditions}


def _bounded_limit(limit: int) -> int:
    return min(max(limit, 1), MAX_ARTIFACT_LIMIT)


def _apply_cursor_options(cursor: Any, *, limit: int, offset: int) -> Any:
    if hasattr(cursor, "sort") and hasattr(cursor, "limit"):
        sorted_cursor = cursor.sort("evaluation.total", -1)
        if offset and hasattr(sorted_cursor, "skip"):
            sorted_cursor = sorted_cursor.skip(offset)
        return sorted_cursor.limit(limit)

    documents = sorted(
        list(cursor),
        key=lambda document: int(document.get("evaluation", {}).get("total", 0)),
        reverse=True,
    )
    return documents[offset : offset + limit]


def _escape_regex(value: str) -> str:
    return re.escape(value)


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
