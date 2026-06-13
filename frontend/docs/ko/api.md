# `src/api`

`src/api`는 gallery frontend가 Gallery API 또는 local mock data에서 artifact를 읽는 API 경계입니다.

## 책임

- `VITE_ARTIFACT_API_URL`이 있으면 Gallery API를 호출합니다.
- API URL이 없으면 local mock artifact data를 사용합니다.
- UI component가 transport 세부사항에 직접 의존하지 않도록 repository 함수를 제공합니다.

## 관련 문서

- [Processing Layers](processing-layers.md)
- [API Data Types](../../../api/docs/ko/data-types.md)
