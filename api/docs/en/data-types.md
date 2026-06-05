# API Data Types

This document defines the public response DTOs owned by `api`.
Even when the API models resemble the MongoDB-stored crawl artifact documents, they are maintained separately as the
public API contract.

`api` does not import `crawl_service`.

## `ArtifactSource`

- Defined in: `api.models.ArtifactSource`
- Fields:
  - `player: str`
  - `file: str`
  - `url: str | None`
  - `line: int`

## `ArtifactAttribute`

- Defined in: `api.models.ArtifactAttribute`
- Fields:
  - `token: str`
  - `kind: str`
  - `description: str`
  - `scoreImpact: str`

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
  - `enchantment`, `brand`, `origin`
  - `source: ArtifactSource`
  - `attributes: list[ArtifactAttribute]`
  - `allAttributes`, `baseAttributes`, `randomAttributes`
  - `allAttributeText`, `baseAttributeText`, `randomAttributeText`
  - `evaluation: ArtifactEvaluation`
  - `score: ArtifactEvaluation`
  - `rawDescription: list[str]`
  - `dcssDescription: str`

## `CrawlStatus`

- Defined in: `api.admin_models.CrawlStatus`
- Purpose: admin dashboard status response
- Fields:
  - `artifactCount: int`
  - `rawFiles: RawFileStatus`
  - `crawlFiles: dict[str, int]`
  - `crawlUsers: dict[str, int]`
  - `latest: LatestActivity`
  - `recentErrors: list[CrawlError]`

## Related Docs

- [API Processing Layers](./processing-layers.md)
- [Frontend Data Types](../../../frontend/docs/en/data-types.md)
- [Admin Frontend Data Types](../../../admin-frontend/docs/en/data-types.md)
