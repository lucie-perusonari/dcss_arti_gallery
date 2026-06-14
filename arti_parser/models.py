"""Canonical MongoDB artifact document models."""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict


class ArtifactDocumentSource(BaseModel):
    """Original morgue source metadata for an artifact document."""

    model_config = ConfigDict(frozen=True)

    player: str
    file: str
    url: str | None
    line: int
    version: str | None = None


class ArtifactDocumentAttribute(BaseModel):
    """Parsed artifact attribute token data stored in MongoDB."""

    model_config = ConfigDict(frozen=True)

    token: str
    key: str
    value: int | bool | None
    description: str | None


class ArtifactDocumentEvaluation(BaseModel):
    """Document-owned shape for an artifact evaluation result."""

    model_config = ConfigDict(frozen=True)

    total: int
    practical_score: int | None = None
    rarity_score: int = 0
    offense: int
    defense: int
    utility: int
    penalty: int
    base_fit: int
    grade: str
    luxury_grade: str | None = None


class ArtifactDocument(BaseModel):
    """Canonical artifact document stored by arti_parser."""

    model_config = ConfigDict(frozen=True)

    id: str
    occurrence_id: str
    canonical_key: str
    name: str
    base_item: str
    base_subtype: str | None
    item_class: str
    item_subtype: str
    weapon_subtype: str | None
    armour_subtype: str | None = None
    armour_slot: str | None
    jewellery_slot: str | None
    enchantment: int | None
    brand: str | None
    source: ArtifactDocumentSource
    attributes: list[ArtifactDocumentAttribute]
    ignored_attributes: list[ArtifactDocumentAttribute] = []
    all_attributes: list[str]
    base_attributes: list[str]
    random_attributes: list[str]
    all_attribute_text: str
    base_attribute_text: str
    random_attribute_text: str
    evaluation: ArtifactDocumentEvaluation
    visible_item_description: list[str]
    visible_description_labels: list[str]
    raw_text_block: str
    item_location: str | None
    item_source: str | None

    def to_dict(self) -> dict:
        return self.model_dump()
