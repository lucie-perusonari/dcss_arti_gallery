# Crawl Admin Frontend

`admin-frontend` is a React + TypeScript + Vite-based crawl operations dashboard.
It reads crawl file/user/raw file status and Gallery API metrics from the Admin API endpoint and presents the operational state.

## Modules

- [`src/App.tsx`](docs/ko/app.md): crawl status dashboard UI
- [`src/api/status.ts`](docs/ko/api-status.md): admin API client backed by `VITE_ADMIN_API_URL`
- [`src/types/status.ts`](docs/ko/types-status.md): TypeScript types for Admin API responses
- [`src/styles.css`](docs/ko/styles.md): dashboard layout and status styling
- [`vite.config.ts`](docs/ko/vite-config.md): Vite build/dev configuration
- [`tests/test_mock_smoke.py`](docs/ko/mock-smoke-test.md): mock admin API smoke test

## Runtime

Dependencies:

```sh
npm install
```

Run the dev server with an explicit API URL:

```sh
VITE_ADMIN_API_URL=http://127.0.0.1:8001 npm run dev -- --host 127.0.0.1 --port 5174
```

In the full development stack, compose manages the Admin API and admin frontend API URL together:

```sh
docker compose -f infra/dev/docker-compose.yml up admin-api admin-frontend
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
