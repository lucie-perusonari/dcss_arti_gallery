"""Observability helpers for crawl service runtime status."""

from __future__ import annotations

import logging
import os
from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class CrawlServicePassSummary:
    """Raw ingest summary for one worker loop pass."""

    crawl: Any
    duration_seconds: float


def configure_logging(level_name: str | None = None) -> None:
    """Configure process-wide logging for crawl service commands."""

    configured = (level_name or os.environ.get("CRAWL_LOG_LEVEL") or "INFO").upper()
    level = getattr(logging, configured, logging.INFO)
    logging.basicConfig(
        level=level,
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    )


def get_logger(name: str) -> logging.Logger:
    return logging.getLogger(name)


def crawl_pass_message(summary: CrawlServicePassSummary) -> str:
    crawl = summary.crawl
    return (
        "Crawl pass complete: "
        f"{crawl.users_seen} users seen, "
        f"{crawl.users_scanned} users scanned, "
        f"{crawl.users_skipped_by_date} users skipped by date, "
        f"{crawl.users_skipped_unchanged} users skipped unchanged, "
        f"{crawl.users_failed} users failed, "
        f"{crawl.files_processed} files stored, "
        f"{crawl.files_skipped_existing_raw} files already stored, "
        f"duration={summary.duration_seconds:.2f}s."
    )
