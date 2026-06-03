"""Artifact domain data types."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class ArtifactRawTextInput:
    """Parser-ready raw text owned by the artifact domain."""

    name: str
    url: str
    extension: str
    text: str


@dataclass(frozen=True)
class ArtifactRawInfo:
    """Raw text and lightly indexed fields for one visible randart block."""

    source_name: str | None
    source_url: str | None
    line_no: int
    raw_text_block: str
    artifact_name: str
    item_location: str | None
    item_source: str | None
    visible_item_description: list[str]
    visible_description_labels: list[str]
    bracket_subtype: str | None


@dataclass(frozen=True)
class ArtifactAttribute:
    """One parsed token from the artifact property braces."""

    token: str
    key: str
    value: int | bool | None
    description: str | None


@dataclass(frozen=True)
class ArtifactInfo:
    """Structured item information parsed from ArtifactRawInfo."""

    raw_info: ArtifactRawInfo
    display_name: str
    base_item: str
    enchantment: int | None
    attributes: list[ArtifactAttribute]
    base_subtype: str | None


@dataclass(frozen=True)
class RandomArtifact:
    """Document-friendly artifact classification result."""

    artifact_info: ArtifactInfo
    name: str
    base_item: str
    enchantment: int | None
    brand: str | None
    base_subtype: str | None
    item_class: str
    item_subtype: str
    weapon_subtype: str | None
    armour_slot: str | None
    jewellery_slot: str | None
    all_attributes: list[str]
    base_attributes: list[str]
    random_attributes: list[str]
    all_attribute_text: str
    base_attribute_text: str
    random_attribute_text: str
