"""Compatibility entrypoint for artifact processing batch execution."""

from __future__ import annotations

from arti_parser.batch import (
    ArtifactProcessingBatchProcessor,
    ArtifactProcessingConfig,
    ArtifactProcessingSummary,
    main,
    processing_summary_message,
)


ArtifactProcessingWorker = ArtifactProcessingBatchProcessor


if __name__ == "__main__":
    main()
