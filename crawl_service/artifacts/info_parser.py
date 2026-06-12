"""Artifact identity and property parsing helpers."""

from __future__ import annotations

from crawl_service.artifacts.property_parser import parse_property_token
from crawl_service.artifacts.constants import (
    ARTIFACT_DESCRIPTION_RE,
    ARTIFACT_ENCHANTMENT_RE,
    ARTIFACT_PROPERTY_BLOCK_RE,
    INTERNAL_PROPERTY_TOKEN_KEYS,
    MULTI_WORD_PROPERTY_TOKENS,
)
from crawl_service.artifacts.models import ArtifactDocumentAttribute


def artifact_display_name(artifact_name: str) -> str:
    """Return the display name without the leading article and property block."""

    return _strip_property_block(artifact_name).removeprefix("the ").strip()


def artifact_enchantment_and_base_text(display_name: str) -> tuple[int | None, str]:
    """Return enchantment and remaining base-name text from a display name."""

    match = ARTIFACT_ENCHANTMENT_RE.match(display_name)
    if not match:
        return None, display_name
    return int(match.group("value")), display_name[match.end() :].strip()


def artifact_base_item(base_text: str, bracket_subtype: str | None) -> str:
    """Return the normalized base item name."""

    if bracket_subtype:
        if bracket_subtype.startswith("ring of "):
            return "ring"
        if bracket_subtype.startswith("amulet of "):
            return "amulet"
        if " staff" in bracket_subtype or bracket_subtype.startswith("staff of "):
            return "staff"
        if "talisman" in bracket_subtype:
            return "talisman"

    for separator in (' "', " of "):
        if separator in base_text:
            base_text = base_text.split(separator, 1)[0]
            break
    return base_text.strip()


def artifact_attributes(
    artifact_name: str,
    visible_item_description: list[str],
) -> list[ArtifactDocumentAttribute]:
    """Return document attribute values parsed from the artifact property block."""

    return [
        _parse_attribute_token(
            token,
            _description_for_token(token, visible_item_description),
        )
        for token in _property_tokens(artifact_name)
        if token.casefold() not in INTERNAL_PROPERTY_TOKEN_KEYS
    ]


def _strip_property_block(artifact_name: str) -> str:
    return ARTIFACT_PROPERTY_BLOCK_RE.sub("", artifact_name).strip()


def _property_tokens(artifact_name: str) -> list[str]:
    match = ARTIFACT_PROPERTY_BLOCK_RE.search(artifact_name.strip())
    if not match:
        return []

    tokens: list[str] = []
    for group in match.group("properties").split(","):
        tokens.extend(_property_group_tokens(group.strip()))
    return tokens


def _property_group_tokens(group: str) -> list[str]:
    if not group:
        return []
    if group in MULTI_WORD_PROPERTY_TOKENS:
        return [group]

    words = [word for word in group.split() if word]
    tokens: list[str] = []
    index = 0
    while index < len(words):
        token = _multi_word_token_at(words, index)
        if token is not None:
            tokens.append(token)
            index += len(token.split())
            continue
        tokens.append(words[index])
        index += 1
    return tokens


def _multi_word_token_at(words: list[str], index: int) -> str | None:
    for token in sorted(
        MULTI_WORD_PROPERTY_TOKENS,
        key=lambda value: len(value.split()),
        reverse=True,
    ):
        token_words = token.split()
        if words[index : index + len(token_words)] == token_words:
            return token
    return None


def _parse_attribute_token(
    token: str,
    description: str | None,
) -> ArtifactDocumentAttribute:
    key, value = parse_property_token(token)
    return ArtifactDocumentAttribute(
        token=token,
        key=key,
        value=value,
        description=description,
    )


def _description_for_token(
    token: str,
    visible_item_description: list[str],
) -> str | None:
    token_key, _ = parse_property_token(token)
    for description in visible_item_description:
        match = ARTIFACT_DESCRIPTION_RE.match(description)
        if not match:
            continue
        label = match.group("label").strip()
        label_key, _ = parse_property_token(label)
        if label == token or label_key == token_key:
            return description
    return None
