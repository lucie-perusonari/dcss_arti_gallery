# `src/api/status.ts`

`src/api/status.ts`는 admin frontend의 Admin API client입니다.

## 책임

- `VITE_ADMIN_API_URL`을 기준으로 `/admin/crawl-status`를 호출합니다.
- HTTP 실패와 response parsing 실패를 frontend에서 다룰 수 있는 오류로 전달합니다.
- UI component가 endpoint URL 구성에 직접 의존하지 않도록 경계를 둡니다.

## 관련 문서

- [Processing Layers](processing-layers.md)
- [Admin API Data Types](../../../admin_api/docs/ko/data-types.md)
