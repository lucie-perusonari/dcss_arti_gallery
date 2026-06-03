# Frontend Processing Layers

이 문서는 gallery frontend의 API boundary와 UI 계층을 정의합니다.

## Project Boundary

- 모듈: `frontend/`
- 역할: Gallery API 응답을 React UI state로 가져와 WebTiles 스타일 gallery와 detail view를 표시한다.
- 입력: Gallery API artifact response
- 출력: browser UI state

## Internal Layers

- `src/api`: `VITE_ARTIFACT_API_URL` 기반 Gallery API client. API URL이 없으면 local mock data로 fallback한다.
- `src/types`: API response와 UI rendering에 쓰는 TypeScript artifact types
- `src/data`: local mock artifact data와 DCSS tile mapping
- `src/components`: WebTiles-style panels, filters, cards, item details, nickname crawl UI
- `public/tiles`: local DCSS tile PNG assets
- `public/STYLE_SOURCES.md`: WebTiles CSS/font source 기록
- `reference`: DCInside 로그라이크 갤러리 기반 DCSS item UI design reference

## Related Docs

- [Frontend Data Types](./data-types.md)
- [API Data Types](../../../api/docs/reference/data-types.md)
