# Crawl Admin Frontend

`admin-frontend` is a React + TypeScript + Vite-based crawl operations dashboard.
It reads crawl file/user/raw file status from the Gallery API admin endpoint and presents the operational state.

## Responsibilities

- `src/App.tsx`: crawl status dashboard UI
- `src/api/status.ts`: admin API client backed by `VITE_ADMIN_API_URL`
- `src/styles.css`: dashboard layout and status styling
- `vite.config.ts`: Vite build/dev configuration

## Runtime

Dependencies:

```sh
npm install
```

Run the dev server with an explicit API URL:

```sh
VITE_ADMIN_API_URL=http://127.0.0.1:8000 npm run dev -- --host 127.0.0.1 --port 5174
```

From the repository root, you can use:

```sh
./scripts/run_admin.sh
```

The default Admin URL is `http://127.0.0.1:5174`.
The API's default CORS setup explicitly allows the gallery dev port `5173`. When the admin dev server calls the API,
include the `5174` origin in the API environment, for example
`ARTIFACT_API_CORS_ORIGINS=http://localhost:5173,http://127.0.0.1:5173,http://127.0.0.1:5174`.

## Build

```sh
npm run build
```

When the admin API contract changes, verify it together with
`python3 -m unittest discover -s api/tests -t .` and the admin frontend build.

## Related Docs

- [Processing Layers](docs/en/processing-layers.md)
- [Data Types](docs/en/data-types.md)
