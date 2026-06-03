# Harness Validation

## Verified Commands

These commands are the standard gates for this workspace.

| Surface | Command |
| --- | --- |
| API tests | `python3 -m unittest discover -s api/tests -t .` |
| Crawl service tests | `python3 -m unittest discover -s crawl_service/tests -t .` |
| Frontend build | `cd frontend && npm run build` |

Known warnings:

- Python tests may emit a FastAPI/Starlette `TestClient` deprecation warning about `httpx`.
- Mongo-backed tests may emit `MongoClient.close()` `ResourceWarning` messages.

## Standard Validation Matrix

| Change area | Minimum validation |
| --- | --- |
| Crawl service morgue fetch | `python3 -m unittest discover -s crawl_service/tests/morgue -t .` |
| Crawl service artifact domain | `python3 -m unittest discover -s crawl_service/tests/domain/artifacts -t .` |
| Crawl service scoring | `python3 -m unittest discover -s crawl_service/tests/domain/evaluation -t .` and compare `crawl_service/docs/reference/artifact_scoring_formula.md` |
| Crawl service document/write flow | `python3 -m unittest discover -s crawl_service/tests/domain/documents -t . && python3 -m unittest discover -s crawl_service/tests -t .` |
| Gallery API read contract | `python3 -m unittest discover -s api/tests -t .` |
| Frontend UI/API client | `cd frontend && npm run build` |
| Cross-project changes | `python3 -m unittest discover -s api/tests -t .`, `python3 -m unittest discover -s crawl_service/tests -t .`, and `cd frontend && npm run build` |

## Optional Local Integration

Use these only when the task needs MongoDB or end-to-end API behavior.

```sh
eval "$(infra/mongo/mongo_up.sh)"
python3 -m crawl_service.worker
python3 -m uvicorn api.app:app --host 0.0.0.0 --port 8000
cd frontend
VITE_ARTIFACT_API_URL=http://127.0.0.1:8000 npm run dev -- --host 127.0.0.1 --port 5173
```

For frontend-only mock review:

```sh
./scripts/run_frontend.sh
```

## Quality Gates

- `api` must not import `crawl_service`.
- API field changes must be checked against `api.models`, FastAPI responses, frontend TypeScript types, and UI usage.
- Crawl worker/document changes must be checked against `crawl_service.worker`, `crawl_service.domain.documents`, `crawl_service.repository`, and API DTO compatibility.
- Scoring changes must explain whether they affect only `random_attributes` or also base item handling.
- Network-facing changes should have mocked tests unless the user explicitly asks for live crawl verification.
- TODO: No formatter, linter, coverage threshold, CI configuration, or deployment gate is defined in the repository.
