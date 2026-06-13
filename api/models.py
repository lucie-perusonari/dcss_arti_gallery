"""Gallery API-owned response models."""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict, model_validator


class ArtifactSource(BaseModel):
    model_config = ConfigDict(extra="ignore")

    player: str
    url: str | None = None


class ArtifactEvaluation(BaseModel):
    model_config = ConfigDict(extra="ignore")

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
    """Read model returned by the Gallery API."""

    model_config = ConfigDict(extra="ignore")

    id: str
    name: str
    baseItem: str
    type: str
    subtype: str
    weaponSubtype: str | None = None
    armourSlot: str | None = None
    jewellerySlot: str | None = None
    tile: str
    source: ArtifactSource
    randomAttributes: list[str]
    score: ArtifactEvaluation
    dcssDescription: str

    @model_validator(mode="before")
    @classmethod
    def normalize_document(cls, value):
        data = dict(value)
        data.pop("_id", None)
        data["score"] = data.get("score") or data.get("evaluation")
        return data
