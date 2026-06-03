# Gallery API

`api`는 MongoDB에 저장된 artifact read model과 crawl status 데이터를 읽어 FastAPI로 제공합니다.
API response model은 `api`가 소유하며, `crawl_service` document model과 중복될 수 있습니다.

`api`는 `crawl_service`를 import하지 않습니다. 두 프로젝트의 경계는 MongoDB에 저장된 문서와
API-owned Pydantic DTO입니다.

## Responsibilities

- `app.py`: FastAPI app factory, CORS 설정, gallery/admin router wiring
- `routes.py`: gallery read endpoints
- `models.py`: artifact API response DTO
- `presenter.py`: persisted artifact document를 public response shape로 변환
- `repository.py`: MongoDB artifact read repository
- `admin_routes.py`: crawl operations dashboard status endpoint
- `admin_models.py`: admin status response DTO
- `admin_repository.py`: crawl file/user/raw file 상태 read repository

## Endpoints

- `GET /artifacts`: artifact list, optional `q`, `type`, `player` filters
- `GET /artifacts/{artifact_id}`: single artifact read
- `GET /artifact-types`: available artifact types
- `GET /filters`: gallery filter metadata
- `GET /admin/crawl-status`: crawl operations dashboard status

## Runtime

dependencies:

```sh
python3 -m pip install -r requirements.txt
```

local MongoDB:

```sh
eval "$(infra/mongo/mongo_up.sh)"
```

API server:

```sh
python3 -m uvicorn api.app:app --host 0.0.0.0 --port 8000
```

기본 CORS origin은 `http://localhost:5173`과 `http://127.0.0.1:5173`입니다.
필요하면 `ARTIFACT_API_CORS_ORIGINS` 또는 `ARTIFACT_API_CORS_ORIGIN_REGEX`로 조정합니다.

## Tests

```sh
python3 -m unittest discover -s api/tests -t .
```

API/frontend contract 변경은 API 테스트와 `cd frontend && npm run build`를 함께 확인합니다.

## Related Shared Docs

- [Processing Layers](docs/reference/processing-layers.md)
- [Data Types](docs/reference/data-types.md)
- [Harness Validation](../docs/ops/harness/validation.md)
