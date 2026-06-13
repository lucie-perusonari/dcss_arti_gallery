---
name: dcss-pipeline-orchestrator
description: Coordinate cross-layer DCSS artifact pipeline work across crawl, parsing, scoring, persistence, API, and WebTiles UI specialists.
---

# DCSS Pipeline Orchestrator

## When to Use

Use this skill when a request spans more than one repository boundary or needs routing across existing specialist skills.

Route here for:

- changes that cross `crawl_service/`, `arti_parser/`, `api/`, `admin_api/`, `frontend/`, `admin-frontend/`, and `infra/`
- API/UI contract changes involving `ArtifactDocument` or admin status DTOs
- crawl-to-persistence workflow changes
- tasks that need implementation plus explicit review or validation planning
- root `scripts/` migration/removal or relocation into owning services
- harness updates that affect `AGENTS.md`, `.agents/skills/`, README files, module `docs/`, or `_workspace/`

Do not use this skill for a narrow single-layer fix when `bugfix`, `test-generation`, `code-review`, or `webtiles-ui` directly covers the task.

## Required Inputs

- user request and expected observable outcome
- relevant contract docs:
  - `README.md`
  - README files for every touched service
  - `docs/ko/processing-layers.md` and `docs/ko/data-types.md` for every touched service that has them
  - relevant `arti_parser/docs/*.md`, `arti_parser/models.py`, and `arti_parser/processor.py` for parser/scoring/document changes
  - `frontend/docs/ko/style-sources.md` and `frontend/docs/ko/ui-reference.md` for WebTiles UI changes
- current code slice for every touched boundary
- existing tests or validation commands from affected service README files, when validation is explicitly requested or required by task context

## Workflow

1. Classify the request against the repository boundaries and routing rules in this skill.
2. Read the smallest relevant code and docs before editing.
3. Select specialist behavior:
   - `bugfix` for implementation or behavior changes
   - `test-generation` when regression coverage is needed
   - `webtiles-ui` for DCSS/WebTiles frontend fidelity
   - `code-review` for findings-first review or high-risk contract checks
4. Preserve the service boundaries:
   - `crawl_service` orchestrates only morgue fetch/cache/progress/raw-source persist work.
   - `crawl_service` must not own artifact parsing, classification, scoring, document construction, artifact read-model storage, or imports from `arti_parser`.
   - `arti_parser` owns artifact parsing, classification, scoring, document construction, and artifact read-model regeneration/storage from stored raw source.
   - `api` serves persisted reads through API-owned DTOs and does not import `crawl_service`.
   - `frontend` reads only from the gallery API for persisted artifact data.
   - `admin_api` serves crawl operation status through API-owned DTOs and does not import `crawl_service`.
   - `admin-frontend` reads only from the Admin API for crawl operation status.
5. Write `_workspace/handoffs/` artifacts for multi-phase work or non-obvious decisions.
6. Run scoped validation only when explicitly requested or required by task context; choose broader validation only for shared contracts when that validation is requested.
7. Summarize changed boundaries, commands run, and residual risks.

## Repository Boundaries

This repository has six independent projects: `crawl_service`, `arti_parser`, `api`, `admin_api`, `frontend`, and
`admin-frontend`.

The source-of-truth flow is:

```text
remote morgue
  -> crawl_service/ writer project
  -> MongoDB raw_morgue_files source store
  -> arti_parser/ read-model regeneration
  -> MongoDB artifacts read model
  -> api/ read project
  -> frontend/ gallery project
  -> admin_api/ operations read project
  -> admin-frontend/ operations dashboard
```

- `crawl_service` owns remote morgue discovery/fetching, request pacing, raw source persistence, Mongo raw/cache writes, crawl file/user cache records, and the background worker.
- `arti_parser` owns artifact parsing, classification, scoring, `ArtifactDocument` construction, and `artifacts` read-model regeneration/storage from stored raw source.
- `api` owns Gallery API reads, API-owned Pydantic response DTOs, repositories, and routes. It must not import `crawl_service`.
- `admin_api` owns crawl operations status reads, admin API-owned response DTOs, repositories, and routes. It must not import `crawl_service`.
- `frontend` reads persisted artifact data only from the Gallery API.
- `admin-frontend` reads crawl operations status only from the Admin API.
- Root `scripts/` is not an ownership boundary. It is a removal target. Script placement follows the shared script policy: run scripts live under the owning service or `infra/dev` for cross-service dev orchestration; mock/test helpers live in tests; generators live with the generated artifact owner.

## Documentation Rules

- Repository documentation is written in Korean by default. Keep code identifiers, commands, API fields, external titles, and direct quotes in their original language.
- Root `README.md` is only the repository entry point: project overview, independent project list, top-level data flow, and ownership boundaries.
- Service `README.md` files are the entry point for each service. They should describe service purpose, owned and non-owned responsibilities, top-level flow, run commands, key environment variables, dependency installation, test/build commands, and links to detailed docs.
- Service `README.md` files may include a short file/directory index when it helps navigation, but they should not become module-by-module implementation manuals.
- Detailed file responsibilities, processing layers, data types, API contracts, UI rules, and operations policies belong under the owning service docs when that service has docs.
- Do not create a root-level shared `docs/` directory or central validation matrix. Put shared contract authority in the owning service docs, and link to it from consuming service docs.
- Do not add new root `scripts/` entrypoints. Apply the shared script policy uniformly across services for `.sh` files, mock/test helpers, and generation scripts.
- When script policy changes, update affected service README command examples and package scripts in the same change.

## Routing Rules

- Reports, analysis notes, and repository docs are written in Korean by default. Keep code identifiers, commands, API field names, external titles, and direct quotes in the original language.
- Multi-project requests start with this orchestrator.
- Crawl ingest changes route to `crawl_service`; parser/scorer/document-build/artifact read-model regeneration changes route to `arti_parser`.
- Gallery API changes route to `api` behavior through `bugfix`, while preserving frontend response compatibility.
- API response shape work compares `api.models`, `api.routes`, `frontend/src/types/artifact.ts`, and `frontend/src/api/artifacts.ts`.
- Admin status contract work compares `admin_api.models`, `admin_api.routes`, `admin-frontend/src/types/status.ts`, and `admin-frontend/src/api/status.ts`.
- WebTiles/gallery display fidelity work routes to `webtiles-ui`.
- Test-only work routes to `test-generation`.
- Review or audit requests route to `code-review`.

## Common Work Surfaces

- Remote crawl fetch: `crawl_service/fetcher.py`
- Raw source persistence and duplicate state: `crawl_service/repository.py`
- Artifact document creation from raw source: `arti_parser.processor`
- Artifact read-model regeneration batch: `arti_parser.batch`
- Artifact parsing/classification/scoring/document generation: `arti_parser/`
- Crawl orchestration: `crawl_service/worker.py`
- Gallery API: `api/`
- Operations status API: `admin_api/`
- Mongo lifecycle scripts: development in `infra/dev/`, production in `infra/prod/`
- Gallery frontend: `frontend/`
- Operations dashboard: `admin-frontend/`
- Existing root `scripts/`: migration/removal candidates governed by the shared script policy, not a target for new ownership

## Routing Examples

- Crawl persistence or read-model flow changes: start here, then use `bugfix` for the implementation slice; add `test-generation` only when tests are explicitly requested; use `code-review` if contract risk remains.
- WebTiles detail UI changes: use `webtiles-ui` first; add `bugfix` only if API contract or data behavior changes.
- Live crawl verification requests: prefer mock/fixture validation unless live network verification is explicitly requested and available.
- Review-only requests: use `code-review` only and do not edit code unless the user explicitly asks for fixes.

## Handoff Outputs

Use deterministic files only when they add continuity or audit value:

- `_workspace/handoffs/YYYYMMDD-HHMM-{slug}-analysis.md`
- `_workspace/handoffs/YYYYMMDD-HHMM-{slug}-implementation.md`
- `_workspace/handoffs/YYYYMMDD-HHMM-{slug}-review.md`
- `_workspace/handoffs/YYYYMMDD-HHMM-{slug}-validation.md`

Each handoff should include request summary, boundaries touched, files inspected or changed, validation run or intentionally skipped, assumptions, and open risks.

## Validation

Use the affected service README test or build section as the command source only when validation is explicitly requested or required by task context.

For cross-service changes, combine the relevant test or build commands from each affected service README.

## Expected Output

- selected specialist route and rationale
- implementation or review result
- handoff files when useful
- validation commands and results, or explicit note that validation was not run because it was not requested
- explicit note when live crawl or integration validation was intentionally skipped
