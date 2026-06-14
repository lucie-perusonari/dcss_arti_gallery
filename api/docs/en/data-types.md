# API Data Types

This document defines the public response DTOs owned by `api`.
Even when the API models resemble the MongoDB-stored artifact read model, they are maintained separately as the
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

## `ArtifactDiscovery`

- Defined in: `api.models.ArtifactDiscovery`
- Fields:
  - `version: str | None`: DCSS version from the first discovered source.
  - `datetime: str | None`: `game_ended_at` from the first discovered source.

## `ArtifactDocument`

- Defined in: `api.models.ArtifactDocument`
- Purpose: artifact read model returned by the Gallery API
- Key fields:
  - `id`, `name`, `baseItem`, `type`, `subtype`, `tile`
  - `weaponSubtype: str | None`
  - `armourSubtype: str | None`
  - `armourSlot: str | None`
  - `jewellerySlot: str | None`
  - `source: ArtifactSource`
  - `allAttributes: list[str]`
  - `baseAttributes: list[str]`
  - `randomAttributes: list[str]`
  - `discovery: ArtifactDiscovery`
  - `score: ArtifactEvaluation`
  - `dcssDescription: str`

The subtype/slot fields are camelCase projections of MongoDB fields such as
`weapon_subtype`, `armour_subtype`, `armour_slot`, and `jewellery_slot`.
`armourSubtype` preserves the original armour base type within a slot, such as `hat`, `helmet`, or `pair of gloves`.
For jewellery artifacts, `dcssDescription` includes the original subtype as `[ring of ...]`.
`allAttributes` excludes ignored Ashenzari skill boost tokens.

## Related Docs

- [API Processing Layers](./processing-layers.md)
- [Frontend Data Types](../../../frontend/docs/en/data-types.md)
