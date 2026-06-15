# `src/api`

`src/api`는 gallery frontend가 Gallery API에서 artifact를 읽는 API 경계입니다.

## 책임

- `VITE_ARTIFACT_API_URL`이 있으면 Gallery API를 호출합니다.
- `VITE_ARTIFACT_API_URL`이 없으면 설정 오류를 반환합니다.
- UI component가 transport 세부사항에 직접 의존하지 않도록 repository 함수를 제공합니다.
- `search`, `type`, `player`, `timeRange`는 Gallery API 요청에 반영합니다.
- `displayCategory`는 Gallery API 요청에 반영해 하위 카테고리별로 고정 개수를 로드합니다.
- `slot` 하위 필터는 화면 표시 상태이며, API와 같은 fallback 분류 규칙으로 파생합니다.

## 필터 동작

`listArtifacts`는 type/search/player/timeRange 기준에 더해 `displayCategory`별로 Gallery API를 호출합니다.
`timeRange`는 Gallery API의 `since` query parameter로 전달하며, 기본값은 최근 30일입니다.
전체 타입 조회와 특정 타입 조회 모두 타입별 `displayCategory`마다 70개씩 로드합니다.

이 구분을 유지해야 하위 카테고리별 충분한 목록을 확보하면서도 하위 필터를 클릭했을 때 같은 type에 속한
다른 하위 항목 옵션이 사라지지 않습니다.

## 관련 문서

- [Processing Layers](processing-layers.md)
- [API Data Types](../../../api/docs/ko/data-types.md)
