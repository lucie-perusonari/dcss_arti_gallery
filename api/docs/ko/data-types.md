# API 데이터 타입

이 문서는 `api`가 소유하는 공개 응답 DTO를 정의합니다.
`api` 모델은 MongoDB에 저장된 crawl artifact 문서와 모양이 비슷해도 API 공개 계약으로 별도로 관리합니다.

`api`는 `crawl_service`를 import하지 않습니다.

## `ArtifactSource`

- 정의 위치: `api.models.ArtifactSource`
- 필드:
  - `player: str`

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
  - `source: ArtifactSource`
  - `randomAttributes: list[str]`
  - `score: ArtifactEvaluation`
  - `dcssDescription: str`

## 연계 문서

- [API Processing Layers](./processing-layers.md)
- [Frontend Data Types](../../../frontend/docs/ko/data-types.md)
