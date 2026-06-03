# Frontend 데이터 타입

이 문서는 gallery frontend가 소비하는 artifact 타입을 정의합니다.
TypeScript 타입은 Gallery API 응답과 정렬되어야 합니다.

## `ArtifactType`

- 정의 위치: `frontend/src/types/artifact.ts`
- 값: `weapon`, `armour`, `jewellery`, `talisman`, `staff`, `misc`

## `ArtifactAttribute`

- 정의 위치: `frontend/src/types/artifact.ts`
- 필드:
  - `token: string`
  - `kind: 'resistance' | 'stat' | 'property' | 'penalty' | 'brand' | 'spell_school'`
  - `description: string`
  - `scoreImpact: 'positive' | 'negative' | 'neutral'`

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
  - `enchantment`, `brand`, `origin`
  - `source`
  - `attributes`, `randomAttributes`
  - `allAttributes`, `baseAttributes`
  - `allAttributeText`, `baseAttributeText`, `randomAttributeText`
  - `evaluation`, `score`
  - `rawDescription`, `dcssDescription`

## 연계 문서

- [Frontend Processing Layers](./processing-layers.md)
- [API Data Types](../../../api/docs/reference/data-types.md)
