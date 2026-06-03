# Repository Agents Guide

## What

- This repository contains three independent projects: `crawl_service`, `api`, and `frontend`.
- `crawl_service` owns remote morgue fetch, parsing, classification, evaluation, artifact document creation, MongoDB writes, crawl file/user cache records, and the background crawl worker.
- `api` owns the gallery read API. It reads MongoDB artifacts through API-owned repository and Pydantic response models, and it must not import `crawl_service`.
- `frontend` is a React + TypeScript + Vite app in `frontend/` and talks to the gallery API.
- Local MongoDB lifecycle scripts live in `infra/mongo/`.

## Why

- Treat `crawl_service` and `api` as separate projects even though they share this repository.
- API response models may duplicate crawl document models; that duplication is intentional because the API owns its public contract.
- Artifact evaluation should be based on `RandomArtifact.random_attributes`; base item attributes are separated to avoid over-scoring intrinsic item properties.
- API and frontend types must stay aligned because the gallery renders artifact fields directly.

## How

- Write reports, analysis notes, and repository documentation in Korean by default. Keep code identifiers, commands, API field names, and quoted source text in their original language.
- Install Python dependencies with `python3 -m pip install -r requirements.txt`.
- Run API tests with `python3 -m unittest discover -s api/tests -t .`.
- Run crawl service tests with `python3 -m unittest discover -s crawl_service/tests -t .`.
- Install frontend dependencies with `cd frontend && npm install`.
- Run the frontend production build with `cd frontend && npm run build`.
- Start local MongoDB with `eval "$(infra/mongo/mongo_up.sh)"`.
- Start the crawl worker with `python3 -m crawl_service.worker`.
- Start the API with `python3 -m uvicorn api.app:app --host 0.0.0.0 --port 8000`.
- Start the frontend dev server with `./scripts/run_frontend.sh` or `cd frontend && VITE_ARTIFACT_API_URL=http://127.0.0.1:8000 npm run dev -- --host 127.0.0.1 --port 5173`.
- Use `docs/harness/team-spec.md` for routing, ownership, and failure policy.
- Use `docs/harness/workflow.md` for the default work sequence.
- Use `docs/harness/validation.md` for scoped and cross-project validation gates.
- For multi-boundary work, start with `.agents/skills/dcss-pipeline-orchestrator/SKILL.md`; route narrow fixes, reviews, tests, and WebTiles UI work to the matching repo-local skill.
- Do not run live morgue crawls unless network behavior is required or explicitly requested.

## TODO

- No repository-wide Python version, virtual environment manager, formatter, linter, or deployment target is defined yet.
