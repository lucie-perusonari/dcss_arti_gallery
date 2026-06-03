# DCSS Artifact Gallery Frontend

`frontend`는 React + TypeScript + Vite 기반 WebTiles-style artifact gallery입니다.
persisted artifact data는 Gallery API에서 읽고, `VITE_ARTIFACT_API_URL`이 없으면 local mock data로 fallback합니다.

## Responsibilities

- `src/api`: frontend API boundary. `VITE_ARTIFACT_API_URL`로 artifact repository reads를 호출합니다.
- `src/types`: API response와 gallery rendering에 쓰는 TypeScript artifact types
- `src/data`: local mock artifact data와 DCSS tile mapping
- `src/components`: WebTiles-style panels, filters, cards, item details, nickname crawl UI
- `public/tiles`: local DCSS tile PNG assets
- `public/STYLE_SOURCES.md`: DCSS popup look을 맞추기 위한 WebTiles CSS/font source 기록
- `reference`: DCInside 로그라이크 갤러리 기반 DCSS item UI design reference
- `screenshots/current-ui`: regression comparison용 현재 UI snapshots

## Runtime

dependencies:

```sh
npm install
```

API에 연결하지 않는 mock gallery:

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

## Build

```sh
npm run build
```

API/frontend contract 변경은 [Frontend Data Types](docs/reference/data-types.md)와
[API Data Types](../api/docs/reference/data-types.md)를 확인하고,
API 테스트와 frontend build를 함께 실행합니다.

## Mock Screen States

- `/`: full gallery
- `/?type=jewellery&selected=keod`: type-filtered jewellery detail
- `/?type=weapon&selected=ashenzari-axe`: weapon detail
- `/?search=regen&selected=ceguteof`: search flow

## Related Shared Docs

- [Processing Layers](docs/reference/processing-layers.md)
- [Data Types](docs/reference/data-types.md)
- [Harness Validation](../docs/ops/harness/validation.md)
