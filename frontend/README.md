# DCSS 아티팩트 갤러리 프론트엔드

`frontend`는 React + TypeScript + Vite 기반 WebTiles 스타일 artifact 갤러리입니다.
persisted artifact data는 Gallery API에서 읽고, `VITE_ARTIFACT_API_URL`이 없으면 local mock data로 fallback합니다.

## 모듈

- [`src/api`](docs/ko/api.md): frontend API 경계와 `VITE_ARTIFACT_API_URL` 기반 Gallery API client
- [`src/types`](docs/ko/types.md): API 응답과 갤러리 렌더링에 쓰는 TypeScript artifact 타입
- [`src/data`](docs/ko/data.md): 로컬 mock artifact 데이터와 DCSS 타일 매핑
- [`src/components`](docs/ko/components.md): WebTiles 스타일 패널, 필터, 카드, 아이템 상세, 닉네임 크롤 UI
- [`public/tiles`](docs/ko/public-tiles.md): 로컬 DCSS 타일 PNG 자산
- [`reference/`](docs/ko/reference.md): DCSS/WebTiles UI 레퍼런스와 회귀 비교용 스냅샷
- [`run_frontend.sh`](docs/ko/run_frontend.md): frontend dev server 실행 wrapper

English version: [README.en.md](README.en.md)

## 책임

- Gallery API 응답을 사용해 artifact 갤러리 화면을 렌더링합니다.
- `VITE_ARTIFACT_API_URL`이 없을 때 local mock data fallback을 제공합니다.
- frontend TypeScript 타입과 API 응답 사용 경계를 소유합니다.
- DCSS/WebTiles 스타일의 갤러리 UI, 타일 사용, 상세 패널 표현을 소유합니다.

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

서비스 스크립트로 실행:

```sh
./frontend/run_frontend.sh
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

## 관련 상세 문서

- [Processing Layers](docs/ko/processing-layers.md)
- [Data Types](docs/ko/data-types.md)
