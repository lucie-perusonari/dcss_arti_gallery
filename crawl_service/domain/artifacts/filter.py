"""Filters for artifacts that should not enter the gallery repository."""

from __future__ import annotations

from crawl_service.domain.artifacts.types import ArtifactInfo
from crawl_service.domain.constants import ENCHANTMENT_PREFIX_RE, UNRANDART_NAME_KEYS


def is_random_artifact_info(artifact_info: ArtifactInfo) -> bool:
    """Return False for fixed unrandarts and plain magic item candidates."""

    name_key = _identity_key(artifact_info.display_name)
    if name_key in UNRANDART_NAME_KEYS:
        return False
    return not _is_plain_magic_item(artifact_info)


def _is_plain_magic_item(artifact_info: ArtifactInfo) -> bool:
    if '"' in artifact_info.display_name:
        return False
    if not artifact_info.base_subtype:
        return False
    return _identity_key(artifact_info.display_name) == _normalize_key(
        artifact_info.base_subtype
    )


def _identity_key(name: str) -> str:
    name = name.strip().removeprefix("cursed ").strip()
    name = ENCHANTMENT_PREFIX_RE.sub("", name)
    return _normalize_key(name)


def _normalize_key(value: str) -> str:
    return " ".join(value.casefold().split())
