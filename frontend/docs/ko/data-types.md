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

## `ArtifactDiscovery`

- 정의 위치: `frontend/src/types/artifact.ts`
- 필드:
  - `version?: string | null`: 최초 발견 source의 DCSS version입니다.
  - `datetime?: string | null`: 최초 발견 source의 datetime입니다.

## `Artifact`

- 정의 위치: `frontend/src/types/artifact.ts`
  - 용도: 갤러리 목록/상세 렌더링 상태
- 주요 필드:
  - `id`, `name`, `baseItem`, `type`, `subtype`, `tile`
  - `weaponSubtype?: string | null`
  - `armourSubtype?: string | null`
  - `armourSlot?: string | null`
  - `jewellerySlot?: string | null`
  - `source`
  - `allAttributes`
  - `baseAttributes`
  - `randomAttributes`
  - `discovery`
  - `score`
  - `dcssDescription`

`weaponSubtype`, `armourSubtype`, `armourSlot`, `jewellerySlot`는 타입별 하위 필터와 렌더링 보조 정보로 사용합니다.
값이 없으면 UI는 `subtype`을 fallback으로 사용합니다.
`armourSubtype`은 `hat`, `helmet`, `pair of gloves`처럼 같은 armour slot 안에서 아이콘과 카드 표시를
구분하는 원본 장비 타입입니다.
`source.url`이 있으면 상세 설명창에서 원본 morgue 링크로 사용합니다.
`allAttributes`는 카드 `token-row` 표시 원본이며, base intrinsic 속성을 포함하지만 ignored 속성은 포함하지 않습니다.
`baseAttributes`는 원본 아이템/세부 타입이 제공하는 intrinsic 속성입니다.
`discovery`는 상세 팝업 하단의 발견 version/datetime 표시에 사용합니다.

## `ArtifactFilters`

- 정의 위치: `frontend/src/types/artifact.ts`
- 필드:
  - `search: string`
  - `type: ArtifactType | 'all'`
  - `slot: string`
  - `player: string`
  - `timeRange: '30d' | 'all'`

`player`는 Gallery API의 `player` query parameter로 전달해 특정 플레이어가 얻은 랜다트 목록을
불러오는 데 사용합니다.

`timeRange`는 Gallery API의 `since` query parameter로 전달합니다. 기본값 `30d`는 최근 30일 게임만
조회하고, `all`은 날짜 범위를 제한하지 않습니다.

`slot`은 frontend 표시 필터이며, API와 같은 fallback 분류 규칙으로 계산합니다. API에서 받은 타입/검색/player 기준 원본
목록은 유지하고, 화면에 표시할 목록만 `slot`으로 파생 필터링합니다. 이렇게 해야 하위 필터 버튼을
클릭해도 같은 타입의 다른 하위 항목 버튼이 사라지지 않습니다.

무기의 `slot`은 DCSS weapon skill 분류를 기준으로 `short blades`, `long blades`, `axes`,
`maces & flails`, `polearms`, `staves`, `ranged`로 나눕니다. 예를 들어 `giant club`과
`giant spiked club`은 `maces & flails`, `quick blade`는 `short blades`입니다.

장신구의 `slot`은 세부 subtype이 아니라 `ring` 또는 `amulet`으로 단순화합니다.

Talisman의 `slot`은 개별 subtype 대신 form tier 단위로 묶습니다. 현재 UI는 `tier 1 talismans`부터
`tier 5 talismans`, `other talismans`를 표시 필터로 사용합니다.

## 연계 문서

- [Frontend Processing Layers](./processing-layers.md)
- [API Data Types](../../../api/docs/ko/data-types.md)
