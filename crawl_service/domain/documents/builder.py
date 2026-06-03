"""Build canonical MongoDB artifact documents."""

from __future__ import annotations

import hashlib
from typing import Any

from pydantic import BaseModel, ConfigDict

from crawl_service.domain.constants import ARTIFACT_ID_SLUG_RE, PLAYER_RE


class ArtifactDocumentSource(BaseModel):
    """Original morgue source metadata for an artifact document."""

    model_config = ConfigDict(frozen=True)

    player: str
    file: str
    url: str | None
    line: int


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
    """Canonical artifact document stored by crawl_service."""

    model_config = ConfigDict(frozen=True)

    id: str
    name: str
    base_item: str
    base_subtype: str | None
    item_class: str
    item_subtype: str
    weapon_subtype: str | None
    armour_slot: str | None
    jewellery_slot: str | None
    enchantment: int | None
    brand: str | None
    source: ArtifactDocumentSource
    attributes: list[ArtifactDocumentAttribute]
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


def build_artifact_document(
    artifact: Any,
    evaluation: Any,
) -> ArtifactDocument:
    """Combine a random artifact and evaluation-like value into a storage document."""

    raw_info = artifact.artifact_info.raw_info
    source_file = raw_info.source_name or ""
    return ArtifactDocument(
        id=_artifact_id(artifact),
        name=artifact.name,
        base_item=artifact.base_item,
        base_subtype=artifact.base_subtype,
        item_class=artifact.item_class,
        item_subtype=artifact.item_subtype,
        weapon_subtype=artifact.weapon_subtype,
        armour_slot=artifact.armour_slot,
        jewellery_slot=artifact.jewellery_slot,
        enchantment=artifact.enchantment,
        brand=artifact.brand,
        source=ArtifactDocumentSource(
            player=_player_from_source(source_file),
            file=source_file,
            url=raw_info.source_url,
            line=raw_info.line_no,
        ),
        attributes=[
            ArtifactDocumentAttribute(
                token=attribute.token,
                key=attribute.key,
                value=attribute.value,
                description=attribute.description,
            )
            for attribute in artifact.artifact_info.attributes
        ],
        all_attributes=artifact.all_attributes,
        base_attributes=artifact.base_attributes,
        random_attributes=artifact.random_attributes,
        all_attribute_text=artifact.all_attribute_text,
        base_attribute_text=artifact.base_attribute_text,
        random_attribute_text=artifact.random_attribute_text,
        evaluation=_document_evaluation(evaluation),
        visible_item_description=raw_info.visible_item_description,
        visible_description_labels=raw_info.visible_description_labels,
        raw_text_block=raw_info.raw_text_block,
        item_location=raw_info.item_location,
        item_source=raw_info.item_source,
    )


def _document_evaluation(evaluation: Any) -> ArtifactDocumentEvaluation:
    if isinstance(evaluation, ArtifactDocumentEvaluation):
        return evaluation
    if isinstance(evaluation, dict):
        return ArtifactDocumentEvaluation.model_validate(evaluation)
    return ArtifactDocumentEvaluation(
        total=evaluation.total,
        practical_score=evaluation.practical_score,
        rarity_score=evaluation.rarity_score,
        offense=evaluation.offense,
        defense=evaluation.defense,
        utility=evaluation.utility,
        penalty=evaluation.penalty,
        base_fit=evaluation.base_fit,
        grade=evaluation.grade,
        luxury_grade=evaluation.luxury_grade,
    )


def _artifact_id(artifact: Any) -> str:
    raw_info = artifact.artifact_info.raw_info
    key = "|".join(
        [
            raw_info.source_name or "",
            str(raw_info.line_no),
            artifact.name,
        ]
    )
    digest = hashlib.sha1(key.encode("utf-8")).hexdigest()[:10]
    slug = ARTIFACT_ID_SLUG_RE.sub("-", artifact.name.lower()).strip("-")
    return f"{slug[:48]}-{digest}" if slug else digest


def _player_from_source(source_file: str) -> str:
    match = PLAYER_RE.search(source_file)
    return match.group("player") if match else ""
