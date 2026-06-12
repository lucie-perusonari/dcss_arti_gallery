# DCSS Arti Gallery

This repository collects random artifact information from Dungeon Crawl Stone Soup morgue logs and `lst` files,
then separates the random properties that do not exist on the base item and presents them as a gallery.

The repository contains several independent modules in one checkout. See each module's `README.md` for execution
details and local structure.

## Modules

- [crawl_service](crawl_service/README.en.md): remote morgue discovery/fetch, raw file storage, processing of stored raw source, artifact document generation, MongoDB writes, background worker
- [api](api/README.en.md): MongoDB artifact/admin read API, API-owned Pydantic response DTOs, FastAPI routes
- [frontend](frontend/README.en.md): React/Vite WebTiles-style artifact gallery
- [admin-frontend](admin-frontend/README.en.md): React/Vite crawl operations dashboard
- `infra/mongo`: Docker-based local MongoDB lifecycle scripts
- `scripts`: local development, corpus/report generation, and DCSS item data refresh scripts

`crawl_service` and `api` are treated as separate projects. `api` does not import `crawl_service`; it validates the
artifact documents stored in MongoDB with API-specific DTOs before returning them to the frontend.

The key data flow is: store the raw source first, then process the stored source later. The `raw_morgue_files`
collection is the reprocessable source of truth, and the `artifacts` collection is the reproducible read model read
by the API and frontend.

## Shared Docs

Module-specific documents live under each module's `docs/` directory. The root [docs](docs/README.en.md) directory acts
as the index for module docs. Root-level `docs/ops` files are working documents and are maintained in Korean only.

Key shared documents:

- [Documentation Index](docs/README.en.md): index of module reference docs
- [Crawl Service Data Types](crawl_service/docs/en/data-types.md): crawl/parser/scoring/storage types
- [API Data Types](api/docs/en/data-types.md): Gallery/admin API response DTOs
- [Frontend Data Types](frontend/docs/en/data-types.md): gallery TypeScript artifact types
- [Artifact Scoring Formula](crawl_service/docs/en/artifact_scoring_formula.md): artifact scoring criteria
- [DCSS Item Data](crawl_service/docs/en/dcss_item_data.md): official DCSS item data refresh criteria

## Crawl Operation Modes

The worker only fetches remote morgue source and stores it in `raw_morgue_files`.

```sh
python3 -m crawl_service.worker
```

Run artifact regeneration separately through the stored raw-file processor:

```sh
crawl_service/run_raw_crawler.sh
crawl_service/process_raw_morgue_files.sh
```

`crawl_service/run_raw_crawler.sh` runs the worker, so it only fills `raw_morgue_files`.
Run `DETACH=1 crawl_service/run_raw_crawler.sh` for background mode; the default log is
`.logs/crawl_raw_only.log`. `crawl_service/process_raw_morgue_files.sh` processes stored fetched raw files with the
current parser/scoring versions. Use `PROCESS_LIMIT` for batch size and `ONCE=1` for a single batch.

## Local MongoDB

```sh
eval "$(infra/mongo/mongo_up.sh)"
```

This script starts a `mongo:7.0` container with Docker and prints the default connection values.

Use the following scripts to check status or shut it down:

```sh
infra/mongo/mongo_status.sh
infra/mongo/mongo_down.sh
```

## Local Development

To run the gallery development stack (MongoDB, crawl worker, API, frontend) at once:

```sh
./scripts/run_dev.sh
```

Manual startup:

```sh
eval "$(infra/mongo/mongo_up.sh)"
python3 -m crawl_service.worker
python3 -m uvicorn api.app:app --host 0.0.0.0 --port 8000
cd frontend && VITE_ARTIFACT_API_URL=http://127.0.0.1:8000 npm run dev -- --host 127.0.0.1 --port 5173
```

Admin dashboard:

```sh
./scripts/run_admin.sh
```

The default Admin URL is `http://127.0.0.1:5174`, and the API URL is set through `VITE_ADMIN_API_URL`.
The API's default CORS origins target the gallery dev port `5173`, so allow `5174` before starting the API when the
admin dashboard calls it directly.

```sh
ARTIFACT_API_CORS_ORIGINS=http://localhost:5173,http://127.0.0.1:5173,http://127.0.0.1:5174 \
  python3 -m uvicorn api.app:app --host 0.0.0.0 --port 8000
```

## Validation

```sh
python3 -m unittest discover -s api/tests -t .
python3 -m unittest discover -s crawl_service/tests -t .
cd frontend && npm run build
cd admin-frontend && npm run build
```

If only documentation changes, prioritize link checks and diff review.
