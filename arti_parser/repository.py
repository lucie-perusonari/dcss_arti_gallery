"""MongoDB repository for artifact read-model regeneration."""

from __future__ import annotations

import os
import re
from dataclasses import dataclass
from datetime import UTC, datetime
from typing import Any, Protocol

from arti_parser.models import ArtifactDocument


DEFAULT_MONGO_URI = "mongodb://localhost:27018"
DEFAULT_MONGO_DATABASE = "dcss_arti_gallery"
DEFAULT_MONGO_RAW_FILES_COLLECTION = "raw_morgue_files"
DEFAULT_MONGO_ARTIFACTS_COLLECTION = "artifacts"
DEFAULT_MONGO_ARTIFACT_PROCESSING_COLLECTION = "artifact_processing_files"
FETCH_STATUS_FETCHED = "fetched"
PROCESSING_STATUS_COMPLETED = "completed"
PROCESSING_STATUS_FAILED = "failed"
ARTIFACT_METADATA_VERSION = "attribute-delta-v1"
MORGUE_FILE_DATE_RE = re.compile(r"-(?P<date>\d{8})-(?P<time>\d{6})(?:\.[^.]+)?$")
RAW_FILE_METADATA_PROJECTION = {
    "_id": 0,
    "player": 1,
    "name": 1,
    "url": 1,
    "extension": 1,
    "content_hash": 1,
    "fetch_status": 1,
    "fetched_at": 1,
    "fetch_error": 1,
}
RAW_FILE_TEXT_PROJECTION = {
    **RAW_FILE_METADATA_PROJECTION,
    "text": 1,
}


@dataclass(frozen=True)
class RawMorgueSource:
    """Fetched raw morgue source consumed by artifact processing."""

    player: str
    name: str
    url: str
    extension: str
    text: str
    content_hash: str
    fetch_status: str
    fetched_at: str | None = None
    fetch_error: str | None = None

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


@dataclass(frozen=True)
class ArtifactProcessingRecord:
    """Artifact regeneration status for one raw morgue file."""

    player: str
    name: str
    content_hash: str
    status: str
    artifact_count: int = 0
    processed_at: str | None = None
    error: str | None = None
    metadata_version: str = ARTIFACT_METADATA_VERSION

    def to_dict(self) -> dict:
        return {
            "player": self.player,
            "name": self.name,
            "content_hash": self.content_hash,
            "status": self.status,
            "artifact_count": self.artifact_count,
            "processed_at": self.processed_at,
            "error": self.error,
            "metadata_version": self.metadata_version,
        }


@dataclass(frozen=True)
class ArtifactSaveResult:
    """Write result for one processed raw morgue file."""

    artifact_count: int
    stale_deleted: int


class ArtifactProcessingRepository(Protocol):
    def list_pending_raw_files(
        self,
        *,
        limit: int,
        scan_batch_size: int,
    ) -> list[RawMorgueSource]:
        ...

    def save_artifacts_for_raw_file(
        self,
        *,
        raw_file: RawMorgueSource,
        artifacts: list[ArtifactDocument],
        processed_at: str,
    ) -> ArtifactSaveResult:
        ...

    def save_processing_failure(
        self,
        *,
        raw_file: RawMorgueSource,
        processed_at: str,
        error: str,
    ) -> None:
        ...


class MongoArtifactProcessingRepository:
    """MongoDB-backed repository for raw-to-artifact processing."""

    def __init__(
        self,
        raw_file_collection=None,
        artifacts_collection=None,
        processing_collection=None,
    ) -> None:
        self.raw_file_collection = raw_file_collection
        self.artifacts_collection = artifacts_collection
        self.processing_collection = processing_collection

    def list_pending_raw_files(
        self,
        *,
        limit: int,
        scan_batch_size: int,
    ) -> list[RawMorgueSource]:
        if self.raw_file_collection is None or limit < 1:
            return []

        pending: list[RawMorgueSource] = []
        scan_batch_size = max(scan_batch_size, 1)
        cursor = self.raw_file_collection.find(
            {"fetch_status": FETCH_STATUS_FETCHED},
            RAW_FILE_METADATA_PROJECTION,
        ).sort([("player", 1), ("name", 1)])
        if hasattr(cursor, "batch_size"):
            cursor = cursor.batch_size(scan_batch_size)

        batch: list[RawMorgueSource] = []
        for document in cursor:
            batch.append(_raw_morgue_file_record_from_mongo(document))
            if len(batch) >= scan_batch_size:
                pending.extend(
                    self._pending_from_batch(
                        batch,
                    )
                )
                if len(pending) >= limit:
                    return self._raw_files_with_text(pending[:limit])
                batch = []

        if batch:
            pending.extend(
                self._pending_from_batch(
                    batch,
                )
            )
        return self._raw_files_with_text(pending[:limit])

    def save_artifacts_for_raw_file(
        self,
        *,
        raw_file: RawMorgueSource,
        artifacts: list[ArtifactDocument],
        processed_at: str,
    ) -> ArtifactSaveResult:
        occurrence_canonical_ids = {
            artifact.occurrence_id: artifact.id
            for artifact in artifacts
        }
        stale_deleted = self._delete_stale_artifact_sources(raw_file, occurrence_canonical_ids)
        if self.artifacts_collection is not None:
            existing_artifacts = self._existing_artifacts_by_id(
                [artifact.id for artifact in artifacts]
            )
            update_operations = []
            for artifact in artifacts:
                document = _canonical_artifact_mongo_document(
                    artifact,
                    raw_file=raw_file,
                    processed_at=processed_at,
                    existing=existing_artifacts.get(artifact.id),
                )
                update_operations.append(
                    _update_one_operation(
                        {"id": artifact.id},
                        {
                            "$set": document,
                            "$unset": _version_metadata_unset(),
                        },
                        upsert=True,
                    )
                )
            if update_operations:
                self._bulk_write_artifact_updates(update_operations)

        self._save_processing_record(
            ArtifactProcessingRecord(
                player=raw_file.player,
                name=raw_file.name,
                content_hash=raw_file.content_hash,
                status=PROCESSING_STATUS_COMPLETED,
                artifact_count=len(artifacts),
                processed_at=processed_at,
                error=None,
            )
        )
        return ArtifactSaveResult(
            artifact_count=len(artifacts),
            stale_deleted=stale_deleted,
        )

    def save_processing_failure(
        self,
        *,
        raw_file: RawMorgueSource,
        processed_at: str,
        error: str,
    ) -> None:
        self._save_processing_record(
            ArtifactProcessingRecord(
                player=raw_file.player,
                name=raw_file.name,
                content_hash=raw_file.content_hash,
                status=PROCESSING_STATUS_FAILED,
                artifact_count=0,
                processed_at=processed_at,
                error=error,
            )
        )

    def _pending_from_batch(
        self,
        batch: list[RawMorgueSource],
    ) -> list[RawMorgueSource]:
        processing_records = self._processing_records_for_raw_files(batch)
        pending: list[RawMorgueSource] = []
        for raw_file in batch:
            record = processing_records.get((raw_file.player, raw_file.name))
            if record is None or _should_process(raw_file, record):
                pending.append(raw_file)
        return pending

    def _processing_records_for_raw_files(
        self,
        raw_files: list[RawMorgueSource],
    ) -> dict[tuple[str, str], ArtifactProcessingRecord]:
        if self.processing_collection is None or not raw_files:
            return {}
        documents = self.processing_collection.find(
            _raw_file_pair_query(raw_files)
        )
        records = [_processing_record_from_mongo(document) for document in documents]
        return {(record.player, record.name): record for record in records}

    def _raw_files_with_text(
        self,
        raw_files: list[RawMorgueSource],
    ) -> list[RawMorgueSource]:
        if self.raw_file_collection is None or not raw_files:
            return raw_files
        documents = self.raw_file_collection.find(
            _raw_file_pair_query(raw_files),
            RAW_FILE_TEXT_PROJECTION,
        )
        records = {
            (record.player, record.name): record
            for record in (
                _raw_morgue_file_record_from_mongo(document)
                for document in documents
            )
        }
        return [
            records.get((raw_file.player, raw_file.name), raw_file)
            for raw_file in raw_files
        ]

    def _delete_stale_artifact_sources(
        self,
        raw_file: RawMorgueSource,
        current_occurrence_canonical_ids: dict[str, str],
    ) -> int:
        if self.artifacts_collection is None:
            return 0
        stale_removed = 0
        for document in list(self.artifacts_collection.find(_artifact_source_query(raw_file))):
            sources = _artifact_sources_from_document(document)
            kept_sources = [
                source
                for source in sources
                if _should_keep_source_evidence(
                    source,
                    raw_file=raw_file,
                    document_id=document.get("id", ""),
                    current_occurrence_canonical_ids=current_occurrence_canonical_ids,
                )
            ]
            removed = len(sources) - len(kept_sources)
            if removed == 0:
                continue
            stale_removed += removed
            if kept_sources:
                self.artifacts_collection.update_one(
                    {"id": document["id"]},
                    {"$set": _artifact_document_with_sources(document, kept_sources)},
                    upsert=False,
                )
            else:
                self.artifacts_collection.delete_many({"id": document["id"]})
        return stale_removed

    def _existing_artifacts_by_id(self, artifact_ids: list[str]) -> dict[str, dict]:
        if self.artifacts_collection is None:
            return {}
        ids = sorted(set(artifact_ids))
        if not ids:
            return {}
        documents = self.artifacts_collection.find({"id": {"$in": ids}})
        return {
            str(document.get("id", "")): document
            for document in documents
            if document.get("id")
        }

    def _bulk_write_artifact_updates(self, operations: list[Any]) -> None:
        if self.artifacts_collection is None:
            return
        if hasattr(self.artifacts_collection, "bulk_write"):
            self.artifacts_collection.bulk_write(operations, ordered=False)
            return
        for operation in operations:
            self.artifacts_collection.update_one(
                operation._filter,
                operation._doc,
                upsert=operation._upsert,
            )

    def _save_processing_record(self, record: ArtifactProcessingRecord) -> None:
        if self.processing_collection is None:
            return
        document = record.to_dict()
        self.processing_collection.update_one(
            {"player": document["player"], "name": document["name"]},
            {
                "$set": document,
                "$unset": _version_metadata_unset(),
            },
            upsert=True,
        )

def repository_from_env() -> MongoArtifactProcessingRepository:
    return create_mongo_artifact_processing_repository(
        uri=os.environ.get("MONGODB_URI", DEFAULT_MONGO_URI),
        database=os.environ.get("MONGODB_DATABASE", DEFAULT_MONGO_DATABASE),
        raw_files_collection=os.environ.get(
            "MONGODB_RAW_FILES_COLLECTION",
            DEFAULT_MONGO_RAW_FILES_COLLECTION,
        ),
        artifacts_collection=os.environ.get(
            "MONGODB_COLLECTION",
            DEFAULT_MONGO_ARTIFACTS_COLLECTION,
        ),
        processing_collection=os.environ.get(
            "MONGODB_ARTIFACT_PROCESSING_COLLECTION",
            DEFAULT_MONGO_ARTIFACT_PROCESSING_COLLECTION,
        ),
    )


def create_mongo_artifact_processing_repository(
    uri: str = DEFAULT_MONGO_URI,
    database: str = DEFAULT_MONGO_DATABASE,
    raw_files_collection: str = DEFAULT_MONGO_RAW_FILES_COLLECTION,
    artifacts_collection: str = DEFAULT_MONGO_ARTIFACTS_COLLECTION,
    processing_collection: str = DEFAULT_MONGO_ARTIFACT_PROCESSING_COLLECTION,
    client_factory: Any | None = None,
) -> MongoArtifactProcessingRepository:
    if client_factory is None:
        from pymongo import MongoClient

        client_factory = MongoClient
    client = client_factory(uri)
    database_handle = client[database]
    return MongoArtifactProcessingRepository(
        database_handle[raw_files_collection],
        database_handle[artifacts_collection],
        database_handle[processing_collection],
    )


def _artifact_mongo_document(
    artifact: ArtifactDocument,
    *,
    raw_file: RawMorgueSource,
) -> dict:
    document = artifact.to_dict()
    document["source"]["player"] = raw_file.player
    document["source_content_hash"] = raw_file.content_hash
    return document


def _update_one_operation(filter_document: dict, update_document: dict, *, upsert: bool):
    from pymongo import UpdateOne

    return UpdateOne(filter_document, update_document, upsert=upsert)


def _canonical_artifact_mongo_document(
    artifact: ArtifactDocument,
    *,
    raw_file: RawMorgueSource,
    processed_at: str,
    existing: dict | None,
) -> dict:
    candidate = _artifact_mongo_document(
        artifact,
        raw_file=raw_file,
    )
    source = _artifact_source_evidence(
        artifact,
        raw_file=raw_file,
        processed_at=processed_at,
    )
    sources = _merge_artifact_source(
        _artifact_sources_from_document(existing or {}),
        source,
    )

    if existing and _representative_rank(existing) > _representative_rank(candidate):
        document = _without_mongo_id(existing)
        document.setdefault("id", artifact.id)
        document.setdefault("canonical_key", artifact.canonical_key)
    else:
        document = candidate

    return _artifact_document_with_sources(document, sources, updated_at=processed_at)


def _artifact_source_evidence(
    artifact: ArtifactDocument,
    *,
    raw_file: RawMorgueSource,
    processed_at: str,
) -> dict:
    return {
        "occurrence_id": artifact.occurrence_id,
        "player": raw_file.player,
        "file": raw_file.name,
        "game_ended_at": _game_ended_at_from_file(raw_file.name),
        "url": artifact.source.url,
        "line": artifact.source.line,
        "version": artifact.source.version,
        "item_location": artifact.item_location,
        "item_source": artifact.item_source,
        "source_content_hash": raw_file.content_hash,
        "processed_at": processed_at,
    }


def _artifact_sources_from_document(document: dict) -> list[dict]:
    sources = document.get("sources")
    if isinstance(sources, list):
        return [
            _artifact_source_with_game_time(_without_version_metadata(source))
            for source in sources
            if isinstance(source, dict)
        ]

    source = document.get("source")
    if not isinstance(source, dict):
        return []
    return [
        _artifact_source_with_game_time(
            {
                "occurrence_id": document.get("occurrence_id", document.get("id", "")),
                "player": source.get("player", ""),
                "file": source.get("file", ""),
                "game_ended_at": source.get("game_ended_at") or document.get("latest_game_ended_at"),
                "url": source.get("url"),
                "line": source.get("line"),
                "version": source.get("version") or document.get("source_version"),
                "item_location": document.get("item_location"),
                "item_source": document.get("item_source"),
                "source_content_hash": document.get("source_content_hash", ""),
            }
        )
    ]


def _artifact_source_query(raw_file: RawMorgueSource) -> dict:
    return {
        "$or": [
            {"sources": {"$elemMatch": {"player": raw_file.player, "file": raw_file.name}}},
            {"source.player": raw_file.player, "source.file": raw_file.name},
        ]
    }


def _raw_file_pair_query(raw_files: list[RawMorgueSource]) -> dict:
    pairs = sorted(
        {
            (raw_file.player, raw_file.name)
            for raw_file in raw_files
        }
    )
    if not pairs:
        return {"player": {"$in": []}}
    return {
        "$or": [
            {"player": player, "name": name}
            for player, name in pairs
        ]
    }


def _merge_artifact_source(sources: list[dict], source: dict) -> list[dict]:
    merged: list[dict] = []
    replaced = False
    for existing in sources:
        if existing.get("occurrence_id") == source["occurrence_id"]:
            merged.append(dict(source))
            replaced = True
        else:
            merged.append(dict(existing))
    if not replaced:
        merged.append(dict(source))
    return merged


def _artifact_document_with_sources(
    document: dict,
    sources: list[dict],
    *,
    updated_at: str | None = None,
) -> dict:
    updated = _without_mongo_id(document)
    enriched_sources = [_artifact_source_with_game_time(source) for source in sources]
    updated["sources"] = [dict(source) for source in enriched_sources]
    updated["occurrence_ids"] = [
        str(source["occurrence_id"])
        for source in enriched_sources
        if source.get("occurrence_id")
    ]
    ended_at_values = [
        str(source["game_ended_at"])
        for source in enriched_sources
        if source.get("game_ended_at")
    ]
    updated["latest_game_ended_at"] = max(ended_at_values) if ended_at_values else None
    updated["source_count"] = len(enriched_sources)
    if enriched_sources:
        first_source = dict(enriched_sources[0])
        updated["first_source"] = first_source
        updated["first_discovered_by"] = first_source.get("player", "")
        if not _source_in_sources(updated.get("source"), enriched_sources):
            _apply_representative_source(updated, first_source)
    else:
        updated["first_source"] = None
        updated["first_discovered_by"] = ""
    if updated_at is not None:
        updated["updated_at"] = updated_at
    updated.setdefault("known_seeds", [])
    return updated


def _source_in_sources(source: Any, sources: list[dict]) -> bool:
    if not isinstance(source, dict):
        return False
    source_file = source.get("file")
    source_line = source.get("line")
    return any(
        candidate.get("file") == source_file and candidate.get("line") == source_line
        for candidate in sources
    )


def _public_source_from_evidence(source: dict) -> dict:
    return {
        "player": source.get("player", ""),
        "file": source.get("file", ""),
        "url": source.get("url"),
        "line": source.get("line"),
        "version": source.get("version"),
    }


def _apply_representative_source(document: dict, source: dict) -> None:
    document["source"] = _public_source_from_evidence(source)
    document["occurrence_id"] = source.get("occurrence_id", "")
    document["item_location"] = source.get("item_location")
    document["item_source"] = source.get("item_source")
    document["source_content_hash"] = source.get("source_content_hash", "")
    document["source_version"] = source.get("version")


def _is_source_for_raw_file(source: dict, raw_file: RawMorgueSource) -> bool:
    return (
        source.get("player") == raw_file.player
        and source.get("file") == raw_file.name
    )


def _should_keep_source_evidence(
    source: dict,
    *,
    raw_file: RawMorgueSource,
    document_id: str,
    current_occurrence_canonical_ids: dict[str, str],
) -> bool:
    if not _is_source_for_raw_file(source, raw_file):
        return True
    occurrence_id = str(source.get("occurrence_id", ""))
    return current_occurrence_canonical_ids.get(occurrence_id) == document_id


def _representative_rank(document: dict) -> tuple[int, int, int]:
    source_file = str(document.get("source", {}).get("file", ""))
    source_rank = 1 if source_file.endswith(".txt") else 0
    description_rank = len(document.get("visible_item_description", []))
    evaluation = document.get("evaluation", {})
    score_rank = int(evaluation.get("total", 0)) if isinstance(evaluation, dict) else 0
    return (source_rank, description_rank, score_rank)


def _without_mongo_id(document: dict) -> dict:
    copy = dict(document)
    copy.pop("_id", None)
    copy.pop("parser_version", None)
    copy.pop("scoring_version", None)
    return copy


def _should_process(
    raw_file: RawMorgueSource,
    record: ArtifactProcessingRecord,
) -> bool:
    return (
        record.status != PROCESSING_STATUS_COMPLETED
        or record.content_hash != raw_file.content_hash
        or record.metadata_version != ARTIFACT_METADATA_VERSION
    )


def _raw_morgue_file_record_from_mongo(document: dict) -> RawMorgueSource:
    return RawMorgueSource(
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


def _processing_record_from_mongo(document: dict) -> ArtifactProcessingRecord:
    return ArtifactProcessingRecord(
        player=document["player"],
        name=document["name"],
        content_hash=document.get("content_hash", ""),
        status=document.get("status", ""),
        artifact_count=int(document.get("artifact_count", 0)),
        processed_at=document.get("processed_at"),
        error=document.get("error"),
        metadata_version=document.get("metadata_version", ""),
    )


def _version_metadata_unset() -> dict[str, str]:
    return {"parser_version": "", "scoring_version": ""}


def _without_version_metadata(document: dict) -> dict:
    copy = dict(document)
    copy.pop("parser_version", None)
    copy.pop("scoring_version", None)
    return copy


def _artifact_source_with_game_time(source: dict) -> dict:
    copy = dict(source)
    if not copy.get("game_ended_at"):
        copy["game_ended_at"] = _game_ended_at_from_file(str(copy.get("file", "")))
    return copy


def _game_ended_at_from_file(file_name: str) -> str | None:
    match = MORGUE_FILE_DATE_RE.search(file_name)
    if match is None:
        return None
    value = f"{match.group('date')}{match.group('time')}"
    try:
        ended_at = datetime.strptime(value, "%Y%m%d%H%M%S").replace(tzinfo=UTC)
    except ValueError:
        return None
    return ended_at.isoformat()
