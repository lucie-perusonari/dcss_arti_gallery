"""Crawl service MongoDB repository for morgue ingest state."""

from __future__ import annotations

import hashlib
import os
from dataclasses import dataclass


DEFAULT_MONGO_URI = "mongodb://localhost:27018"
DEFAULT_MONGO_DATABASE = "dcss_arti_gallery"
DEFAULT_MONGO_CRAWL_ERRORS_COLLECTION = "crawl_errors"
DEFAULT_MONGO_RAW_FILES_COLLECTION = "raw_morgue_files"

FETCH_STATUS_FETCHED = "fetched"


@dataclass(frozen=True)
class CrawlErrorRecord:
    """Append-only crawl failure event."""

    player: str
    stage: str
    message: str
    occurred_at: str
    name: str | None = None
    url: str | None = None
    extension: str | None = None
    error_type: str | None = None
    user_url: str | None = None

    def to_dict(self) -> dict:
        return {
            "player": self.player,
            "name": self.name,
            "url": self.url,
            "extension": self.extension,
            "stage": self.stage,
            "message": self.message,
            "error_type": self.error_type,
            "user_url": self.user_url,
            "occurred_at": self.occurred_at,
        }


@dataclass(frozen=True)
class RawMorgueFileRecord:
    """Fetched morgue source text."""

    player: str
    name: str
    url: str
    extension: str
    text: str
    content_hash: str = ""
    fetch_status: str = FETCH_STATUS_FETCHED
    fetched_at: str | None = None

    def __post_init__(self) -> None:
        if not self.content_hash:
            object.__setattr__(self, "content_hash", raw_text_hash(self.text))
        if not self.fetch_status:
            object.__setattr__(self, "fetch_status", FETCH_STATUS_FETCHED)

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
        }


class MongoCrawlRepository:
    """MongoDB-backed repository for crawl_service morgue ingest state."""

    def __init__(self, database) -> None:
        self.client = getattr(database, "client", None)
        self.crawl_error_collection = database[DEFAULT_MONGO_CRAWL_ERRORS_COLLECTION]
        self.raw_file_collection = database[DEFAULT_MONGO_RAW_FILES_COLLECTION]

    def close(self) -> None:
        if self.client is not None:
            self.client.close()

    def save_crawl_error_record(self, record: CrawlErrorRecord) -> None:
        self.crawl_error_collection.insert_one(record.to_dict())

    def list_raw_morgue_file_records_for_files(
        self,
        source_files: list[str],
    ) -> dict[str, RawMorgueFileRecord]:
        file_names = sorted({source_file for source_file in source_files if source_file})
        if not file_names:
            return {}
        documents = self.raw_file_collection.find(
            {
                "name": {"$in": file_names},
            }
        )
        records = [_raw_morgue_file_record_from_mongo(document) for document in documents]
        return {record.name: record for record in records}

    def save_raw_morgue_file(self, record: RawMorgueFileRecord) -> None:
        document = record.to_dict()
        self.raw_file_collection.replace_one(
            {"player": document["player"], "name": document["name"]},
            document,
            upsert=True,
        )


def create_mongo_crawl_repository() -> MongoCrawlRepository:
    """Create a MongoDB-backed crawl repository."""

    from pymongo import MongoClient

    client = MongoClient(os.environ.get("MONGODB_URI", DEFAULT_MONGO_URI))
    database_handle = client[DEFAULT_MONGO_DATABASE]
    return MongoCrawlRepository(database_handle)


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
    )


def raw_text_hash(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()
