# Crawl Admin Frontend

`admin-frontend` is a React + TypeScript + Vite-based crawl operations dashboard.
It reads crawl file/user/raw file status and Gallery API metrics from the Admin API endpoint and presents the operational state.

## Modules

- [`src/App.tsx`](src/App.tsx): crawl status dashboard UI
- [`src/api/status.ts`](src/api/status.ts): admin API client backed by `VITE_ADMIN_API_URL`
- [`src/types/status.ts`](src/types/status.ts): TypeScript types for Admin API responses
- [`src/styles.css`](src/styles.css): dashboard layout and status styling
- [`vite.config.ts`](vite.config.ts): Vite build/dev configuration
- [`run_admin.sh`](run_admin.sh): admin frontend dev server wrapper
- [`tests/test_mock_smoke.py`](tests/test_mock_smoke.py): mock admin API smoke test

## Runtime

Dependencies:

```sh
npm install
```

Run the dev server with an explicit API URL:

```sh
VITE_ADMIN_API_URL=http://127.0.0.1:8001 npm run dev -- --host 127.0.0.1 --port 5174
```

From the repository root, you can use the service scripts:

```sh
./admin_api/run_admin_api.sh
./admin-frontend/run_admin.sh
```

The default Admin URL is `http://127.0.0.1:5174`.
The default Admin API URL is `http://127.0.0.1:8001`, and the default CORS setup allows the admin dev port `5174`.
Set `ADMIN_API_CORS_ORIGINS` or `ADMIN_API_CORS_ORIGIN_REGEX` when another origin needs access.
Set `VITE_GRAFANA_URL` in the frontend run or build environment to show the Grafana dashboard link.

## Build

```sh
npm run build
```

Smoke test with a mock admin API:

```sh
npm run test:mock
```

When the admin API contract changes, verify it together with
`python3 -m unittest discover -s admin_api/tests -t .` and the admin frontend build.

## Related Docs

- [Processing Layers](docs/en/processing-layers.md)
- [Data Types](docs/en/data-types.md)
