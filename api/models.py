"""Gallery API-owned response models."""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict, model_validator


class ArtifactSource(BaseModel):
    model_config = ConfigDict(extra="ignore")

    player: str
    file: str
    url: str | None
    line: int


class ArtifactAttribute(BaseModel):
    model_config = ConfigDict(extra="ignore")

    token: str
    kind: str
    description: str
    scoreImpact: str


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
    tile: str
    enchantment: str | None
    brand: str | None
    origin: str = ""
    source: ArtifactSource
    attributes: list[ArtifactAttribute]
    allAttributes: list[str]
    baseAttributes: list[str]
    randomAttributes: list[str]
    allAttributeText: str
    baseAttributeText: str
    randomAttributeText: str
    evaluation: ArtifactEvaluation
    score: ArtifactEvaluation
    rawDescription: list[str]
    dcssDescription: str

    @model_validator(mode="before")
    @classmethod
    def normalize_document(cls, value):
        data = dict(value)
        data.pop("_id", None)
        data["origin"] = data.get("origin", "")
        data["score"] = data.get("score") or data.get("evaluation")
        return data
