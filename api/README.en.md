# Gallery API

`api` reads artifact read models and crawl status data stored in MongoDB and serves them through FastAPI.
The API response model is owned by `api` and may duplicate the `crawl_service` document model.

`api` does not import `crawl_service`. The boundary between the two projects is the MongoDB-stored document shape
and the API-owned Pydantic DTOs.

## Responsibilities

- `app.py`: FastAPI app factory, CORS setup, and gallery/admin router wiring
- `routes.py`: gallery read endpoints
- `models.py`: artifact API response DTOs
- `presenter.py`: converts persisted artifact documents into public response shapes
- `repository.py`: MongoDB artifact read repository
- `admin_routes.py`: crawl operations dashboard status endpoints
- `admin_models.py`: admin status response DTOs
- `admin_repository.py`: read repository for crawl file/user/raw file status

## Endpoints

- `GET /artifacts`: list artifacts with `q`, `type`, and `player` filters
- `GET /artifacts/{artifact_id}`: read a single artifact
- `GET /artifact-types`: list available artifact types
- `GET /filters`: gallery filter metadata
- `GET /admin/crawl-status`: crawl operations dashboard status

## Runtime

Dependencies:

```sh
python3 -m pip install -r requirements.txt
```

Local MongoDB:

```sh
eval "$(infra/mongo/mongo_up.sh)"
```

API server:

```sh
python3 -m uvicorn api.app:app --host 0.0.0.0 --port 8000
```

The default CORS origins are `http://localhost:5173` and `http://127.0.0.1:5173`.
Adjust them with `ARTIFACT_API_CORS_ORIGINS` or `ARTIFACT_API_CORS_ORIGIN_REGEX` if needed.

## Tests

```sh
python3 -m unittest discover -s api/tests -t .
```

When the API/frontend contract changes, run the API tests together with `cd frontend && npm run build`.

## Related Docs

- [Processing Layers](docs/en/processing-layers.md)
- [Data Types](docs/en/data-types.md)
