"""Artifact document processor entrypoint."""

from __future__ import annotations

from dataclasses import dataclass, field

from arti_parser.extractor import extract_artifact_documents
from arti_parser.models import ArtifactDocument


CURRENT_PARSER_VERSION = "artifact-parser-v1"
CURRENT_SCORING_VERSION = "artifact-scoring-v4"


@dataclass(frozen=True)
class MorgueRawText:
    """Raw morgue text input accepted by the artifact parser."""

    name: str
    url: str | None
    extension: str
    text: str


@dataclass(frozen=True)
class ArtifactProcessor:
    """Build storage-ready artifact documents from one raw morgue text."""

    parser_version: str = field(default=CURRENT_PARSER_VERSION)
    scoring_version: str = field(default=CURRENT_SCORING_VERSION)

    def documents_from_raw_text(self, raw_text: MorgueRawText) -> list[ArtifactDocument]:
        """Convert one fetched morgue text into sorted storage documents."""
        return extract_artifact_documents(raw_text)

    def supported_extensions(self) -> set[str]:
        """Return raw morgue extensions accepted by this processor."""
        return {"txt", "lst"}
