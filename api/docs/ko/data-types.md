# API 데이터 타입

이 문서는 `api`가 소유하는 공개 응답 DTO를 정의합니다.
`api` 모델은 MongoDB에 저장된 crawl artifact 문서와 모양이 비슷해도 API 공개 계약으로 별도로 관리합니다.

`api`는 `crawl_service`를 import하지 않습니다.

## `ArtifactSource`

- 정의 위치: `api.models.ArtifactSource`
- 필드:
  - `player: str`
  - `url: str | None`: 원본 morgue 파일 URL입니다.

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

## `ArtifactDiscovery`

- 정의 위치: `api.models.ArtifactDiscovery`
- 필드:
  - `version: str | None`: 최초 발견 source의 DCSS version입니다.
  - `datetime: str | None`: 최초 발견 source의 `game_ended_at`입니다.

## `ArtifactDocument`

- 정의 위치: `api.models.ArtifactDocument`
- 용도: Gallery API가 반환하는 artifact read model
- 주요 필드:
  - `id`, `name`, `baseItem`, `type`, `subtype`, `tile`
  - `weaponSubtype: str | None`: weapon 세부 분류입니다. 예: `melee`, `ranged`.
  - `armourSubtype: str | None`: armour 원본 장비 타입입니다. 예: `hat`, `helmet`, `pair of gloves`.
  - `armourSlot: str | None`: armour 장착 부위입니다. 예: `body armour`, `cloak`, `boots`.
  - `jewellerySlot: str | None`: jewellery 장착 부위입니다. 예: `ring`, `amulet`.
  - `source: ArtifactSource`
  - `allAttributes: list[str]`: base intrinsic 속성을 포함한 모든 표시 대상 속성입니다.
  - `baseAttributes: list[str]`: base item/subtype이 원래 가지는 intrinsic 속성입니다.
  - `randomAttributes: list[str]`
  - `discovery: ArtifactDiscovery`
  - `score: ArtifactEvaluation`
  - `dcssDescription: str`

분류 필드는 MongoDB의 snake_case field인 `weapon_subtype`, `armour_subtype`, `armour_slot`, `jewellery_slot`를
frontend용 camelCase field로 변환한 값입니다.
`dcssDescription`은 jewellery artifact의 원본 subtype을 `[ring of ...]` 형식으로 포함합니다.
`allAttributes`에는 Ashenzari skill boost처럼 ignored 처리된 속성을 포함하지 않습니다.

## 연계 문서

- [API Processing Layers](./processing-layers.md)
- [Frontend Data Types](../../../frontend/docs/ko/data-types.md)
