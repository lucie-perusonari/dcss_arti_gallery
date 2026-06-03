# API Data Types

이 문서는 `api`가 소유하는 public response DTO를 정의합니다.
`api` 모델은 MongoDB에 저장된 crawl artifact document와 모양이 비슷해도 API public contract로 따로 관리합니다.

`api`는 `crawl_service`를 import하지 않습니다.

## `ArtifactSource`

- 정의 위치: `api.models.ArtifactSource`
- 필드:
  - `player: str`
  - `file: str`
  - `url: str | None`
  - `line: int`

## `ArtifactAttribute`

- 정의 위치: `api.models.ArtifactAttribute`
- 필드:
  - `token: str`
  - `kind: str`
  - `description: str`
  - `scoreImpact: str`

## `ArtifactEvaluation`

- 정의 위치: `api.models.ArtifactEvaluation`
- 필드:
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

- 정의 위치: `api.models.ArtifactDocument`
- 용도: Gallery API가 반환하는 artifact read model
- 주요 필드:
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

- 정의 위치: `api.admin_models.CrawlStatus`
- 용도: admin dashboard status response
- 필드:
  - `artifactCount: int`
  - `rawFiles: RawFileStatus`
  - `crawlFiles: dict[str, int]`
  - `crawlUsers: dict[str, int]`
  - `latest: LatestActivity`
  - `recentErrors: list[CrawlError]`

## Related Docs

- [API Processing Layers](./processing-layers.md)
- [Frontend Data Types](../../../frontend/docs/reference/data-types.md)
- [Admin Frontend Data Types](../../../admin-frontend/docs/reference/data-types.md)
