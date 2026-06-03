from __future__ import annotations

import os
import subprocess
import time
import uuid
from pathlib import Path

from crawl_service.repository import create_mongo_crawl_repository


PROJECT_ROOT = Path(__file__).resolve().parents[2]
SCRIPT_DIR = PROJECT_ROOT / "infra" / "mongo"


def mongo_repository_for_test(prefix: str):
    env = _ensure_mongo_env()
    suffix = uuid.uuid4().hex
    repository = create_mongo_crawl_repository(
        uri=env["MONGODB_URI"],
        database=env["MONGODB_DATABASE"],
        collection=f"{prefix}_artifacts_{suffix}",
        crawl_files_collection=f"{prefix}_crawl_files_{suffix}",
        crawl_users_collection=f"{prefix}_crawl_users_{suffix}",
        raw_files_collection=f"{prefix}_raw_files_{suffix}",
    )
    _wait_for_mongo(repository)
    return repository


def drop_repository_collections(repository) -> None:
    repository.collection.drop()
    if repository.crawl_file_collection is not None:
        repository.crawl_file_collection.drop()
    if repository.crawl_user_collection is not None:
        repository.crawl_user_collection.drop()
    if repository.raw_file_collection is not None:
        repository.raw_file_collection.drop()


def _ensure_mongo_env() -> dict[str, str]:
    if os.environ.get("MONGODB_URI") and os.environ.get("MONGODB_DATABASE"):
        return {
            "MONGODB_URI": os.environ["MONGODB_URI"],
            "MONGODB_DATABASE": os.environ["MONGODB_DATABASE"],
        }

    result = subprocess.run(
        [str(SCRIPT_DIR / "mongo_up.sh")],
        check=True,
        capture_output=True,
        text=True,
    )
    env = _parse_exports(result.stdout)
    return {
        "MONGODB_URI": env["MONGODB_URI"],
        "MONGODB_DATABASE": env["MONGODB_DATABASE"],
    }


def _parse_exports(output: str) -> dict[str, str]:
    env: dict[str, str] = {}
    for line in output.splitlines():
        if not line.startswith("export "):
            continue
        key, value = line.removeprefix("export ").split("=", 1)
        env[key] = value
    return env


def _wait_for_mongo(repository) -> None:
    last_error: Exception | None = None
    for _ in range(50):
        try:
            repository.collection.database.command("ping")
            return
        except Exception as exc:
            last_error = exc
            time.sleep(0.1)
    raise RuntimeError(f"MongoDB did not become ready: {last_error}")
