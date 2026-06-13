# DCSS Arti Gallery

This repository collects random artifact information from Dungeon Crawl Stone Soup morgue logs and `lst` files,
separates random properties that do not exist on the base item, and presents them as a gallery.

The repository contains several independent modules in one checkout. The root README only introduces the project and
lists the modules. Use each module's `README.md` for execution, tests, environment variables, and local structure.

## Modules

- [crawl_service](crawl_service/README.en.md): remote morgue discovery/fetch, raw morgue source storage, crawl status records, background worker
- [arti_parser](arti_parser/README.md): parses stored raw morgue source and regenerates the `artifacts` read model
- [api](api/README.en.md): artifact read API for the gallery, API-owned DTOs, FastAPI routes
- [admin_api](admin_api/README.en.md): crawl/processing operations status and Gallery API metrics read API, admin API-owned DTOs, FastAPI routes
- [frontend](frontend/README.en.md): React/Vite WebTiles-style artifact gallery
- [admin-frontend](admin-frontend/README.en.md): React/Vite crawl operations dashboard
- [infra](infra/README.md): development/production Docker Compose stacks and environment policy

## Data Flow

```text
remote morgue
  -> crawl_service
  -> raw_morgue_files
  -> arti_parser
  -> artifacts
  -> api
  -> frontend

crawl status collections
artifact_processing_files
Prometheus Gallery API metrics
  -> admin_api
  -> admin-frontend
```

`crawl_service` only owns remote source collection and raw storage. `arti_parser` owns artifact parsing, scoring, and
read-model generation. The gallery and operations dashboard read data only through `api` and `admin_api`, respectively.

## Responsibility Boundaries

- `crawl_service` owns remote morgue discovery, raw morgue source storage, crawl status records, and the background worker only. It does not own artifact parsing, classification, scoring, or `artifacts` storage.
- `arti_parser` uses stored `raw_morgue_files` as input, parses random artifacts, scores them, and regenerates the `artifacts` read model. It does not fetch remote morgues or serve HTTP APIs.
- `api` reads the `artifacts` read model and serves Gallery API responses. The public API contract is owned by `api` DTOs, and `api` does not import `crawl_service` internals.
- `admin_api` reads crawl status collections, artifact processing status, and internal Prometheus Gallery API metrics,
  then serves operations dashboard API responses. It does not directly depend on crawl worker internals.
- `frontend` owns the gallery UI and reads persisted artifact data only through the Gallery API.
- `admin-frontend` owns the operations dashboard and reads crawl status data only through the Admin API.
- `infra` owns development/production Docker Compose stacks and infrastructure work such as MongoDB indexes. Application repositories do not take over infra DDL.
- Root `scripts/` is a removal target. Run scripts belong under the appropriate service. Mock validation logic and test fixture generators belong in test files or test packages. Keep only generation scripts that are essential to runtime logic, and document why they cannot be replaced by runtime code, hand-maintained constants, or test fixtures.
