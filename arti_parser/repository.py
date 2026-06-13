"""MongoDB repository for artifact read-model regeneration."""

from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Any, Protocol

from arti_parser.models import ArtifactDocument


DEFAULT_MONGO_URI = "mongodb://localhost:27017"
DEFAULT_MONGO_DATABASE = "dcss_arti_gallery"
DEFAULT_MONGO_RAW_FILES_COLLECTION = "raw_morgue_files"
DEFAULT_MONGO_ARTIFACTS_COLLECTION = "artifacts"
DEFAULT_MONGO_ARTIFACT_PROCESSING_COLLECTION = "artifact_processing_files"
FETCH_STATUS_FETCHED = "fetched"
PROCESSING_STATUS_COMPLETED = "completed"
PROCESSING_STATUS_FAILED = "failed"


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
    parser_version: str
    scoring_version: str
    status: str
    artifact_count: int = 0
    processed_at: str | None = None
    error: str | None = None

    def to_dict(self) -> dict:
        return {
            "player": _player_key(self.player),
            "name": self.name,
            "content_hash": self.content_hash,
            "parser_version": self.parser_version,
            "scoring_version": self.scoring_version,
            "status": self.status,
            "artifact_count": self.artifact_count,
            "processed_at": self.processed_at,
            "error": self.error,
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
        parser_version: str,
        scoring_version: str,
        limit: int,
        scan_batch_size: int,
    ) -> list[RawMorgueSource]:
        ...

    def save_artifacts_for_raw_file(
        self,
        *,
        raw_file: RawMorgueSource,
        artifacts: list[ArtifactDocument],
        parser_version: str,
        scoring_version: str,
        processed_at: str,
    ) -> ArtifactSaveResult:
        ...

    def save_processing_failure(
        self,
        *,
        raw_file: RawMorgueSource,
        parser_version: str,
        scoring_version: str,
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
        parser_version: str,
        scoring_version: str,
        limit: int,
        scan_batch_size: int,
    ) -> list[RawMorgueSource]:
        if self.raw_file_collection is None or limit < 1:
            return []

        pending: list[RawMorgueSource] = []
        scan_batch_size = max(scan_batch_size, 1)
        cursor = self.raw_file_collection.find(
            {"fetch_status": FETCH_STATUS_FETCHED},
            {
                "_id": 0,
                "player": 1,
                "name": 1,
                "url": 1,
                "extension": 1,
                "text": 1,
                "content_hash": 1,
                "fetch_status": 1,
                "fetched_at": 1,
                "fetch_error": 1,
            },
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
                        parser_version=parser_version,
                        scoring_version=scoring_version,
                    )
                )
                if len(pending) >= limit:
                    return pending[:limit]
                batch = []

        if batch:
            pending.extend(
                self._pending_from_batch(
                    batch,
                    parser_version=parser_version,
                    scoring_version=scoring_version,
                )
            )
        return pending[:limit]

    def save_artifacts_for_raw_file(
        self,
        *,
        raw_file: RawMorgueSource,
        artifacts: list[ArtifactDocument],
        parser_version: str,
        scoring_version: str,
        processed_at: str,
    ) -> ArtifactSaveResult:
        artifact_ids = [artifact.id for artifact in artifacts]
        stale_deleted = self._delete_stale_artifacts(raw_file, artifact_ids)
        if self.artifacts_collection is not None and artifacts:
            operations = [
                _update_one(
                    {"id": artifact.id},
                    {
                        "$set": _artifact_mongo_document(
                            artifact,
                            raw_file=raw_file,
                            parser_version=parser_version,
                            scoring_version=scoring_version,
                        )
                    },
                    upsert=True,
                )
                for artifact in artifacts
            ]
            self.artifacts_collection.bulk_write(operations, ordered=False)

        self._save_processing_record(
            ArtifactProcessingRecord(
                player=raw_file.player,
                name=raw_file.name,
                content_hash=raw_file.content_hash,
                parser_version=parser_version,
                scoring_version=scoring_version,
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
        parser_version: str,
        scoring_version: str,
        processed_at: str,
        error: str,
    ) -> None:
        self._save_processing_record(
            ArtifactProcessingRecord(
                player=raw_file.player,
                name=raw_file.name,
                content_hash=raw_file.content_hash,
                parser_version=parser_version,
                scoring_version=scoring_version,
                status=PROCESSING_STATUS_FAILED,
                artifact_count=0,
                processed_at=processed_at,
                error=error,
            )
        )

    def _pending_from_batch(
        self,
        batch: list[RawMorgueSource],
        *,
        parser_version: str,
        scoring_version: str,
    ) -> list[RawMorgueSource]:
        processing_records = self._processing_records_for_raw_files(batch)
        pending: list[RawMorgueFileRecord] = []
        for raw_file in batch:
            record = processing_records.get((_player_key(raw_file.player), raw_file.name))
            if record is None or _should_process(raw_file, record, parser_version, scoring_version):
                pending.append(raw_file)
        return pending

    def _processing_records_for_raw_files(
        self,
        raw_files: list[RawMorgueSource],
    ) -> dict[tuple[str, str], ArtifactProcessingRecord]:
        if self.processing_collection is None or not raw_files:
            return {}
        players = sorted({_player_key(raw_file.player) for raw_file in raw_files})
        names = sorted({raw_file.name for raw_file in raw_files})
        documents = self.processing_collection.find(
            {
                "player": {"$in": players},
                "name": {"$in": names},
            }
        )
        records = [_processing_record_from_mongo(document) for document in documents]
        return {(_player_key(record.player), record.name): record for record in records}

    def _delete_stale_artifacts(
        self,
        raw_file: RawMorgueSource,
        current_artifact_ids: list[str],
    ) -> int:
        if self.artifacts_collection is None:
            return 0
        selector: dict[str, Any] = {
            "source.player": _player_key(raw_file.player),
            "source.file": raw_file.name,
        }
        if current_artifact_ids:
            selector["id"] = {"$nin": current_artifact_ids}
        result = self.artifacts_collection.delete_many(selector)
        return int(getattr(result, "deleted_count", 0))

    def _save_processing_record(self, record: ArtifactProcessingRecord) -> None:
        if self.processing_collection is None:
            return
        document = record.to_dict()
        self.processing_collection.update_one(
            {"player": document["player"], "name": document["name"]},
            {"$set": document},
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
    parser_version: str,
    scoring_version: str,
) -> dict:
    document = artifact.to_dict()
    document["source"]["player"] = _player_key(raw_file.player)
    document["source_content_hash"] = raw_file.content_hash
    document["parser_version"] = parser_version
    document["scoring_version"] = scoring_version
    return document


def _should_process(
    raw_file: RawMorgueSource,
    record: ArtifactProcessingRecord,
    parser_version: str,
    scoring_version: str,
) -> bool:
    return (
        record.status != PROCESSING_STATUS_COMPLETED
        or record.content_hash != raw_file.content_hash
        or record.parser_version != parser_version
        or record.scoring_version != scoring_version
    )


def _update_one(selector: dict, update: dict, *, upsert: bool):
    from pymongo import UpdateOne

    return UpdateOne(selector, update, upsert=upsert)


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
        parser_version=document.get("parser_version", ""),
        scoring_version=document.get("scoring_version", ""),
        status=document.get("status", ""),
        artifact_count=int(document.get("artifact_count", 0)),
        processed_at=document.get("processed_at"),
        error=document.get("error"),
    )


def _player_key(player: str) -> str:
    return player.strip().lower()
