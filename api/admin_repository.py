"""Read-only MongoDB repository for crawl operations dashboard status."""

from __future__ import annotations

import os
from typing import Any, Protocol

from api.admin_models import CrawlError, CrawlStatus, LatestActivity, RawFileStatus


DEFAULT_MONGO_URI = "mongodb://localhost:27017"
DEFAULT_MONGO_DATABASE = "dcss_best_arti"
DEFAULT_MONGO_COLLECTION = "artifacts"
DEFAULT_MONGO_CRAWL_FILES_COLLECTION = "crawl_files"
DEFAULT_MONGO_CRAWL_USERS_COLLECTION = "crawl_users"
DEFAULT_MONGO_RAW_FILES_COLLECTION = "raw_morgue_files"


class CrawlStatusRepository(Protocol):
    def get_crawl_status(self) -> CrawlStatus:
        ...


class MongoCrawlStatusRepository:
    """MongoDB-backed read repository for crawl operations status."""

    def __init__(
        self,
        artifacts_collection,
        raw_files_collection,
        crawl_files_collection,
        crawl_users_collection,
    ) -> None:
        self.artifacts_collection = artifacts_collection
        self.raw_files_collection = raw_files_collection
        self.crawl_files_collection = crawl_files_collection
        self.crawl_users_collection = crawl_users_collection

    def get_crawl_status(self) -> CrawlStatus:
        raw_files = list(self.raw_files_collection.find({}))
        crawl_files = list(self.crawl_files_collection.find({}))
        crawl_users = list(self.crawl_users_collection.find({}))
        return CrawlStatus(
            artifactCount=self.artifacts_collection.count_documents({}),
            rawFiles=_raw_file_status(raw_files),
            crawlFiles=_status_counts(crawl_files, "status"),
            crawlUsers=_status_counts(crawl_users, "status"),
            latest=LatestActivity(
                fetchedAt=_latest(raw_files, "fetched_at"),
                processedAt=_latest(raw_files, "processed_at"),
                scannedAt=_latest(crawl_users, "scanned_at"),
            ),
            recentErrors=_recent_errors(raw_files, crawl_files, crawl_users),
        )


def repository_from_env() -> MongoCrawlStatusRepository:
    return create_mongo_crawl_status_repository(
        uri=os.environ.get("MONGODB_URI", DEFAULT_MONGO_URI),
        database=os.environ.get("MONGODB_DATABASE", DEFAULT_MONGO_DATABASE),
        artifacts_collection=os.environ.get("MONGODB_COLLECTION", DEFAULT_MONGO_COLLECTION),
        raw_files_collection=os.environ.get(
            "MONGODB_RAW_FILES_COLLECTION",
            DEFAULT_MONGO_RAW_FILES_COLLECTION,
        ),
        crawl_files_collection=os.environ.get(
            "MONGODB_CRAWL_FILES_COLLECTION",
            DEFAULT_MONGO_CRAWL_FILES_COLLECTION,
        ),
        crawl_users_collection=os.environ.get(
            "MONGODB_CRAWL_USERS_COLLECTION",
            DEFAULT_MONGO_CRAWL_USERS_COLLECTION,
        ),
    )


def create_mongo_crawl_status_repository(
    uri: str = DEFAULT_MONGO_URI,
    database: str = DEFAULT_MONGO_DATABASE,
    artifacts_collection: str = DEFAULT_MONGO_COLLECTION,
    raw_files_collection: str = DEFAULT_MONGO_RAW_FILES_COLLECTION,
    crawl_files_collection: str = DEFAULT_MONGO_CRAWL_FILES_COLLECTION,
    crawl_users_collection: str = DEFAULT_MONGO_CRAWL_USERS_COLLECTION,
    client_factory: Any | None = None,
) -> MongoCrawlStatusRepository:
    if client_factory is None:
        from pymongo import MongoClient

        client_factory = MongoClient
    client = client_factory(uri)
    database_handle = client[database]
    return MongoCrawlStatusRepository(
        database_handle[artifacts_collection],
        database_handle[raw_files_collection],
        database_handle[crawl_files_collection],
        database_handle[crawl_users_collection],
    )


def _raw_file_status(documents: list[dict]) -> RawFileStatus:
    return RawFileStatus(
        total=len(documents),
        fetched=sum(1 for document in documents if document.get("fetch_status") == "fetched"),
        fetchFailed=sum(1 for document in documents if document.get("fetch_status") == "failed"),
        processPending=sum(1 for document in documents if document.get("process_status") == "pending"),
        processProcessed=sum(1 for document in documents if document.get("process_status") == "processed"),
        processFailed=sum(1 for document in documents if document.get("process_status") == "failed"),
    )


def _status_counts(documents: list[dict], key: str) -> dict[str, int]:
    counts: dict[str, int] = {}
    for document in documents:
        status = str(document.get(key) or "unknown")
        counts[status] = counts.get(status, 0) + 1
    return counts


def _latest(documents: list[dict], key: str) -> str | None:
    values = [document.get(key) for document in documents if document.get(key)]
    return max(values) if values else None


def _recent_errors(
    raw_files: list[dict],
    crawl_files: list[dict],
    crawl_users: list[dict],
) -> list[CrawlError]:
    errors: list[CrawlError] = []
    for document in raw_files:
        if document.get("fetch_error"):
            errors.append(
                CrawlError(
                    kind="fetch",
                    player=str(document.get("player", "")),
                    name=document.get("name"),
                    message=str(document["fetch_error"]),
                    at=document.get("fetched_at"),
                )
            )
        if document.get("process_error"):
            errors.append(
                CrawlError(
                    kind="process",
                    player=str(document.get("player", "")),
                    name=document.get("name"),
                    message=str(document["process_error"]),
                    at=document.get("processed_at"),
                )
            )
    for document in crawl_files:
        if document.get("error"):
            errors.append(
                CrawlError(
                    kind="file",
                    player=str(document.get("player", "")),
                    name=document.get("name"),
                    message=str(document["error"]),
                    at=document.get("processed_at"),
                )
            )
    for document in crawl_users:
        if document.get("error"):
            errors.append(
                CrawlError(
                    kind="user",
                    player=str(document.get("player", "")),
                    message=str(document["error"]),
                    at=document.get("scanned_at"),
                )
            )
    return sorted(errors, key=lambda error: error.at or "", reverse=True)[:10]
