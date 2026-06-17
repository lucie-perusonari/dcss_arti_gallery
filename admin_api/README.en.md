# Admin API

`admin_api` reads MongoDB crawl operations status collections and the internal Prometheus API, then serves read-only
FastAPI endpoints for the admin dashboard. Response DTOs and repositories are owned by `admin_api`, and it does not
import `crawl_service`.

## Modules

- [`app.py`](docs/ko/app.md): admin FastAPI app factory, CORS setup, and admin router wiring
- [`routes.py`](docs/ko/routes.md): crawl operations dashboard status endpoints
- [`models.py`](docs/ko/models.md): admin status response DTOs
- [`repository.py`](docs/ko/repository.md): read repository for crawl file/user/raw file status
- [`prometheus.py`](docs/ko/prometheus.md): Gallery API metrics read repository backed by the Prometheus HTTP API
- [`tests/`](docs/ko/tests.md): Admin API response contract and MongoDB read checks

## Endpoints

- `GET /admin/crawl-status`: crawl operations dashboard status
- `GET /admin/metrics/gallery-api`: Gallery API request/latency metrics read from Prometheus

## Runtime

Dependencies:

```sh
python3 -m pip install -r requirements.txt
```

Local MongoDB:

```sh
docker compose -f infra/dev/docker-compose.yml up -d mongo mongo-indexes
```

Admin API server:

```sh
python3 -m uvicorn admin_api.app:app --host 0.0.0.0 --port 8001
```

In the full development stack, compose manages the Admin API runtime and MongoDB connection environment together:

```sh
docker compose -f infra/dev/docker-compose.yml up admin-api
```

The admin API default CORS origins are `http://localhost:5174` and `http://127.0.0.1:5174`.
`ADMIN_CRAWL_STATUS_CACHE_SECONDS` controls the in-process `/admin/crawl-status` cache TTL and defaults to `5` seconds.
Adjust them with `ADMIN_API_CORS_ORIGINS` or `ADMIN_API_CORS_ORIGIN_REGEX` if needed.
Gallery API metrics use `PROMETHEUS_URL`, defaulting to `http://localhost:9090`.
`PROMETHEUS_TIMEOUT_SECONDS` defaults to `3`, and `PROMETHEUS_METRICS_WINDOW_SECONDS` defaults to `300`.
Artifact processing status is read from `MONGODB_ARTIFACT_PROCESSING_COLLECTION`, defaulting to `artifact_processing_files`.

Key MongoDB environment variables:

| Environment variable | Default | Description |
| --- | --- | --- |
| `MONGODB_URI` | `mongodb://localhost:27018` | MongoDB connection string. Compose injects `mongodb://mongo:27017` internally. |
| `MONGODB_DATABASE` | `dcss_arti_gallery` | Database name. |
| `MONGODB_COLLECTION` | `artifacts` | Collection used for artifact counts. |
| `MONGODB_RAW_FILES_COLLECTION` | `raw_morgue_files` | Collection read for raw fetch/process status. |
| `MONGODB_CRAWL_ERRORS_COLLECTION` | `crawl_errors` | Crawl failure event log collection. |
| `MONGODB_ARTIFACT_PROCESSING_COLLECTION` | `artifact_processing_files` | Artifact processing status collection. |

## Tests

```sh
python3 -m unittest discover -s admin_api/tests -t .
```

When the admin status contract changes, run the admin API tests together with `cd admin-frontend && npm run build`.

## Related Docs

- [Processing Layers](docs/en/processing-layers.md)
- [Data Types](docs/en/data-types.md)
