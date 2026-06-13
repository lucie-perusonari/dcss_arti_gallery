# API Data Types

This document defines the public response DTOs owned by `api`.
Even when the API models resemble the MongoDB-stored crawl artifact documents, they are maintained separately as the
public API contract.

`api` does not import `crawl_service`.

## `ArtifactSource`

- Defined in: `api.models.ArtifactSource`
- Fields:
  - `player: str`
  - `url: str | None`: original morgue file URL.

## `ArtifactEvaluation`

- Defined in: `api.models.ArtifactEvaluation`
- Fields:
  - `total: int`
  - `practical_score: int | None`
  - `rarity_score: int`
  - `offense: int`
  - `defense: int`
  - `utility: int`
  - `penalty: int`
  - `base_fit: int`
  - `grade: str`
  - `luxury_grade: str | None`

## `ArtifactDocument`

- Defined in: `api.models.ArtifactDocument`
- Purpose: artifact read model returned by the Gallery API
- Key fields:
  - `id`, `name`, `baseItem`, `type`, `subtype`, `tile`
  - `weaponSubtype: str | None`
  - `armourSlot: str | None`
  - `jewellerySlot: str | None`
  - `source: ArtifactSource`
  - `randomAttributes: list[str]`
  - `score: ArtifactEvaluation`
  - `dcssDescription: str`

The subtype/slot fields are camelCase projections of MongoDB fields such as
`weapon_subtype`, `armour_slot`, and `jewellery_slot`.

## Related Docs

- [API Processing Layers](./processing-layers.md)
- [Frontend Data Types](../../../frontend/docs/en/data-types.md)
