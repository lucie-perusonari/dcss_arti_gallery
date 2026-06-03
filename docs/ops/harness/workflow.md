# Harness Workflow

## Default Flow

1. Identify the owning project: `crawl_service`, `api`, or `frontend`.
2. Read the smallest relevant code and tests inside that project.
3. Write reports, analysis notes, and repository-facing documents in Korean by default; keep code identifiers, commands, API fields, external titles, and direct quotes in their original language.
4. Preserve project independence:
   - `crawl_service` writes raw morgue sources, regenerates artifact read models, and owns crawl cache state.
   - `api` reads artifacts through API-owned DTOs and repositories.
   - `frontend` consumes only the Gallery API.
5. Run validation per project; for contract changes, run each affected project gate.

## Common Surfaces

- Crawl remote fetch: `crawl_service/morgue/`
- Raw source persistence and processing state: `crawl_service/repository.py`
- Raw source to artifact read model processing: `crawl_service/processor.py`
- Artifact parsing/classification: `crawl_service/domain/artifacts/`
- Scoring: `crawl_service/domain/evaluation/`
- Crawl document construction: `crawl_service/domain/documents/`
- Crawl orchestration: `crawl_service/worker.py`
- Gallery read API: `api/`
- Mongo lifecycle scripts: `infra/mongo/`
- Frontend gallery: `frontend/`

## Validation

- Cross-project changes: `python3 -m unittest discover -s api/tests -t .`, `python3 -m unittest discover -s crawl_service/tests -t .`, and `cd frontend && npm run build`
- API-only changes: `python3 -m unittest discover -s api/tests -t .`
- Crawl-only changes: targeted `crawl_service/tests` tests, then `python3 -m unittest discover -s crawl_service/tests -t .` if broader crawl behavior changed
- Frontend-only changes: `cd frontend && npm run build`
