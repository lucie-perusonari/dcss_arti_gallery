# Crawl Admin Frontend

`admin-frontend`는 React + TypeScript + Vite 기반 crawl operations dashboard입니다.
Gallery API의 admin endpoint에서 crawl file/user/raw file 상태를 읽어 운영 상태를 보여줍니다.

## Responsibilities

- `src/App.tsx`: crawl status dashboard 화면
- `src/api/status.ts`: `VITE_ADMIN_API_URL` 기반 admin API client
- `src/styles.css`: dashboard layout과 상태 표시 스타일
- `vite.config.ts`: Vite build/dev configuration

## Runtime

dependencies:

```sh
npm install
```

API URL을 지정해 dev server를 실행합니다.

```sh
VITE_ADMIN_API_URL=http://127.0.0.1:8000 npm run dev -- --host 127.0.0.1 --port 5174
```

저장소 루트에서는 다음 스크립트를 사용할 수 있습니다.

```sh
./scripts/run_admin.sh
```

기본 Admin URL은 `http://127.0.0.1:5174`입니다.

## Build

```sh
npm run build
```

admin API contract 변경은 `python3 -m unittest discover -s api/tests -t .`와 admin frontend build를 함께 확인합니다.

## Related Shared Docs

- [Processing Layers](docs/reference/processing-layers.md)
- [Data Types](docs/reference/data-types.md)
- [Harness Validation](../docs/ops/harness/validation.md)
