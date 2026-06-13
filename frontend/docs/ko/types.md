# `src/types`

`src/types`는 Gallery API 응답과 UI 렌더링에 쓰는 TypeScript 타입을 소유합니다.

## 책임

- artifact 목록/상세 렌더링에 필요한 `Artifact` 계열 타입을 정의합니다.
- API response shape와 frontend state 사이의 타입 경계를 명시합니다.
- component와 data module이 공유하는 타입 export를 제공합니다.

## 변경 규칙

타입을 변경하면 [API Data Types](../../../api/docs/ko/data-types.md)와 API 응답 DTO를 함께 확인합니다.

## 관련 문서

- [Frontend Data Types](data-types.md)
