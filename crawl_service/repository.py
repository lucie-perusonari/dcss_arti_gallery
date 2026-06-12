"""Crawl service MongoDB writer/cache repository."""

from __future__ import annotations

import hashlib
import os
import re
from dataclasses import dataclass
from typing import Any, Protocol

from crawl_service.domain.documents.builder import ArtifactDocument


DEFAULT_MONGO_URI = "mongodb://localhost:27017"
DEFAULT_MONGO_DATABASE = "dcss_arti_gallery"
DEFAULT_MONGO_COLLECTION = "artifacts"
DEFAULT_MONGO_CRAWL_FILES_COLLECTION = "crawl_files"
DEFAULT_MONGO_CRAWL_USERS_COLLECTION = "crawl_users"
DEFAULT_MONGO_RAW_FILES_COLLECTION = "raw_morgue_files"

FETCH_STATUS_FETCHED = "fetched"
FETCH_STATUS_FAILED = "failed"
PROCESS_STATUS_PENDING = "pending"
PROCESS_STATUS_PROCESSED = "processed"
PROCESS_STATUS_FAILED = "failed"


@dataclass(frozen=True)
class CrawlFileRecord:
    """Persistent processing state for one remote morgue file."""

    player: str
    name: str
    url: str
    status: str
    artifact_count: int = 0
    processed_at: str | None = None
    error: str | None = None

    def to_dict(self) -> dict:
        return {
            "player": self.player,
            "name": self.name,
            "url": self.url,
            "status": self.status,
            "artifact_count": self.artifact_count,
            "processed_at": self.processed_at,
            "error": self.error,
        }


@dataclass(frozen=True)
class CrawlUserRecord:
    """Persistent scan state for one remote morgue user directory."""

    player: str
    url: str
    observed_at: str
    status: str
    scanned_at: str | None = None
    processed_files: int = 0
    artifact_count: int = 0
    error: str | None = None

    def to_dict(self) -> dict:
        return {
            "player": self.player,
            "url": self.url,
            "observed_at": self.observed_at,
            "status": self.status,
            "scanned_at": self.scanned_at,
            "processed_files": self.processed_files,
            "artifact_count": self.artifact_count,
            "error": self.error,
        }


@dataclass(frozen=True)
class RawMorgueFileRecord:
    """Fetched morgue source text and independent processing state."""

    player: str
    name: str
    url: str
    extension: str
    text: str
    content_hash: str
    fetch_status: str
    process_status: str
    fetched_at: str | None = None
    processed_at: str | None = None
    artifact_count: int = 0
    fetch_error: str | None = None
    process_error: str | None = None
    parser_version: str | None = None
    scoring_version: str | None = None

    @classmethod
    def fetched(
        cls,
        *,
        player: str,
        name: str,
        url: str,
        extension: str,
        text: str,
        fetched_at: str,
    ) -> "RawMorgueFileRecord":
        return cls(
            player=player,
            name=name,
            url=url,
            extension=extension,
            text=text,
            content_hash=raw_text_hash(text),
            fetch_status=FETCH_STATUS_FETCHED,
            process_status=PROCESS_STATUS_PENDING,
            fetched_at=fetched_at,
            fetch_error=None,
            process_error=None,
        )

    @classmethod
    def fetch_failed(
        cls,
        *,
        player: str,
        name: str,
        url: str,
        extension: str,
        error: str,
    ) -> "RawMorgueFileRecord":
        return cls(
            player=player,
            name=name,
            url=url,
            extension=extension,
            text="",
            content_hash="",
            fetch_status=FETCH_STATUS_FAILED,
            process_status=PROCESS_STATUS_PENDING,
            fetch_error=error,
        )

    def to_dict(self) -> dict:
        return {
            "player": self.player,
            "name": self.name,
            "url": self.url,
            "extension": self.extension,
            "text": self.text,
            "content_hash": self.content_hash,
            "fetch_status": self.fetch_status,
            "process_status": self.process_status,
            "fetched_at": self.fetched_at,
            "processed_at": self.processed_at,
            "artifact_count": self.artifact_count,
            "fetch_error": self.fetch_error,
            "process_error": self.process_error,
            "parser_version": self.parser_version,
            "scoring_version": self.scoring_version,
        }


class CrawlIngestRepository(Protocol):
    """Storage operations required by the raw morgue ingest worker."""

    def get_crawl_file_record(
        self,
        player: str,
        source_file: str,
    ) -> CrawlFileRecord | None:
        ...

    def save_crawl_file_record(self, record: CrawlFileRecord) -> None:
        ...

    def get_crawl_user_record(self, player: str) -> CrawlUserRecord | None:
        ...

    def list_crawl_user_records(
        self,
        players: list[str],
    ) -> dict[str, CrawlUserRecord]:
        ...

    def save_crawl_user_record(self, record: CrawlUserRecord) -> None:
        ...

    def get_raw_morgue_file(self, player: str, source_file: str) -> RawMorgueFileRecord | None:
        ...

    def list_raw_morgue_file_records_for_players(
        self,
        players: list[str],
    ) -> dict[tuple[str, str], RawMorgueFileRecord]:
        ...

    def list_raw_morgue_file_records_for_player_files(
        self,
        player: str,
        source_files: list[str],
    ) -> dict[str, RawMorgueFileRecord]:
        ...

    def save_raw_morgue_file(self, record: RawMorgueFileRecord) -> None:
        ...


class CrawlArtifactRepository(CrawlIngestRepository, Protocol):
    """Storage operations required by raw processing and artifact writes."""

    def replace_artifacts_for_source(
        self,
        player: str,
        source_file: str,
        artifacts: list[ArtifactDocument],
    ) -> None:
        ...

    def list_raw_morgue_files_for_processing(
        self,
        *,
        parser_version: str,
        scoring_version: str,
        limit: int,
    ) -> list[RawMorgueFileRecord]:
        ...


class MongoCrawlArtifactRepository:
    """MongoDB-backed writer/cache repository for crawl_service."""

    def __init__(
        self,
        collection,
        crawl_file_collection=None,
        crawl_user_collection=None,
        raw_file_collection=None,
    ) -> None:
        self.collection = collection
        self.crawl_file_collection = crawl_file_collection
        self.crawl_user_collection = crawl_user_collection
        self.raw_file_collection = raw_file_collection
        self._indexes_ensured = False

    def replace_artifacts_for_source(
        self,
        player: str,
        source_file: str,
        artifacts: list[ArtifactDocument],
    ) -> None:
        self._ensure_indexes()
        self.collection.delete_many(
            {
                "source.player": {
                    "$regex": f"^{re.escape(_player_key(player))}$",
                    "$options": "i",
                },
                "source.file": source_file,
            }
        )
        if artifacts:
            self.collection.insert_many([artifact.model_dump() for artifact in artifacts])

    def get_crawl_file_record(
        self,
        player: str,
        source_file: str,
    ) -> CrawlFileRecord | None:
        self._ensure_indexes()
        if self.crawl_file_collection is None:
            return None
        document = self.crawl_file_collection.find_one(
            {"player": _player_key(player), "name": source_file}
        )
        return _crawl_file_record_from_mongo(document) if document else None

    def save_crawl_file_record(self, record: CrawlFileRecord) -> None:
        self._ensure_indexes()
        if self.crawl_file_collection is None:
            return
        document = record.to_dict()
        document["player"] = _player_key(document["player"])
        self.crawl_file_collection.update_one(
            {"player": document["player"], "name": document["name"]},
            {"$set": document},
            upsert=True,
        )

    def get_crawl_user_record(self, player: str) -> CrawlUserRecord | None:
        self._ensure_indexes()
        if self.crawl_user_collection is None:
            return None
        document = self.crawl_user_collection.find_one({"player": _player_key(player)})
        return _crawl_user_record_from_mongo(document) if document else None

    def list_crawl_user_records(
        self,
        players: list[str],
    ) -> dict[str, CrawlUserRecord]:
        self._ensure_indexes()
        if self.crawl_user_collection is None:
            return {}
        player_keys = _player_keys(players)
        if not player_keys:
            return {}
        documents = self.crawl_user_collection.find({"player": {"$in": player_keys}})
        records = [_crawl_user_record_from_mongo(document) for document in documents]
        return {_player_key(record.player): record for record in records}

    def save_crawl_user_record(self, record: CrawlUserRecord) -> None:
        self._ensure_indexes()
        if self.crawl_user_collection is None:
            return
        document = record.to_dict()
        document["player"] = _player_key(document["player"])
        self.crawl_user_collection.update_one(
            {"player": document["player"]},
            {"$set": document},
            upsert=True,
        )

    def get_raw_morgue_file(
        self,
        player: str,
        source_file: str,
    ) -> RawMorgueFileRecord | None:
        self._ensure_indexes()
        if self.raw_file_collection is None:
            return None
        document = self.raw_file_collection.find_one(
            {"player": _player_key(player), "name": source_file}
        )
        return _raw_morgue_file_record_from_mongo(document) if document else None

    def list_raw_morgue_file_records_for_players(
        self,
        players: list[str],
    ) -> dict[tuple[str, str], RawMorgueFileRecord]:
        self._ensure_indexes()
        if self.raw_file_collection is None:
            return {}
        player_keys = _player_keys(players)
        if not player_keys:
            return {}
        documents = self.raw_file_collection.find({"player": {"$in": player_keys}})
        records = [_raw_morgue_file_record_from_mongo(document) for document in documents]
        return {(_player_key(record.player), record.name): record for record in records}

    def list_raw_morgue_file_records_for_player_files(
        self,
        player: str,
        source_files: list[str],
    ) -> dict[str, RawMorgueFileRecord]:
        self._ensure_indexes()
        if self.raw_file_collection is None:
            return {}
        file_names = sorted({source_file for source_file in source_files if source_file})
        if not file_names:
            return {}
        documents = self.raw_file_collection.find(
            {
                "player": _player_key(player),
                "name": {"$in": file_names},
            }
        )
        records = [_raw_morgue_file_record_from_mongo(document) for document in documents]
        return {record.name: record for record in records}

    def save_raw_morgue_file(self, record: RawMorgueFileRecord) -> None:
        self._ensure_indexes()
        if self.raw_file_collection is None:
            return
        document = record.to_dict()
        document["player"] = _player_key(document["player"])
        self.raw_file_collection.update_one(
            {"player": document["player"], "name": document["name"]},
            {"$set": document},
            upsert=True,
        )

    def list_raw_morgue_files_for_processing(
        self,
        *,
        parser_version: str,
        scoring_version: str,
        limit: int,
    ) -> list[RawMorgueFileRecord]:
        self._ensure_indexes()
        if self.raw_file_collection is None or limit <= 0:
            return []
        query = {
            "fetch_status": FETCH_STATUS_FETCHED,
            "$or": [
                {"process_status": {"$in": [PROCESS_STATUS_PENDING, PROCESS_STATUS_FAILED]}},
                {"parser_version": {"$ne": parser_version}},
                {"scoring_version": {"$ne": scoring_version}},
            ],
        }
        documents = self.raw_file_collection.find(query).limit(limit)
        return [_raw_morgue_file_record_from_mongo(document) for document in documents]

    def _ensure_indexes(self) -> None:
        if self._indexes_ensured:
            return
        if hasattr(self.collection, "create_index"):
            self.collection.create_index("id", unique=True)
            self.collection.create_index("source.file")
            self.collection.create_index("source.player")
        if self.crawl_file_collection is not None and hasattr(
            self.crawl_file_collection,
            "create_index",
        ):
            self.crawl_file_collection.create_index(
                [("player", 1), ("name", 1)],
                unique=True,
            )
        if self.crawl_user_collection is not None and hasattr(
            self.crawl_user_collection,
            "create_index",
        ):
            self.crawl_user_collection.create_index("player", unique=True)
            self.crawl_user_collection.create_index("observed_at")
        if self.raw_file_collection is not None and hasattr(
            self.raw_file_collection,
            "create_index",
        ):
            self.raw_file_collection.create_index(
                [("player", 1), ("name", 1)],
                unique=True,
            )
            self.raw_file_collection.create_index("content_hash")
            self.raw_file_collection.create_index("fetch_status")
            self.raw_file_collection.create_index("process_status")
        self._indexes_ensured = True


def repository_from_env() -> MongoCrawlArtifactRepository:
    """Create the crawl service MongoDB repository from its environment."""

    return create_mongo_crawl_repository(
        uri=os.environ.get("MONGODB_URI", DEFAULT_MONGO_URI),
        database=os.environ.get("MONGODB_DATABASE", DEFAULT_MONGO_DATABASE),
        collection=os.environ.get("MONGODB_COLLECTION", DEFAULT_MONGO_COLLECTION),
        crawl_files_collection=os.environ.get(
            "MONGODB_CRAWL_FILES_COLLECTION",
            DEFAULT_MONGO_CRAWL_FILES_COLLECTION,
        ),
        crawl_users_collection=os.environ.get(
            "MONGODB_CRAWL_USERS_COLLECTION",
            DEFAULT_MONGO_CRAWL_USERS_COLLECTION,
        ),
        raw_files_collection=os.environ.get(
            "MONGODB_RAW_FILES_COLLECTION",
            DEFAULT_MONGO_RAW_FILES_COLLECTION,
        ),
    )


def create_mongo_crawl_repository(
    uri: str = DEFAULT_MONGO_URI,
    database: str = DEFAULT_MONGO_DATABASE,
    collection: str = DEFAULT_MONGO_COLLECTION,
    crawl_files_collection: str = DEFAULT_MONGO_CRAWL_FILES_COLLECTION,
    crawl_users_collection: str = DEFAULT_MONGO_CRAWL_USERS_COLLECTION,
    raw_files_collection: str = DEFAULT_MONGO_RAW_FILES_COLLECTION,
    client_factory: Any | None = None,
) -> MongoCrawlArtifactRepository:
    """Create a MongoDB-backed crawl repository."""

    if client_factory is None:
        from pymongo import MongoClient

        client_factory = MongoClient
    client = client_factory(uri)
    database_handle = client[database]
    return MongoCrawlArtifactRepository(
        database_handle[collection],
        database_handle[crawl_files_collection],
        database_handle[crawl_users_collection],
        database_handle[raw_files_collection],
    )


def _crawl_file_record_from_mongo(document: dict) -> CrawlFileRecord:
    document = dict(document)
    document.pop("_id", None)
    return CrawlFileRecord(
        player=document["player"],
        name=document["name"],
        url=document.get("url", ""),
        status=document["status"],
        artifact_count=int(document.get("artifact_count", 0)),
        processed_at=document.get("processed_at"),
        error=document.get("error"),
    )


def _crawl_user_record_from_mongo(document: dict) -> CrawlUserRecord:
    document = dict(document)
    document.pop("_id", None)
    return CrawlUserRecord(
        player=document["player"],
        url=document.get("url", ""),
        observed_at=document["observed_at"],
        status=document["status"],
        scanned_at=document.get("scanned_at"),
        processed_files=int(document.get("processed_files", 0)),
        artifact_count=int(document.get("artifact_count", 0)),
        error=document.get("error"),
    )


def _raw_morgue_file_record_from_mongo(document: dict) -> RawMorgueFileRecord:
    document = dict(document)
    document.pop("_id", None)
    return RawMorgueFileRecord(
        player=document["player"],
        name=document["name"],
        url=document.get("url", ""),
        extension=document.get("extension", ""),
        text=document.get("text", ""),
        content_hash=document.get("content_hash", ""),
        fetch_status=document.get("fetch_status", ""),
        process_status=document.get("process_status", PROCESS_STATUS_PENDING),
        fetched_at=document.get("fetched_at"),
        processed_at=document.get("processed_at"),
        artifact_count=int(document.get("artifact_count", 0)),
        fetch_error=document.get("fetch_error"),
        process_error=document.get("process_error"),
        parser_version=document.get("parser_version"),
        scoring_version=document.get("scoring_version"),
    )


def _player_key(player: str) -> str:
    return player.strip().lower()


def _player_keys(players: list[str]) -> list[str]:
    return sorted({_player_key(player) for player in players if player.strip()})


def raw_text_hash(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()
