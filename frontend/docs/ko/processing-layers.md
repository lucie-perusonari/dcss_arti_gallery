# Frontend 처리 계층

이 문서는 gallery frontend의 API boundary와 UI 계층을 정의합니다.

## 프로젝트 경계

- 모듈: `frontend/`
- 역할: Gallery API 응답을 React UI state로 가져와 WebTiles 스타일 gallery와 detail view를 표시한다.
- 입력: Gallery API artifact response
- 출력: browser UI state

## 내부 계층

- `src/api`: `VITE_ARTIFACT_API_URL` 기반 Gallery API client
- `src/types`: API 응답과 갤러리 렌더링에 쓰는 TypeScript artifact 타입
- `src/components`: WebTiles 스타일 패널, 필터, 카드, 아이템 상세, 닉네임 크롤 UI
- `public/tiles`: 로컬 DCSS 타일 PNG 자산
- `docs/ko/style-sources.md`: WebTiles CSS/font 출처 기록
- `reference`: DCInside 로그라이크 갤러리를 기준으로 한 DCSS 아이템 UI 참고 자료

## 연계 문서

- [Frontend Data Types](./data-types.md)
- [API Data Types](../../../api/docs/ko/data-types.md)
