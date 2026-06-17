from __future__ import annotations

import os
import time
import uuid

from admin_api.repository import create_mongo_crawl_status_repository


def mongo_crawl_status_repository_for_test(prefix: str):
    env = _ensure_mongo_env()
    suffix = uuid.uuid4().hex
    repository = create_mongo_crawl_status_repository(
        uri=env["MONGODB_URI"],
        database=env["MONGODB_DATABASE"],
        artifacts_collection=f"{prefix}_artifacts_{suffix}",
        raw_files_collection=f"{prefix}_raw_files_{suffix}",
        crawl_errors_collection=f"{prefix}_crawl_errors_{suffix}",
    )
    _wait_for_collection(repository.artifacts_collection)
    return repository


def drop_crawl_status_repository_collections(repository) -> None:
    repository.artifacts_collection.drop()
    repository.raw_files_collection.drop()
    repository.crawl_errors_collection.drop()


def _ensure_mongo_env() -> dict[str, str]:
    return {
        "MONGODB_URI": os.environ.get("MONGODB_URI", "mongodb://localhost:27018"),
        "MONGODB_DATABASE": os.environ.get("MONGODB_DATABASE", "dcss_arti_gallery"),
    }


def _wait_for_collection(collection) -> None:
    last_error: Exception | None = None
    for _ in range(50):
        try:
            collection.database.command("ping")
            return
        except Exception as exc:
            last_error = exc
            time.sleep(0.1)
    raise RuntimeError(f"MongoDB did not become ready: {last_error}")
