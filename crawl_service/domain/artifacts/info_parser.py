"""Artifact identity and property parsing."""

from __future__ import annotations


from crawl_service.domain.artifacts.types import ArtifactAttribute, ArtifactInfo, ArtifactRawInfo
from crawl_service.domain.constants import (
    ARTIFACT_DESCRIPTION_RE,
    ARTIFACT_ENCHANTMENT_RE,
    ARTIFACT_PROPERTY_BLOCK_RE,
    INTERNAL_PROPERTY_TOKEN_KEYS,
    MULTI_WORD_PROPERTY_TOKENS,
    SIGNED_PROPERTY_RE,
)


def parse_artifact_info(raw_info: ArtifactRawInfo) -> ArtifactInfo:
    """Parse a raw randart block into item identity and visible attributes."""

    item_text = _strip_property_block(raw_info.artifact_name)
    display_name = _clean_display_name(item_text)
    enchantment, base_text = _split_enchantment(display_name)
    attributes = [
        _parse_attribute_token(token, _description_for_token(token, raw_info))
        for token in _property_tokens(raw_info.artifact_name)
        if token.casefold() not in INTERNAL_PROPERTY_TOKEN_KEYS
    ]
    return ArtifactInfo(
        raw_info=raw_info,
        display_name=display_name,
        base_item=_base_item_from_name(base_text, raw_info.bracket_subtype),
        enchantment=enchantment,
        attributes=attributes,
        base_subtype=raw_info.bracket_subtype,
    )


def _strip_property_block(artifact_name: str) -> str:
    return ARTIFACT_PROPERTY_BLOCK_RE.sub("", artifact_name).strip()


def _clean_display_name(item_text: str) -> str:
    return item_text.removeprefix("the ").strip()


def _split_enchantment(display_name: str) -> tuple[int | None, str]:
    match = ARTIFACT_ENCHANTMENT_RE.match(display_name)
    if not match:
        return None, display_name
    return int(match.group("value")), display_name[match.end() :].strip()


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


def _parse_attribute_token(token: str, description: str | None) -> ArtifactAttribute:
    key, value = _attribute_key_value(token)
    return ArtifactAttribute(
        token=token,
        key=key,
        value=value,
        description=description,
    )


def _attribute_key_value(token: str) -> tuple[str, int | bool | None]:
    signed_match = SIGNED_PROPERTY_RE.match(token)
    if signed_match:
        return signed_match.group("key"), int(signed_match.group("value"))

    for key in ("rF", "rC", "rN", "Will"):
        if token.startswith(key) and set(token[len(key) :]) <= {"+", "-"}:
            suffix = token[len(key) :]
            if suffix:
                sign = -1 if suffix[0] == "-" else 1
                return key, sign * len(suffix)

    for key in ("RegenMP", "Regen"):
        if token == f"{key}+":
            return key, True

    return token, True


def _description_for_token(token: str, raw_info: ArtifactRawInfo) -> str | None:
    token_key, _ = _attribute_key_value(token)
    for description in raw_info.visible_item_description:
        match = ARTIFACT_DESCRIPTION_RE.match(description)
        if not match:
            continue
        label = match.group("label").strip()
        label_key, _ = _attribute_key_value(label)
        if label == token or label_key == token_key:
            return description
    return None


def _base_item_from_name(base_text: str, bracket_subtype: str | None) -> str:
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
