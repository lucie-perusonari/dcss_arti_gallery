"""Artifact name, property, and randart eligibility parsing."""

from __future__ import annotations

from arti_parser.constants import (
    ARTIFACT_DESCRIPTION_RE,
    ARTIFACT_ENCHANTMENT_RE,
    ARTIFACT_PROPERTY_BLOCK_RE,
    ENCHANTMENT_PREFIX_RE,
    INTERNAL_PROPERTY_TOKEN_KEYS,
    MULTI_WORD_PROPERTY_TOKENS,
    SIGNED_PROPERTY_RE,
    UNRANDART_NAME_KEYS,
)
from arti_parser.models import ArtifactDocumentAttribute

RESISTANCE_STEP_KEYS = {"rF", "rC", "rN", "Will", "rElec", "rPois", "rCorr"}
NUMERIC_STEP_KEYS = {"Stlth"}
BOOLEAN_PLUS_KEYS = {"RegenMP", "Regen"}
EXCLUDED_RANDOM_ARTIFACT_NAME_KEYS = {"sprint"}
ITEM_STATUS_PREFIXES = {"chaotic", "choatic", "cursed"}
STEP_PROPERTY_KEYS_BY_LENGTH = tuple(
    sorted((*RESISTANCE_STEP_KEYS, *NUMERIC_STEP_KEYS), key=len, reverse=True)
)
MULTI_WORD_PROPERTY_TOKENS_BY_LENGTH = tuple(
    sorted(
        MULTI_WORD_PROPERTY_TOKENS,
        key=lambda value: len(value.split()),
        reverse=True,
    )
)


def artifact_display_name(artifact_name: str) -> str:
    return _strip_item_status_prefixes(
        _strip_property_block(artifact_name).removeprefix("the ").strip()
    )


def normalized_artifact_name(artifact_name: str) -> str:
    display_name = artifact_display_name(artifact_name)
    property_block = _property_block(artifact_name)
    article = "the " if artifact_name.strip().casefold().startswith("the ") else ""
    return f"{article}{display_name}{property_block}".strip()


def artifact_status_prefixes(artifact_name: str) -> list[str]:
    return _item_status_prefixes(
        _strip_property_block(artifact_name).removeprefix("the ").strip()
    )


def artifact_enchantment_and_base_text(display_name: str) -> tuple[int | None, str]:
    match = ARTIFACT_ENCHANTMENT_RE.match(display_name)
    if not match:
        return None, display_name
    return int(match.group("value")), display_name[match.end() :].strip()


def artifact_base_item(base_text: str, bracket_subtype: str | None) -> str:
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
    descriptions = _parsed_descriptions(visible_item_description)
    attributes: list[ArtifactDocumentAttribute] = []
    for token in _property_tokens(artifact_name):
        if token.casefold() in INTERNAL_PROPERTY_TOKEN_KEYS:
            continue
        key, value = parse_property_token(token)
        attributes.append(
            ArtifactDocumentAttribute(
                token=token,
                key=key,
                value=value,
                description=_description_for_token(token, key, value, descriptions),
            )
        )
    return attributes


def is_random_artifact(
    *,
    display_name: str,
    base_subtype: str | None,
    status_prefixes: list[str] | None = None,
) -> bool:
    name_key = _identity_key(display_name)
    if not status_prefixes:
        if name_key in UNRANDART_NAME_KEYS:
            return False
        if name_key in EXCLUDED_RANDOM_ARTIFACT_NAME_KEYS:
            return False
    return not _is_plain_magic_item(display_name, base_subtype)


def parse_property_token(token: str) -> tuple[str, int | bool | None]:
    signed_match = SIGNED_PROPERTY_RE.match(token)
    if signed_match:
        return signed_match.group("key"), int(signed_match.group("value"))

    for key in STEP_PROPERTY_KEYS_BY_LENGTH:
        suffix = token[len(key) :]
        if token.startswith(key) and suffix and set(suffix) <= {"+", "-"}:
            sign = -1 if suffix[0] == "-" else 1
            return key, sign * len(suffix)

    for key in BOOLEAN_PLUS_KEYS:
        if token == f"{key}+":
            return key, True

    return token, True


def _strip_property_block(artifact_name: str) -> str:
    return ARTIFACT_PROPERTY_BLOCK_RE.sub("", artifact_name).strip()


def _property_block(artifact_name: str) -> str:
    match = ARTIFACT_PROPERTY_BLOCK_RE.search(artifact_name.strip())
    return f" {match.group(0)}" if match else ""


def _strip_item_status_prefixes(display_name: str) -> str:
    words = display_name.strip().split()
    while words and words[0].casefold() in ITEM_STATUS_PREFIXES:
        words.pop(0)
    return " ".join(words)


def _item_status_prefixes(display_name: str) -> list[str]:
    prefixes: list[str] = []
    words = display_name.strip().split()
    while words and words[0].casefold() in ITEM_STATUS_PREFIXES:
        prefixes.append(words.pop(0).casefold())
    return prefixes


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
        if token is None:
            tokens.append(words[index])
            index += 1
        else:
            tokens.append(token)
            index += len(token.split())
    return tokens


def _multi_word_token_at(words: list[str], index: int) -> str | None:
    for token in MULTI_WORD_PROPERTY_TOKENS_BY_LENGTH:
        token_words = token.split()
        if words[index : index + len(token_words)] == token_words:
            return token
    return None


def _parsed_descriptions(
    visible_item_description: list[str],
) -> list[tuple[str, str, int | bool | None, str]]:
    descriptions: list[tuple[str, str, int | bool | None, str]] = []
    for description in visible_item_description:
        match = ARTIFACT_DESCRIPTION_RE.match(description)
        if not match:
            continue
        label = match.group("label").strip()
        label_key, label_value = parse_property_token(label)
        descriptions.append((label, label_key, label_value, description))
    return descriptions


def _description_for_token(
    token: str,
    token_key: str,
    token_value: int | bool | None,
    descriptions: list[tuple[str, str, int | bool | None, str]],
) -> str | None:
    for label, label_key, label_value, description in descriptions:
        if label == token or (label_key == token_key and label_value == token_value):
            return description
    return None


def _is_plain_magic_item(display_name: str, base_subtype: str | None) -> bool:
    if '"' in display_name:
        return False
    if not base_subtype:
        return False
    return _identity_key(display_name) == _normalize_key(base_subtype)


def _identity_key(name: str) -> str:
    name = _strip_item_status_prefixes(name)
    name = ENCHANTMENT_PREFIX_RE.sub("", name)
    return _normalize_key(name)


def _normalize_key(value: str) -> str:
    return " ".join(value.casefold().split())
