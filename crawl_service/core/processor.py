"""Process persisted raw morgue files into derived artifact documents."""

from __future__ import annotations

from datetime import UTC, datetime

from crawl_service.artifacts.models import (
    ArtifactDocument,
)
from crawl_service.artifacts.extractor import extract_artifact_documents
from crawl_service.morgue.types import MorgueRawText
from crawl_service.core.repository import (
    CrawlArtifactRepository,
    PROCESS_STATUS_FAILED,
    PROCESS_STATUS_PROCESSED,
    RawMorgueFileRecord,
)


CURRENT_PARSER_VERSION = "artifact-parser-v1"
CURRENT_SCORING_VERSION = "artifact-scoring-v1"


class ArtifactProcessor:
    """Build storage-ready artifact documents from one raw morgue text."""

    def documents_from_raw_text(self, raw_text: MorgueRawText) -> list[ArtifactDocument]:
        """Convert one fetched morgue text into sorted storage documents."""
        return extract_artifact_documents(raw_text)


def process_raw_morgue_file(
    repository: CrawlArtifactRepository,
    raw_file: RawMorgueFileRecord,
    *,
    processed_at: str,
    artifact_processor: ArtifactProcessor | None = None,
) -> int:
    """Refresh derived artifact documents from one persisted raw morgue file."""

    try:
        processor = artifact_processor or ArtifactProcessor()
        raw_text = MorgueRawText(
            name=raw_file.name,
            url=raw_file.url,
            extension=raw_file.extension,
            text=raw_file.text,
        )
        documents = processor.documents_from_raw_text(raw_text)
        repository.replace_artifacts_for_source(raw_file.player, raw_file.name, documents)
        repository.save_raw_morgue_file(
            RawMorgueFileRecord(
                player=raw_file.player,
                name=raw_file.name,
                url=raw_file.url,
                extension=raw_file.extension,
                text=raw_file.text,
                content_hash=raw_file.content_hash,
                fetch_status=raw_file.fetch_status,
                process_status=PROCESS_STATUS_PROCESSED,
                fetched_at=raw_file.fetched_at,
                processed_at=processed_at,
                artifact_count=len(documents),
                fetch_error=raw_file.fetch_error,
                process_error=None,
                parser_version=CURRENT_PARSER_VERSION,
                scoring_version=CURRENT_SCORING_VERSION,
            )
        )
        return len(documents)
    except Exception as exc:
        repository.save_raw_morgue_file(
            RawMorgueFileRecord(
                player=raw_file.player,
                name=raw_file.name,
                url=raw_file.url,
                extension=raw_file.extension,
                text=raw_file.text,
                content_hash=raw_file.content_hash,
                fetch_status=raw_file.fetch_status,
                process_status=PROCESS_STATUS_FAILED,
                fetched_at=raw_file.fetched_at,
                processed_at=processed_at,
                artifact_count=0,
                fetch_error=raw_file.fetch_error,
                process_error=str(exc),
                parser_version=raw_file.parser_version,
                scoring_version=raw_file.scoring_version,
            )
        )
        raise


def process_pending_raw_morgue_files(
    repository: CrawlArtifactRepository,
    *,
    limit: int = 100,
    artifact_processor: ArtifactProcessor | None = None,
) -> int:
    """Process fetched raw files whose derived artifact documents are stale or missing."""

    processor = artifact_processor or ArtifactProcessor()
    artifact_count = 0
    raw_files = repository.list_raw_morgue_files_for_processing(
        parser_version=CURRENT_PARSER_VERSION,
        scoring_version=CURRENT_SCORING_VERSION,
        limit=limit,
    )
    for raw_file in raw_files:
        artifact_count += process_raw_morgue_file(
            repository,
            raw_file,
            processed_at=_utc_now(),
            artifact_processor=processor,
        )
    return artifact_count


def _utc_now() -> str:
    return datetime.now(UTC).isoformat()
