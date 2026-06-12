"""Filters for artifacts that should not enter the gallery repository."""

from __future__ import annotations

from crawl_service.artifacts.constants import ENCHANTMENT_PREFIX_RE
from crawl_service.artifacts.constants import UNRANDART_NAME_KEYS

EXCLUDED_RANDOM_ARTIFACT_NAME_KEYS = {"sprint"}


def is_random_artifact(
    *,
    display_name: str,
    base_subtype: str | None,
) -> bool:
    """Return False for fixed unrandarts and plain magic item candidates."""

    name_key = _identity_key(display_name)
    if name_key in UNRANDART_NAME_KEYS:
        return False
    if name_key in EXCLUDED_RANDOM_ARTIFACT_NAME_KEYS:
        return False
    return not _is_plain_magic_item(display_name, base_subtype)


def _is_plain_magic_item(display_name: str, base_subtype: str | None) -> bool:
    if '"' in display_name:
        return False
    if not base_subtype:
        return False
    return _identity_key(display_name) == _normalize_key(base_subtype)


def _identity_key(name: str) -> str:
    name = name.strip().removeprefix("cursed ").strip()
    name = ENCHANTMENT_PREFIX_RE.sub("", name)
    return _normalize_key(name)


def _normalize_key(value: str) -> str:
    return " ".join(value.casefold().split())
