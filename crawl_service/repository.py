"""Crawl service MongoDB repository for morgue ingest state."""

from __future__ import annotations

import hashlib
import os
from dataclasses import dataclass
from typing import Any, Protocol


DEFAULT_MONGO_URI = "mongodb://localhost:27018"
DEFAULT_MONGO_DATABASE = "dcss_arti_gallery_dev"
DEFAULT_MONGO_CRAWL_FILES_COLLECTION = "crawl_files"
DEFAULT_MONGO_CRAWL_USERS_COLLECTION = "crawl_users"
DEFAULT_MONGO_RAW_FILES_COLLECTION = "raw_morgue_files"

FETCH_STATUS_FETCHED = "fetched"
FETCH_STATUS_FAILED = "failed"


@dataclass(frozen=True)
class CrawlFileRecord:
    """Persistent ingest state for one remote morgue file."""

    player: str
    name: str
    url: str
    status: str
    fetched_at: str | None = None
    error: str | None = None

    def to_dict(self) -> dict:
        return {
            "player": self.player,
            "name": self.name,
            "url": self.url,
            "status": self.status,
            "fetched_at": self.fetched_at,
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
    stored_files: int = 0
    error: str | None = None

    def to_dict(self) -> dict:
        return {
            "player": self.player,
            "url": self.url,
            "observed_at": self.observed_at,
            "status": self.status,
            "scanned_at": self.scanned_at,
            "stored_files": self.stored_files,
            "error": self.error,
        }


@dataclass(frozen=True)
class RawMorgueFileRecord:
    """Fetched morgue source text."""

    player: str
    name: str
    url: str
    extension: str
    text: str
    content_hash: str
    fetch_status: str
    fetched_at: str | None = None
    fetch_error: str | None = None

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
            fetched_at=fetched_at,
            fetch_error=None,
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
            "fetched_at": self.fetched_at,
            "fetch_error": self.fetch_error,
        }


class CrawlIngestRepository(Protocol):
    """Storage operations required by the raw morgue ingest worker."""

    def save_crawl_file_record(self, record: CrawlFileRecord) -> None:
        ...

    def list_crawl_user_records(
        self,
        players: list[str],
    ) -> dict[str, CrawlUserRecord]:
        ...

    def save_crawl_user_record(self, record: CrawlUserRecord) -> None:
        ...

    def list_raw_morgue_file_records_for_player_files(
        self,
        player: str,
        source_files: list[str],
    ) -> dict[str, RawMorgueFileRecord]:
        ...

    def save_raw_morgue_file(self, record: RawMorgueFileRecord) -> None:
        ...


class MongoCrawlRepository:
    """MongoDB-backed repository for crawl_service morgue ingest state."""

    def __init__(
        self,
        crawl_file_collection=None,
        crawl_user_collection=None,
        raw_file_collection=None,
    ) -> None:
        self.crawl_file_collection = crawl_file_collection
        self.crawl_user_collection = crawl_user_collection
        self.raw_file_collection = raw_file_collection

    def save_crawl_file_record(self, record: CrawlFileRecord) -> None:
        if self.crawl_file_collection is None:
            return
        document = record.to_dict()
        document["player"] = _player_key(document["player"])
        self.crawl_file_collection.update_one(
            {"player": document["player"], "name": document["name"]},
            {"$set": document},
            upsert=True,
        )

    def list_crawl_user_records(
        self,
        players: list[str],
    ) -> dict[str, CrawlUserRecord]:
        if self.crawl_user_collection is None:
            return {}
        player_keys = _player_keys(players)
        if not player_keys:
            return {}
        documents = self.crawl_user_collection.find({"player": {"$in": player_keys}})
        records = [_crawl_user_record_from_mongo(document) for document in documents]
        return {_player_key(record.player): record for record in records}

    def save_crawl_user_record(self, record: CrawlUserRecord) -> None:
        if self.crawl_user_collection is None:
            return
        document = record.to_dict()
        document["player"] = _player_key(document["player"])
        self.crawl_user_collection.update_one(
            {"player": document["player"]},
            {"$set": document},
            upsert=True,
        )

    def list_raw_morgue_file_records_for_player_files(
        self,
        player: str,
        source_files: list[str],
    ) -> dict[str, RawMorgueFileRecord]:
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
        if self.raw_file_collection is None:
            return
        document = record.to_dict()
        document["player"] = _player_key(document["player"])
        self.raw_file_collection.update_one(
            {"player": document["player"], "name": document["name"]},
            {"$set": document},
            upsert=True,
        )

def repository_from_env() -> MongoCrawlRepository:
    """Create the crawl service MongoDB repository from its environment."""

    return create_mongo_crawl_repository(
        uri=os.environ.get("MONGODB_URI", DEFAULT_MONGO_URI),
        database=os.environ.get("MONGODB_DATABASE", DEFAULT_MONGO_DATABASE),
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
    crawl_files_collection: str = DEFAULT_MONGO_CRAWL_FILES_COLLECTION,
    crawl_users_collection: str = DEFAULT_MONGO_CRAWL_USERS_COLLECTION,
    raw_files_collection: str = DEFAULT_MONGO_RAW_FILES_COLLECTION,
    client_factory: Any | None = None,
) -> MongoCrawlRepository:
    """Create a MongoDB-backed crawl repository."""

    if client_factory is None:
        from pymongo import MongoClient

        client_factory = MongoClient
    client = client_factory(uri)
    database_handle = client[database]
    return MongoCrawlRepository(
        database_handle[crawl_files_collection],
        database_handle[crawl_users_collection],
        database_handle[raw_files_collection],
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
        stored_files=int(document.get("stored_files", document.get("processed_files", 0))),
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
        fetched_at=document.get("fetched_at"),
        fetch_error=document.get("fetch_error"),
    )


def _player_key(player: str) -> str:
    return player.strip().lower()


def _player_keys(players: list[str]) -> list[str]:
    return sorted({_player_key(player) for player in players if player.strip()})


def raw_text_hash(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()
