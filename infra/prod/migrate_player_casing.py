"""Restore stored player casing from morgue file names.

This migration is intended for the production MongoDB after the code path stops
lower-casing player identifiers. It audits by default and only writes when
called with --apply.
"""

from __future__ import annotations

import argparse
import json
import os
import re
from collections import Counter, defaultdict
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from bson import json_util
from pymongo import MongoClient, UpdateOne


DEFAULT_MONGODB_URI = "mongodb://mongo:27017"
DEFAULT_MONGODB_DATABASE = "dcss_arti_gallery"
DEFAULT_RAW_FILES_COLLECTION = "raw_morgue_files"
DEFAULT_ARTIFACTS_COLLECTION = "artifacts"
DEFAULT_ARTIFACT_PROCESSING_COLLECTION = "artifact_processing_files"
DEFAULT_BATCH_SIZE = 1000
MORGUE_FILE_RE = re.compile(r"^\.?morgue-(?P<player>.+?)-\d{8}-\d{6}\.(?:txt|lst)$")


def main() -> None:
    args = _parse_args()
    database = _connect_database(args)
    collections = _collection_names(args)

    audit = audit_player_casing(database, collections)
    print(json.dumps(audit, indent=2, sort_keys=True))

    if _has_blocking_risk(audit):
        raise SystemExit("Blocking risk found. Refusing to apply migration.")
    if not args.apply:
        print("Dry run complete. Re-run with --apply to write changes.")
        return
    if not args.backup_confirmed:
        backup_dir = Path(args.backup_dir or _default_backup_dir())
        dump_collections(database, collections, backup_dir)
        print(f"Backup written to {backup_dir}")

    result = migrate_player_casing(database, collections, args.batch_size)
    print(json.dumps({"updated": result}, indent=2, sort_keys=True))


def audit_player_casing(database, collections: dict[str, str]) -> dict[str, Any]:
    file_collections = {
        "raw_morgue_files": collections["raw_morgue_files"],
        "artifact_processing_files": collections["artifact_processing_files"],
    }
    audit: dict[str, Any] = {"file_collections": {}}
    for label, collection_name in file_collections.items():
        audit["file_collections"][label] = _audit_file_collection(database[collection_name])
    audit["raw_player_lower_key_collisions"] = _raw_player_lower_key_collisions(
        database[collections["raw_morgue_files"]]
    )
    audit["artifact_sources"] = _audit_artifact_sources(database[collections["artifacts"]])
    return audit


def migrate_player_casing(database, collections: dict[str, str], batch_size: int) -> dict[str, int]:
    updated = {
        "raw_morgue_files": _migrate_file_collection(
            database[collections["raw_morgue_files"]],
            batch_size,
        ),
        "artifact_processing_files": _migrate_file_collection(
            database[collections["artifact_processing_files"]],
            batch_size,
        ),
        "artifacts": _migrate_artifacts(
            database[collections["artifacts"]],
            batch_size,
        ),
    }
    return updated


def dump_collections(database, collections: dict[str, str], backup_dir: Path) -> None:
    backup_dir.mkdir(parents=True, exist_ok=False)
    manifest: dict[str, Any] = {
        "created_at": datetime.now(UTC).isoformat(),
        "database": database.name,
        "collections": {},
    }
    for label, collection_name in collections.items():
        collection = database[collection_name]
        output_path = backup_dir / f"{collection_name}.jsonl"
        count = 0
        with output_path.open("w", encoding="utf-8") as output:
            for document in collection.find({}):
                output.write(json_util.dumps(document, sort_keys=True))
                output.write("\n")
                count += 1
        manifest["collections"][label] = {
            "collection": collection_name,
            "documents": count,
            "file": str(output_path),
            "indexes": list(collection.list_indexes()),
        }
    (backup_dir / "manifest.json").write_text(
        json_util.dumps(manifest, indent=2, sort_keys=True),
        encoding="utf-8",
    )


def _audit_file_collection(collection) -> dict[str, Any]:
    total = 0
    needing_update = 0
    missing_target = 0
    target_pairs: dict[tuple[str, str], Any] = {}
    target_pair_collisions: list[dict[str, Any]] = []
    examples = []
    for document in collection.find({}, {"player": 1, "name": 1}):
        total += 1
        target = _player_from_file(document.get("name"))
        if target is None:
            missing_target += 1
            continue
        if document.get("player") != target:
            needing_update += 1
            if len(examples) < 5:
                examples.append(
                    {
                        "current": document.get("player"),
                        "target": target,
                        "name": document.get("name"),
                    }
                )
        pair = (target, document.get("name"))
        existing_id = target_pairs.get(pair)
        if existing_id is not None and existing_id != document.get("_id"):
            target_pair_collisions.append(
                {
                    "player": target,
                    "name": document.get("name"),
                    "ids": [str(existing_id), str(document.get("_id"))],
                }
            )
        target_pairs[pair] = document.get("_id")
    return {
        "total": total,
        "needing_update": needing_update,
        "missing_target": missing_target,
        "target_pair_collisions": target_pair_collisions[:5],
        "target_pair_collision_count": len(target_pair_collisions),
        "examples": examples,
    }


def _raw_player_lower_key_collisions(raw_collection) -> list[dict[str, Any]]:
    players_by_key: dict[str, set[str]] = defaultdict(set)
    for document in raw_collection.find({}, {"player": 1}):
        player = document.get("player")
        if isinstance(player, str) and player:
            players_by_key[player.lower()].add(player)
    return [
        {"key": key, "players": sorted(players)}
        for key, players in sorted(players_by_key.items())
        if len(players) > 1
    ][:20]


def _audit_artifact_sources(collection) -> dict[str, Any]:
    docs_needing_update = 0
    source_entries_needing_update = 0
    docs_with_duplicate_sources_after_update = 0
    examples = []
    for document in collection.find({}, {"source": 1, "sources": 1, "first_source": 1}):
        document_needs_update = False
        for field in ("source", "first_source"):
            source = document.get(field)
            target = _target_player_for_source(source)
            if target is not None and isinstance(source, dict) and source.get("player") != target:
                document_needs_update = True
                if len(examples) < 5:
                    examples.append(
                        {
                            "field": field,
                            "current": source.get("player"),
                            "target": target,
                            "file": source.get("file"),
                        }
                    )
        source_keys = []
        for source in document.get("sources") or []:
            target = _target_player_for_source(source)
            player = target if target is not None else source.get("player")
            key = (player, source.get("file"), source.get("line"), source.get("occurrence_id"))
            source_keys.append(key)
            if target is not None and source.get("player") != target:
                document_needs_update = True
                source_entries_needing_update += 1
                if len(examples) < 5:
                    examples.append(
                        {
                            "field": "sources",
                            "current": source.get("player"),
                            "target": target,
                            "file": source.get("file"),
                        }
                    )
        if source_keys and any(count > 1 for count in Counter(source_keys).values()):
            docs_with_duplicate_sources_after_update += 1
        if document_needs_update:
            docs_needing_update += 1
    return {
        "docs_needing_update": docs_needing_update,
        "source_entries_needing_update": source_entries_needing_update,
        "docs_with_duplicate_sources_after_update": docs_with_duplicate_sources_after_update,
        "examples": examples,
    }


def _migrate_file_collection(collection, batch_size: int) -> int:
    updated = 0
    operations = []
    for document in collection.find({}, {"player": 1, "name": 1}):
        target = _player_from_file(document.get("name"))
        if target is not None and document.get("player") != target:
            operations.append(UpdateOne({"_id": document["_id"]}, {"$set": {"player": target}}))
        if len(operations) >= batch_size:
            updated += _flush(collection, operations)
    updated += _flush(collection, operations)
    return updated


def _migrate_artifacts(collection, batch_size: int) -> int:
    updated = 0
    operations = []
    for document in collection.find({}, {"source": 1, "sources": 1, "first_source": 1}):
        fields = {}
        source, changed = _source_with_original_player(document.get("source"))
        if changed:
            fields["source"] = source
        first_source, changed = _source_with_original_player(document.get("first_source"))
        if changed:
            fields["first_source"] = first_source
            fields["first_discovered_by"] = first_source["player"]
        sources = document.get("sources")
        if isinstance(sources, list):
            updated_sources = []
            sources_changed = False
            for source in sources:
                updated_source, changed = _source_with_original_player(source)
                updated_sources.append(updated_source)
                sources_changed = sources_changed or changed
            if sources_changed:
                fields["sources"] = updated_sources
        if fields:
            operations.append(UpdateOne({"_id": document["_id"]}, {"$set": fields}))
        if len(operations) >= batch_size:
            updated += _flush(collection, operations)
    updated += _flush(collection, operations)
    return updated


def _flush(collection, operations: list[UpdateOne]) -> int:
    if not operations:
        return 0
    result = collection.bulk_write(operations, ordered=False)
    operations.clear()
    return result.modified_count


def _raw_player_map(raw_collection) -> dict[str, str]:
    players_by_key: dict[str, set[str]] = defaultdict(set)
    for document in raw_collection.find({}, {"player": 1}):
        player = document.get("player")
        if isinstance(player, str) and player:
            players_by_key[player.lower()].add(player)
    return {
        key: next(iter(players))
        for key, players in players_by_key.items()
        if len(players) == 1
    }


def _source_with_original_player(source: Any) -> tuple[Any, bool]:
    if not isinstance(source, dict):
        return source, False
    target = _target_player_for_source(source)
    if target is None or source.get("player") == target:
        return source, False
    updated = dict(source)
    updated["player"] = target
    return updated, True


def _target_player_for_source(source: Any) -> str | None:
    if not isinstance(source, dict):
        return None
    return _player_from_file(source.get("file"))


def _player_from_file(file_name: Any) -> str | None:
    if not isinstance(file_name, str):
        return None
    match = MORGUE_FILE_RE.match(file_name)
    if match is None:
        return None
    return match.group("player")


def _has_blocking_risk(audit: dict[str, Any]) -> bool:
    file_collections = audit["file_collections"].values()
    return (
        any(item["target_pair_collision_count"] for item in file_collections)
        or bool(audit["raw_player_lower_key_collisions"])
        or audit["artifact_sources"]["docs_with_duplicate_sources_after_update"] > 0
    )


def _connect_database(args: argparse.Namespace):
    client = MongoClient(args.mongodb_uri)
    return client[args.mongodb_database]


def _collection_names(args: argparse.Namespace) -> dict[str, str]:
    return {
        "raw_morgue_files": args.raw_files_collection,
        "artifacts": args.artifacts_collection,
        "artifact_processing_files": args.artifact_processing_collection,
    }


def _default_backup_dir() -> str:
    stamp = datetime.now(UTC).strftime("%Y%m%d-%H%M%S")
    return f"_workspace/backups/prod-player-casing-{stamp}"


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--apply", action="store_true", help="write the migration")
    parser.add_argument(
        "--backup-confirmed",
        action="store_true",
        help="skip JSONL backup because an external MongoDB dump already exists",
    )
    parser.add_argument("--backup-dir", help="backup directory used before --apply")
    parser.add_argument("--batch-size", type=int, default=DEFAULT_BATCH_SIZE)
    parser.add_argument(
        "--mongodb-uri",
        default=os.environ.get("MONGODB_URI", DEFAULT_MONGODB_URI),
    )
    parser.add_argument(
        "--mongodb-database",
        default=os.environ.get("MONGODB_DATABASE", DEFAULT_MONGODB_DATABASE),
    )
    parser.add_argument(
        "--raw-files-collection",
        default=os.environ.get("MONGODB_RAW_FILES_COLLECTION", DEFAULT_RAW_FILES_COLLECTION),
    )
    parser.add_argument(
        "--artifacts-collection",
        default=os.environ.get("MONGODB_COLLECTION", DEFAULT_ARTIFACTS_COLLECTION),
    )
    parser.add_argument(
        "--artifact-processing-collection",
        default=os.environ.get(
            "MONGODB_ARTIFACT_PROCESSING_COLLECTION",
            DEFAULT_ARTIFACT_PROCESSING_COLLECTION,
        ),
    )
    args = parser.parse_args()
    if args.batch_size < 1:
        parser.error("--batch-size must be greater than 0")
    if args.backup_confirmed and args.backup_dir:
        parser.error("--backup-confirmed and --backup-dir cannot be used together")
    return args


if __name__ == "__main__":
    main()
