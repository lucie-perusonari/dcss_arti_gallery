# DCSS 아티팩트 갤러리 프론트엔드

`frontend`는 React + TypeScript + Vite 기반 WebTiles 스타일 artifact 갤러리입니다.
persisted artifact data는 Gallery API에서 읽고, `VITE_ARTIFACT_API_URL`이 없으면 local mock data로 fallback합니다.

English version: [README.en.md](README.en.md)

## 책임

- `src/api`: frontend API 경계. `VITE_ARTIFACT_API_URL`로 artifact repository read를 호출합니다.
- `src/types`: API 응답과 갤러리 렌더링에 쓰는 TypeScript artifact 타입
- `src/data`: 로컬 mock artifact 데이터와 DCSS 타일 매핑
- `src/components`: WebTiles 스타일 패널, 필터, 카드, 아이템 상세, 닉네임 크롤 UI
- `public/tiles`: 로컬 DCSS 타일 PNG 자산
- `docs/ko/style-sources.md`: DCSS 팝업 스타일 재현을 위한 WebTiles CSS/font 출처
- `reference/dcinside-log-gallery`: DCInside 로그라이크 갤러리 기반 DCSS 아이템 UI 이미지 레퍼런스
- `reference/screenshots/current-ui`: 회귀 비교용 현재 UI 스냅샷

## 실행

dependencies:

```sh
npm install
```

API를 연결하지 않는 mock gallery:

```sh
npm run dev
```

Gallery API에 연결:

```sh
VITE_ARTIFACT_API_URL=http://127.0.0.1:8000 npm run dev -- --host 127.0.0.1 --port 5173
```

저장소 루트에서는 다음 스크립트를 사용할 수 있습니다.

```sh
./scripts/run_frontend.sh
```

## 빌드

```sh
npm run build
```

API/frontend contract 변경은 [Frontend Data Types](docs/ko/data-types.md)와
[API Data Types](../api/docs/ko/data-types.md)를 확인하고,
API 테스트와 frontend build를 함께 실행합니다.

## Mock 화면 상태

- `/`: 전체 갤러리
- `/?type=jewellery&selected=keod`: type 필터링된 장신구 상세
- `/?type=weapon&selected=ashenzari-axe`: 무기 상세
- `/?search=regen&selected=ceguteof`: 검색 흐름

## 연계 문서

- [Processing Layers](docs/ko/processing-layers.md)
- [Data Types](docs/ko/data-types.md)
- [Harness Validation](../docs/ops/harness/validation.md)
