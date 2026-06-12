#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR=$(CDPATH= cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)
ROOT_DIR=$(CDPATH= cd -- "$SCRIPT_DIR/.." && pwd)

export MONGODB_URI="${MONGODB_URI:-mongodb://localhost:27017}"
export MONGODB_DATABASE="${MONGODB_DATABASE:-dcss_arti_gallery}"
export MONGODB_COLLECTION="${MONGODB_COLLECTION:-artifacts}"
export MONGODB_CRAWL_FILES_COLLECTION="${MONGODB_CRAWL_FILES_COLLECTION:-crawl_files}"
export MONGODB_CRAWL_USERS_COLLECTION="${MONGODB_CRAWL_USERS_COLLECTION:-crawl_users}"
export MONGODB_RAW_FILES_COLLECTION="${MONGODB_RAW_FILES_COLLECTION:-raw_morgue_files}"

PROCESS_LIMIT="${PROCESS_LIMIT:-1000}"
ONCE="${ONCE:-0}"

cd "$ROOT_DIR"

python3 - "$PROCESS_LIMIT" "$ONCE" <<'PY'
from __future__ import annotations

import sys
from datetime import UTC, datetime

from crawl_service.core.processor import (
    CURRENT_PARSER_VERSION,
    CURRENT_SCORING_VERSION,
    process_raw_morgue_file,
)
from crawl_service.core.repository import repository_from_env


def utc_now() -> str:
    return datetime.now(UTC).isoformat()


def pending_count(repository) -> int | None:
    collection = getattr(repository, "raw_file_collection", None)
    if collection is None or not hasattr(collection, "count_documents"):
        return None
    return collection.count_documents(
        {
            "fetch_status": "fetched",
            "$or": [
                {"process_status": {"$in": ["pending", "failed"]}},
                {"parser_version": {"$ne": CURRENT_PARSER_VERSION}},
                {"scoring_version": {"$ne": CURRENT_SCORING_VERSION}},
            ],
        }
    )


def main() -> int:
    limit = max(int(sys.argv[1]), 1)
    once = sys.argv[2] == "1"
    repository = repository_from_env()
    artifacts_imported = 0
    files_processed = 0
    files_failed = 0
    failed_keys: set[tuple[str, str]] = set()

    print("Processing fetched raw morgue files.")
    print(f"  Batch limit: {limit}")
    print(f"  Parser: {CURRENT_PARSER_VERSION}")
    print(f"  Scoring: {CURRENT_SCORING_VERSION}")

    while True:
        remaining = pending_count(repository)
        if remaining is not None:
            print(f"  Pending before batch: {remaining}")
            if remaining <= 0:
                break

        fetch_limit = limit + len(failed_keys)
        raw_files = repository.list_raw_morgue_files_for_processing(
            parser_version=CURRENT_PARSER_VERSION,
            scoring_version=CURRENT_SCORING_VERSION,
            limit=fetch_limit,
        )
        raw_files = [
            raw_file
            for raw_file in raw_files
            if (raw_file.player, raw_file.name) not in failed_keys
        ][:limit]
        if not raw_files:
            break

        for raw_file in raw_files:
            try:
                artifact_count = process_raw_morgue_file(
                    repository,
                    raw_file,
                    processed_at=utc_now(),
                )
            except Exception as exc:
                files_failed += 1
                failed_keys.add((raw_file.player, raw_file.name))
                print(f"  FAILED {raw_file.player}/{raw_file.name}: {exc}")
                continue

            files_processed += 1
            artifacts_imported += artifact_count
            print(
                "  processed "
                f"{raw_file.player}/{raw_file.name}: {artifact_count} artifacts"
            )

        if once:
            break

    print("Raw morgue processing complete.")
    print(f"  Files processed: {files_processed}")
    print(f"  Files failed: {files_failed}")
    print(f"  Artifacts imported: {artifacts_imported}")
    remaining = pending_count(repository)
    if remaining is not None:
        print(f"  Pending after run: {remaining}")
    return 1 if files_failed else 0


raise SystemExit(main())
PY
