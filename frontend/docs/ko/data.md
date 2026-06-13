# `src/data`

`src/data`는 frontend 단독 실행과 UI 개발을 위한 local data를 소유합니다.

## 책임

- Gallery API 없이 사용할 mock artifact 목록을 제공합니다.
- DCSS base item과 local tile asset 사이의 매핑을 제공합니다.
- UI fixture가 API 계약에서 벗어나지 않도록 `src/types` 타입을 사용합니다.

## 비소유 책임

- persisted artifact read model 생성은 `arti_parser`가 소유합니다.
- 실제 API 응답 shape는 `api`가 소유합니다.

## 관련 문서

- [Frontend Data Types](data-types.md)
