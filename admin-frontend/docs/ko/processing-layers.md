# Admin Frontend 처리 계층

이 문서는 crawl operations dashboard의 API boundary와 UI 계층을 정의합니다.

## 프로젝트 경계

- 모듈: `admin-frontend/`
- 역할: Admin crawl status API 응답을 React UI state로 가져와 운영 대시보드를 표시한다.
- 입력: `/admin/crawl-status` response
- 출력: browser UI state

## 내부 계층

- `src/api/status.ts`: `VITE_ADMIN_API_URL` 기반 admin API client
- `src/types/status.ts`: admin status TypeScript types
- `src/App.tsx`: crawl status dashboard 화면
- `src/styles.css`: dashboard layout과 상태 표시 스타일

## 연계 문서

- [Admin Frontend Data Types](./data-types.md)
- [API Data Types](../../../api/docs/ko/data-types.md)
