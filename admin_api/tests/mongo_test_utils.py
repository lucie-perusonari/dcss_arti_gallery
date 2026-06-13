from __future__ import annotations

import os
import subprocess
import time
import uuid
from pathlib import Path

from admin_api.repository import create_mongo_crawl_status_repository


PROJECT_ROOT = Path(__file__).resolve().parents[2]
SCRIPT_DIR = PROJECT_ROOT / "infra" / "dev"


def mongo_crawl_status_repository_for_test(prefix: str):
    env = _ensure_mongo_env()
    suffix = uuid.uuid4().hex
    repository = create_mongo_crawl_status_repository(
        uri=env["MONGODB_URI"],
        database=env["MONGODB_DATABASE"],
        artifacts_collection=f"{prefix}_artifacts_{suffix}",
        raw_files_collection=f"{prefix}_raw_files_{suffix}",
        crawl_files_collection=f"{prefix}_crawl_files_{suffix}",
        crawl_users_collection=f"{prefix}_crawl_users_{suffix}",
    )
    _wait_for_collection(repository.artifacts_collection)
    return repository


def drop_crawl_status_repository_collections(repository) -> None:
    repository.artifacts_collection.drop()
    repository.raw_files_collection.drop()
    repository.crawl_files_collection.drop()
    repository.crawl_users_collection.drop()


def _ensure_mongo_env() -> dict[str, str]:
    if (
        os.environ.get("ALLOW_TEST_MONGO_ENV_OVERRIDE") == "1"
        and os.environ.get("MONGODB_URI")
        and os.environ.get("MONGODB_DATABASE")
    ):
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
