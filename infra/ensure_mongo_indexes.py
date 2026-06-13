"""Ensure MongoDB indexes owned by the infra layer."""

from __future__ import annotations

import os
import sys
import time
from typing import Any

from pymongo import MongoClient
from pymongo.errors import PyMongoError, ServerSelectionTimeoutError


DEFAULT_MONGO_URI = "mongodb://localhost:27018"
DEFAULT_MONGO_DATABASE = "dcss_arti_gallery"
DEFAULT_MONGO_COLLECTION = "artifacts"
DEFAULT_MONGO_CRAWL_FILES_COLLECTION = "crawl_files"
DEFAULT_MONGO_CRAWL_USERS_COLLECTION = "crawl_users"
DEFAULT_MONGO_RAW_FILES_COLLECTION = "raw_morgue_files"
DEFAULT_MONGO_ARTIFACT_PROCESSING_COLLECTION = "artifact_processing_files"
CONNECT_TIMEOUT_MS = 1000
RETRY_COUNT = 30
RETRY_DELAY_SECONDS = 0.5


def main() -> int:
    uri = os.environ.get("MONGODB_URI", DEFAULT_MONGO_URI)
    database_name = os.environ.get("MONGODB_DATABASE", DEFAULT_MONGO_DATABASE)
    client = MongoClient(uri, serverSelectionTimeoutMS=CONNECT_TIMEOUT_MS)

    try:
        _wait_for_mongo(client)
        database = client[database_name]
        _ensure_indexes(database)
    except PyMongoError as exc:
        print(f"failed to ensure MongoDB indexes: {exc}", file=sys.stderr)
        return 1
    finally:
        client.close()

    print(f"MongoDB indexes ensured: {uri} / {database_name}", file=sys.stderr)
    return 0


def _wait_for_mongo(client: MongoClient) -> None:
    last_error: Exception | None = None
    for _attempt in range(RETRY_COUNT):
        try:
            client.admin.command("ping")
            return
        except ServerSelectionTimeoutError as exc:
            last_error = exc
            time.sleep(RETRY_DELAY_SECONDS)
    if last_error is not None:
        raise last_error


def _ensure_indexes(database: Any) -> None:
    artifacts = database[os.environ.get("MONGODB_COLLECTION", DEFAULT_MONGO_COLLECTION)]
    crawl_files = database[
        os.environ.get("MONGODB_CRAWL_FILES_COLLECTION", DEFAULT_MONGO_CRAWL_FILES_COLLECTION)
    ]
    crawl_users = database[
        os.environ.get("MONGODB_CRAWL_USERS_COLLECTION", DEFAULT_MONGO_CRAWL_USERS_COLLECTION)
    ]
    raw_files = database[
        os.environ.get("MONGODB_RAW_FILES_COLLECTION", DEFAULT_MONGO_RAW_FILES_COLLECTION)
    ]
    processing = database[
        os.environ.get(
            "MONGODB_ARTIFACT_PROCESSING_COLLECTION",
            DEFAULT_MONGO_ARTIFACT_PROCESSING_COLLECTION,
        )
    ]

    crawl_files.create_index([("player", 1), ("name", 1)], unique=True)
    crawl_files.create_index("status")
    crawl_files.create_index(
        [("processed_at", -1)],
        name="crawl_file_errors_processed_at_desc",
        partialFilterExpression={"error": {"$type": "string"}},
    )

    crawl_users.create_index("player", unique=True)
    crawl_users.create_index("observed_at")
    crawl_users.create_index("status")
    crawl_users.create_index("scanned_at")
    crawl_users.create_index(
        [("scanned_at", -1)],
        name="crawl_user_errors_scanned_at_desc",
        partialFilterExpression={"error": {"$type": "string"}},
    )

    raw_files.create_index([("player", 1), ("name", 1)], unique=True)
    raw_files.create_index("content_hash")
    raw_files.create_index("fetch_status")
    raw_files.create_index("process_status")
    raw_files.create_index("fetched_at")
    raw_files.create_index("processed_at")
    raw_files.create_index([("fetch_status", 1), ("player", 1), ("name", 1)])
    raw_files.create_index(
        [("fetched_at", -1)],
        name="raw_fetch_errors_fetched_at_desc",
        partialFilterExpression={"fetch_error": {"$type": "string"}},
    )
    raw_files.create_index(
        [("processed_at", -1)],
        name="raw_process_errors_processed_at_desc",
        partialFilterExpression={"process_error": {"$type": "string"}},
    )

    artifacts.create_index("id", unique=True)
    artifacts.create_index("canonical_key", unique=True, sparse=True)
    artifacts.create_index([("source.player", 1), ("source.file", 1)])
    artifacts.create_index([("sources.player", 1), ("sources.file", 1)])
    artifacts.create_index("sources.occurrence_id")
    artifacts.create_index("occurrence_ids")
    artifacts.create_index([("evaluation.total", -1)])
    artifacts.create_index([("latest_game_ended_at", -1)])
    artifacts.create_index([("evaluation.total", -1), ("latest_game_ended_at", -1)])
    artifacts.create_index([("item_class", 1), ("evaluation.total", -1), ("latest_game_ended_at", -1)])
    artifacts.create_index("item_class")

    processing.create_index([("player", 1), ("name", 1)], unique=True)
    processing.create_index("status")
    processing.create_index("content_hash")


if __name__ == "__main__":
    raise SystemExit(main())
