# `src/api`

`src/api`는 gallery frontend가 Gallery API 또는 local mock data에서 artifact를 읽는 API 경계입니다.

## 책임

- `VITE_ARTIFACT_API_URL`이 있으면 Gallery API를 호출합니다.
- API URL이 없으면 local mock artifact data를 사용합니다.
- UI component가 transport 세부사항에 직접 의존하지 않도록 repository 함수를 제공합니다.
- `search`와 `type`은 Gallery API 요청에 반영합니다.
- `slot` 하위 필터는 API 요청에 보내지 않고, API 응답 목록을 받은 뒤 frontend state에서만 적용합니다.

## 필터 동작

`listArtifacts`는 type/search 기준 원본 목록을 반환합니다. armour slot, weapon subtype,
jewellery slot 같은 하위 필터는 `App.tsx`에서 `displayedArtifacts`로 파생합니다.

이 구분을 유지해야 하위 필터를 클릭했을 때 같은 type에 속한 다른 하위 항목 옵션이 사라지지 않습니다.

## 관련 문서

- [Processing Layers](processing-layers.md)
- [API Data Types](../../../api/docs/ko/data-types.md)
