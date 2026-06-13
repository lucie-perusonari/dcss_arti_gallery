# Gallery API

`api` reads artifact read models stored in MongoDB and serves gallery FastAPI endpoints.
The API response model is owned by `api` and may duplicate the `crawl_service` document model.

`api` does not import `crawl_service`. The boundary between the two projects is the MongoDB-stored document shape
and the API-owned Pydantic DTOs.

## Responsibilities

- `app.py`: gallery FastAPI app factory, CORS setup, and gallery router wiring
- `routes.py`: gallery read endpoints
- `models.py`: artifact API response DTOs
- `presenter.py`: converts persisted artifact documents into public response shapes
- `repository.py`: MongoDB artifact read repository. DDL such as index creation is owned by `infra/`.

## Endpoints

- `GET /artifacts`: list artifacts with `q`, `type`, and `player` filters
- `GET /artifacts/{artifact_id}`: read a single artifact
- `GET /artifact-types`: list available artifact types
- `GET /filters`: gallery filter metadata

## Runtime

Dependencies:

```sh
python3 -m pip install -r requirements.txt
```

Local MongoDB:

```sh
docker compose -f infra/dev/docker-compose.yml up -d mongo mongo-indexes
```

Gallery API server:

```sh
python3 -m uvicorn api.app:app --host 0.0.0.0 --port 8000
```

The gallery API default CORS origins are `http://localhost:5173` and `http://127.0.0.1:5173`.
Adjust them with `ARTIFACT_API_CORS_ORIGINS` or `ARTIFACT_API_CORS_ORIGIN_REGEX` if needed.

## Tests

```sh
python3 -m unittest discover -s api/tests -t .
```

The API tests verify that Gallery API responses expose only the fields required by the frontend `Artifact` contract.

## Related Docs

- [Processing Layers](docs/en/processing-layers.md)
- [Data Types](docs/en/data-types.md)
