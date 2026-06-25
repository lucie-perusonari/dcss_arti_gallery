# `routes.py`

`routes.py`는 Gallery API HTTP endpoint를 소유합니다.

## 책임

- `GET /artifacts` 목록 조회를 제공합니다.
  - `q`: 이름/base item/subtype/random attribute 검색어입니다.
  - `type`: `weapon`, `armour`, `jewellery`, `talisman`, `staff`, `misc`, `all`입니다.
  - `displayCategory`: 타입 안의 UI 표시 하위 카테고리입니다. 현재는 저장 필드가 아니라 API fallback 계산 규칙으로 필터링합니다.
  - `player`: 대표 source 또는 누적 source evidence의 player exact match입니다.
  - `since`: 기본값 `30d`입니다. `all`이면 날짜 범위를 제한하지 않습니다.
  - `sort`: `recent` 또는 `score`입니다. 기본값 `recent`는 최신 게임 기록 우선입니다.
  - `limit`: 기본값 `200`, 최대 `1000`입니다.
  - `offset`: 정렬된 결과에서 건너뛸 개수입니다.
- `GET /artifacts/{artifact_id}` 단건 조회를 제공합니다.
- `GET /artifact-types`와 `GET /filters` 필터 메타데이터를 제공합니다. `/filters`는 `types`와
  타입별 `displayCategories`를 반환합니다.
- repository 결과를 API response model로 반환합니다.

## 비소유 책임

- MongoDB index DDL은 `infra/`가 소유합니다.
- frontend state와 렌더링은 `frontend`가 소유합니다.

## 관련 문서

- [Processing Layers](processing-layers.md)
- [Data Types](data-types.md)
