"""Batch processor for rebuilding artifact read models from stored raw source."""

from __future__ import annotations

import argparse
import logging
import os
import time
from dataclasses import dataclass
from datetime import UTC, datetime

from arti_parser.processor import (
    ArtifactProcessor,
    MorgueRawText,
)
from arti_parser.repository import (
    ArtifactProcessingRepository,
    RawMorgueSource,
    repository_from_env,
)


DEFAULT_BATCH_SIZE = 100
DEFAULT_SCAN_BATCH_SIZE = 500
DEFAULT_LOOP_INTERVAL_SECONDS = 60.0


@dataclass(frozen=True)
class ArtifactProcessingConfig:
    batch_size: int = DEFAULT_BATCH_SIZE
    scan_batch_size: int = DEFAULT_SCAN_BATCH_SIZE


@dataclass(frozen=True)
class ArtifactProcessingSummary:
    raw_files_seen: int = 0
    raw_files_processed: int = 0
    raw_files_failed: int = 0
    artifacts_written: int = 0
    stale_artifacts_deleted: int = 0


class ArtifactProcessingBatchProcessor:
    """Regenerate artifact documents from fetched raw morgue records."""

    def __init__(
        self,
        repository: ArtifactProcessingRepository,
        config: ArtifactProcessingConfig | None = None,
        processor: ArtifactProcessor | None = None,
    ) -> None:
        self.repository = repository
        self.config = config or ArtifactProcessingConfig()
        self.processor = processor or ArtifactProcessor()
        self.logger = logging.getLogger(__name__)

    def process_batch(self, limit: int | None = None) -> ArtifactProcessingSummary:
        raw_files = self.repository.list_pending_raw_files(
            limit=limit or self.config.batch_size,
            scan_batch_size=self.config.scan_batch_size,
        )
        summary = ArtifactProcessingSummary(raw_files_seen=len(raw_files))
        for raw_file in raw_files:
            summary = _add_summary(summary, self._process_raw_file(raw_file))
        return summary

    def _process_raw_file(self, raw_file: RawMorgueSource) -> ArtifactProcessingSummary:
        try:
            artifacts = self.processor.documents_from_raw_text(
                MorgueRawText(
                    name=raw_file.name,
                    url=raw_file.url,
                    extension=raw_file.extension,
                    text=raw_file.text,
                )
            )
            result = self.repository.save_artifacts_for_raw_file(
                raw_file=raw_file,
                artifacts=artifacts,
                processed_at=_utc_now(),
            )
        except Exception as exc:
            self.repository.save_processing_failure(
                raw_file=raw_file,
                processed_at=_utc_now(),
                error=str(exc),
            )
            self.logger.info(
                "Artifact processing failed for %s/%s: %s",
                raw_file.player,
                raw_file.name,
                exc,
            )
            return ArtifactProcessingSummary(raw_files_failed=1)

        return ArtifactProcessingSummary(
            raw_files_processed=1,
            artifacts_written=result.artifact_count,
            stale_artifacts_deleted=result.stale_deleted,
        )


def processing_summary_message(summary: ArtifactProcessingSummary) -> str:
    return (
        "Artifact processing batch complete: "
        f"{summary.raw_files_seen} raw files seen, "
        f"{summary.raw_files_processed} processed, "
        f"{summary.raw_files_failed} failed, "
        f"{summary.artifacts_written} artifacts written, "
        f"{summary.stale_artifacts_deleted} stale artifacts deleted."
    )


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Regenerate artifact documents from MongoDB raw_morgue_files."
    )
    parser.add_argument("--once", action="store_true", default=_env_bool("ONCE", False))
    parser.add_argument("--limit", type=int, default=_env_int("PROCESS_LIMIT"))
    parser.add_argument("--batch-size", type=int, default=_env_int("BATCH_SIZE", DEFAULT_BATCH_SIZE))
    parser.add_argument(
        "--scan-batch-size",
        type=int,
        default=_env_int("SCAN_BATCH_SIZE", DEFAULT_SCAN_BATCH_SIZE),
    )
    parser.add_argument(
        "--loop-interval-seconds",
        type=float,
        default=_env_float("PROCESS_LOOP_INTERVAL_SECONDS", DEFAULT_LOOP_INTERVAL_SECONDS),
    )
    args = parser.parse_args()

    _configure_logging()
    batch_processor = ArtifactProcessingBatchProcessor(
        repository_from_env(),
        config=ArtifactProcessingConfig(
            batch_size=args.batch_size,
            scan_batch_size=args.scan_batch_size,
        ),
    )
    while True:
        summary = batch_processor.process_batch(limit=args.limit)
        logging.getLogger(__name__).info(processing_summary_message(summary))
        if args.once or summary.raw_files_seen == 0:
            break
        time.sleep(max(args.loop_interval_seconds, 0.0))


def _add_summary(
    left: ArtifactProcessingSummary,
    right: ArtifactProcessingSummary,
) -> ArtifactProcessingSummary:
    return ArtifactProcessingSummary(
        raw_files_seen=left.raw_files_seen + right.raw_files_seen,
        raw_files_processed=left.raw_files_processed + right.raw_files_processed,
        raw_files_failed=left.raw_files_failed + right.raw_files_failed,
        artifacts_written=left.artifacts_written + right.artifacts_written,
        stale_artifacts_deleted=left.stale_artifacts_deleted + right.stale_artifacts_deleted,
    )


def _utc_now() -> str:
    return datetime.now(UTC).isoformat()


def _configure_logging() -> None:
    level_name = (os.environ.get("ARTIFACT_PROCESS_LOG_LEVEL") or "INFO").upper()
    level = getattr(logging, level_name, logging.INFO)
    logging.basicConfig(
        level=level,
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    )


def _env_bool(name: str, default: bool) -> bool:
    value = os.environ.get(name)
    if value is None:
        return default
    return value.lower() in {"1", "true", "yes", "on"}


def _env_int(name: str, default: int | None = None) -> int | None:
    value = os.environ.get(name)
    return default if value is None else int(value)


def _env_float(name: str, default: float) -> float:
    value = os.environ.get(name)
    return default if value is None else float(value)


if __name__ == "__main__":
    main()
