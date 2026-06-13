# Frontend 데이터 타입

이 문서는 gallery frontend가 소비하는 artifact 타입을 정의합니다.
TypeScript 타입은 Gallery API 응답과 정렬되어야 합니다.

## `ArtifactType`

- 정의 위치: `frontend/src/types/artifact.ts`
- 값: `weapon`, `armour`, `jewellery`, `talisman`, `staff`, `misc`

## `ArtifactEvaluation`

- 정의 위치: `frontend/src/types/artifact.ts`
- 필드:
  - `total: number`
  - `practical_score?: number | null`
  - `rarity_score?: number`
  - `offense`, `defense`, `utility`, `penalty`
  - `base_fit?: number`
  - `grade?: string`
  - `luxury_grade?: string | null`

## `Artifact`

- 정의 위치: `frontend/src/types/artifact.ts`
  - 용도: 갤러리 목록/상세 렌더링 상태
- 주요 필드:
  - `id`, `name`, `baseItem`, `type`, `subtype`, `tile`
  - `weaponSubtype?: string | null`
  - `armourSlot?: string | null`
  - `jewellerySlot?: string | null`
  - `source`
  - `randomAttributes`
  - `score`
  - `dcssDescription`

`weaponSubtype`, `armourSlot`, `jewellerySlot`는 타입별 하위 필터와 렌더링 보조 정보로 사용합니다.
값이 없으면 UI는 `subtype`을 fallback으로 사용합니다.
`source.url`이 있으면 상세 설명창에서 원본 morgue 링크로 사용합니다.

## `ArtifactFilters`

- 정의 위치: `frontend/src/types/artifact.ts`
- 필드:
  - `search: string`
  - `type: ArtifactType | 'all'`
  - `slot: string`
  - `luxuryOnly: boolean`
  - `player: string`
  - `timeRange: '30d' | 'all'`

`player`는 Gallery API의 `player` query parameter로 전달해 특정 플레이어가 얻은 랜다트 목록을
불러오는 데 사용합니다.

`timeRange`는 Gallery API의 `since` query parameter로 전달합니다. 기본값 `30d`는 최근 30일 게임만
조회하고, `all`은 날짜 범위를 제한하지 않습니다.

`slot`은 API query parameter가 아니라 frontend 표시 필터입니다. API에서 받은 타입/검색/player 기준 원본
목록은 유지하고, 화면에 표시할 목록만 `slot`으로 파생 필터링합니다. 이렇게 해야 하위 필터 버튼을
클릭해도 같은 타입의 다른 하위 항목 버튼이 사라지지 않습니다.

장신구의 `slot`은 세부 subtype이 아니라 `ring` 또는 `amulet`으로 단순화합니다.

## 연계 문서

- [Frontend Processing Layers](./processing-layers.md)
- [API Data Types](../../../api/docs/ko/data-types.md)
