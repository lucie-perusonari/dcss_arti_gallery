"""Read-only MongoDB repository for crawl operations dashboard status."""

from __future__ import annotations

import os
import time
from typing import Any, Protocol

from admin_api.models import CrawlError, CrawlStatus, LatestActivity, RawFileStatus


DEFAULT_MONGO_URI = "mongodb://localhost:27018"
DEFAULT_MONGO_DATABASE = "dcss_arti_gallery"
DEFAULT_MONGO_COLLECTION = "artifacts"
DEFAULT_MONGO_CRAWL_FILES_COLLECTION = "crawl_files"
DEFAULT_MONGO_CRAWL_USERS_COLLECTION = "crawl_users"
DEFAULT_MONGO_RAW_FILES_COLLECTION = "raw_morgue_files"
DEFAULT_MONGO_ARTIFACT_PROCESSING_COLLECTION = "artifact_processing_files"
DEFAULT_CRAWL_STATUS_CACHE_SECONDS = 5.0
CRAWL_ACTIVE_COMPARE_SECONDS = 180.0

RAW_FILE_STATUS_PROJECTION = {
    "_id": False,
    "player": True,
    "name": True,
    "fetch_status": True,
    "process_status": True,
    "fetched_at": True,
    "processed_at": True,
    "fetch_error": True,
    "process_error": True,
}
CRAWL_FILE_STATUS_PROJECTION = {
    "_id": False,
    "player": True,
    "name": True,
    "status": True,
    "processed_at": True,
    "error": True,
}
CRAWL_USER_STATUS_PROJECTION = {
    "_id": False,
    "player": True,
    "status": True,
    "scanned_at": True,
    "error": True,
}
PROCESSING_STATUS_PROJECTION = {
    "_id": False,
    "player": True,
    "name": True,
    "status": True,
    "processed_at": True,
    "error": True,
}


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
        processing_collection=None,
        cache_ttl_seconds: float = DEFAULT_CRAWL_STATUS_CACHE_SECONDS,
    ) -> None:
        self.artifacts_collection = artifacts_collection
        self.raw_files_collection = raw_files_collection
        self.crawl_files_collection = crawl_files_collection
        self.crawl_users_collection = crawl_users_collection
        self.processing_collection = processing_collection
        self.cache_ttl_seconds = cache_ttl_seconds
        self._cached_status: CrawlStatus | None = None
        self._cached_at = 0.0
        self._raw_file_count_samples: list[tuple[float, int]] = []

    def get_crawl_status(self) -> CrawlStatus:
        now = time.monotonic()
        if self._cached_status is not None and now - self._cached_at < self.cache_ttl_seconds:
            return self._cached_status

        raw_file_status, latest_raw_activity, raw_errors = _raw_file_status_from_collection(
            self.raw_files_collection
        )
        processing_status = _processing_status_from_collection(
            self.processing_collection,
            raw_file_status=raw_file_status,
        )
        if processing_status is not None:
            raw_file_status, processed_at, processing_errors = processing_status
            latest_raw_activity["processed_at"] = processed_at
            raw_errors = [
                error for error in raw_errors if error.kind != "process"
            ]
            raw_errors.extend(processing_errors)
        crawl_file_counts, crawl_file_errors = _crawl_file_status_from_collection(self.crawl_files_collection)
        crawl_user_counts, latest_scanned_at, crawl_user_errors = _crawl_user_status_from_collection(
            self.crawl_users_collection
        )
        status = CrawlStatus(
            artifactCount=self.artifacts_collection.count_documents({}),
            crawlActive=self._raw_file_count_increased_since_comparison_window(
                now,
                raw_file_status.total,
            ),
            rawFiles=raw_file_status,
            crawlFiles=crawl_file_counts,
            crawlUsers=crawl_user_counts,
            latest=LatestActivity(
                fetchedAt=latest_raw_activity.get("fetched_at"),
                processedAt=latest_raw_activity.get("processed_at"),
                scannedAt=latest_scanned_at,
            ),
            recentErrors=_sort_recent_errors([*raw_errors, *crawl_file_errors, *crawl_user_errors]),
        )
        self._cached_status = status
        self._cached_at = now
        return status

    def _raw_file_count_increased_since_comparison_window(
        self,
        now: float,
        current_total: int,
    ) -> bool:
        self._raw_file_count_samples.append((now, current_total))
        comparison_samples = [
            (sampled_at, total)
            for sampled_at, total in self._raw_file_count_samples
            if now - sampled_at >= CRAWL_ACTIVE_COMPARE_SECONDS
        ]
        self._raw_file_count_samples = [
            (sampled_at, total)
            for sampled_at, total in self._raw_file_count_samples
            if now - sampled_at <= CRAWL_ACTIVE_COMPARE_SECONDS * 2
        ]
        if not comparison_samples:
            return False
        _, comparison_total = max(comparison_samples, key=lambda sample: sample[0])
        return current_total > comparison_total


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
        processing_collection=os.environ.get(
            "MONGODB_ARTIFACT_PROCESSING_COLLECTION",
            DEFAULT_MONGO_ARTIFACT_PROCESSING_COLLECTION,
        ),
        cache_ttl_seconds=_env_float("ADMIN_CRAWL_STATUS_CACHE_SECONDS", DEFAULT_CRAWL_STATUS_CACHE_SECONDS),
    )


def create_mongo_crawl_status_repository(
    uri: str = DEFAULT_MONGO_URI,
    database: str = DEFAULT_MONGO_DATABASE,
    artifacts_collection: str = DEFAULT_MONGO_COLLECTION,
    raw_files_collection: str = DEFAULT_MONGO_RAW_FILES_COLLECTION,
    crawl_files_collection: str = DEFAULT_MONGO_CRAWL_FILES_COLLECTION,
    crawl_users_collection: str = DEFAULT_MONGO_CRAWL_USERS_COLLECTION,
    processing_collection: str | None = None,
    cache_ttl_seconds: float = DEFAULT_CRAWL_STATUS_CACHE_SECONDS,
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
        database_handle[processing_collection] if processing_collection else None,
        cache_ttl_seconds,
    )


def _env_float(name: str, default: float) -> float:
    configured = os.environ.get(name)
    return default if configured is None else float(configured)


def _raw_file_status_from_collection(
    collection,
) -> tuple[RawFileStatus, dict[str, str | None], list[CrawlError]]:
    total, fetch_counts, process_counts = _raw_file_counts(collection)
    return (
        RawFileStatus(
            total=total,
            fetched=fetch_counts.get("fetched", 0),
            fetchFailed=fetch_counts.get("failed", 0),
            processPending=process_counts.get("pending", 0),
            processProcessed=process_counts.get("processed", 0),
            processFailed=process_counts.get("failed", 0),
        ),
        {
            "fetched_at": _latest_by_sort(collection, "fetched_at"),
            "processed_at": _latest_by_sort(collection, "processed_at"),
        },
        [
            *_raw_fetch_errors(
                _recent_documents(collection, "fetch_error", "fetched_at", RAW_FILE_STATUS_PROJECTION)
            ),
            *_raw_process_errors(
                _recent_documents(collection, "process_error", "processed_at", RAW_FILE_STATUS_PROJECTION)
            ),
        ],
    )


def _raw_file_counts(collection) -> tuple[int, dict[str, int], dict[str, int]]:
    result = next(
        collection.aggregate(
            [
                {
                    "$facet": {
                        "total": [{"$count": "count"}],
                        "fetch": [{"$group": {"_id": "$fetch_status", "count": {"$sum": 1}}}],
                        "process": [{"$group": {"_id": "$process_status", "count": {"$sum": 1}}}],
                    }
                }
            ]
        ),
        {},
    )
    total = result.get("total", [])
    return (
        total[0]["count"] if total else 0,
        _facet_counts(result.get("fetch", [])),
        _facet_counts(result.get("process", [])),
    )


def _facet_counts(documents: list[dict]) -> dict[str, int]:
    return {str(document.get("_id") or "unknown"): int(document.get("count", 0)) for document in documents}


def _processing_status_from_collection(
    collection,
    *,
    raw_file_status: RawFileStatus,
) -> tuple[RawFileStatus, str | None, list[CrawlError]] | None:
    if collection is None or collection.find_one({}, {"_id": True}) is None:
        return None

    counts = _status_counts_from_collection(collection, "status")
    completed = counts.get("completed", 0) + counts.get("processed", 0)
    failed = counts.get("failed", 0)
    pending = max(raw_file_status.fetched - completed - failed, 0)
    return (
        RawFileStatus(
            total=raw_file_status.total,
            fetched=raw_file_status.fetched,
            fetchFailed=raw_file_status.fetchFailed,
            processPending=pending,
            processProcessed=completed,
            processFailed=failed,
        ),
        _latest_by_sort(collection, "processed_at"),
        _processing_errors(
            _recent_documents(collection, "error", "processed_at", PROCESSING_STATUS_PROJECTION)
        ),
    )


def _status_counts_from_collection(collection, key: str) -> dict[str, int]:
    return _facet_counts(collection.aggregate([{"$group": {"_id": f"${key}", "count": {"$sum": 1}}}]))


def _crawl_file_status_from_collection(collection) -> tuple[dict[str, int], list[CrawlError]]:
    return (
        _status_counts_from_collection(collection, "status"),
        _crawl_file_errors(_recent_documents(collection, "error", "processed_at", CRAWL_FILE_STATUS_PROJECTION)),
    )


def _crawl_user_status_from_collection(collection) -> tuple[dict[str, int], str | None, list[CrawlError]]:
    return (
        _status_counts_from_collection(collection, "status"),
        _latest_by_sort(collection, "scanned_at"),
        _crawl_user_errors(_recent_documents(collection, "error", "scanned_at", CRAWL_USER_STATUS_PROJECTION)),
    )


def _latest_by_sort(collection, key: str) -> str | None:
    document = collection.find_one(
        {key: {"$exists": True}},
        {"_id": False, key: True},
        sort=[(key, -1)],
    )
    return document.get(key) if document else None


def _recent_documents(collection, error_key: str, sort_key: str, projection: dict) -> list[dict]:
    documents = list(
        collection.find(
            {error_key: {"$type": "string"}},
            projection,
        )
        .sort(sort_key, -1)
        .limit(50)
    )
    return [document for document in documents if document.get(error_key)][:10]


def _sort_recent_errors(errors: list[CrawlError]) -> list[CrawlError]:
    return sorted(errors, key=lambda error: error.at or "", reverse=True)[:10]


def _raw_fetch_errors(documents) -> list[CrawlError]:
    return [
        CrawlError(
            kind="fetch",
            player=str(document.get("player", "")),
            name=document.get("name"),
            message=str(document["fetch_error"]),
            at=document.get("fetched_at"),
        )
        for document in documents
    ]


def _raw_process_errors(documents) -> list[CrawlError]:
    return [
        CrawlError(
            kind="process",
            player=str(document.get("player", "")),
            name=document.get("name"),
            message=str(document["process_error"]),
            at=document.get("processed_at"),
        )
        for document in documents
    ]


def _processing_errors(documents) -> list[CrawlError]:
    return [
        CrawlError(
            kind="process",
            player=str(document.get("player", "")),
            name=document.get("name"),
            message=str(document["error"]),
            at=document.get("processed_at"),
        )
        for document in documents
    ]


def _crawl_file_errors(documents) -> list[CrawlError]:
    return [
        CrawlError(
            kind="file",
            player=str(document.get("player", "")),
            name=document.get("name"),
            message=str(document["error"]),
            at=document.get("processed_at"),
        )
        for document in documents
    ]


def _crawl_user_errors(documents) -> list[CrawlError]:
    return [
        CrawlError(
            kind="user",
            player=str(document.get("player", "")),
            message=str(document["error"]),
            at=document.get("scanned_at"),
        )
        for document in documents
    ]
