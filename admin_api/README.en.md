# Admin API

`admin_api` reads MongoDB crawl operations status collections and serves read-only FastAPI endpoints for the admin
dashboard. Response DTOs and repositories are owned by `admin_api`, and it does not import `crawl_service`.

## Responsibilities

- `app.py`: admin FastAPI app factory, CORS setup, and admin router wiring
- `routes.py`: crawl operations dashboard status endpoints
- `models.py`: admin status response DTOs
- `repository.py`: read repository for crawl file/user/raw file status
- `run_admin_api.sh`: Admin API dev server wrapper with the dev MongoDB environment

## Endpoints

- `GET /admin/crawl-status`: crawl operations dashboard status

## Runtime

Dependencies:

```sh
python3 -m pip install -r requirements.txt
```

Local MongoDB:

```sh
eval "$(infra/dev/mongo_up.sh)"
```

Admin API server:

```sh
python3 -m uvicorn admin_api.app:app --host 0.0.0.0 --port 8001
```

From the repository root, you can use the service script:

```sh
./admin_api/run_admin_api.sh
```

The admin API default CORS origins are `http://localhost:5174` and `http://127.0.0.1:5174`.
`ADMIN_CRAWL_STATUS_CACHE_SECONDS` controls the in-process `/admin/crawl-status` cache TTL and defaults to `5` seconds.
Adjust them with `ADMIN_API_CORS_ORIGINS` or `ADMIN_API_CORS_ORIGIN_REGEX` if needed.

## Tests

```sh
python3 -m unittest discover -s admin_api/tests -t .
```

When the admin status contract changes, run the admin API tests together with `cd admin-frontend && npm run build`.

## Related Docs

- [Processing Layers](docs/en/processing-layers.md)
- [Data Types](docs/en/data-types.md)
