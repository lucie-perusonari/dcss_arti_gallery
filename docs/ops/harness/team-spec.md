# Codex Harness Team Spec

## Domain Summary

This repository contains three independent projects plus one admin dashboard:

```text
remote morgue
  -> crawl_service/ writer project
  -> MongoDB raw_morgue_files source records
  -> MongoDB artifacts read model
  -> api/ read project
  -> frontend/ gallery project
  -> admin-frontend/ operations dashboard
```

`crawl_service` owns archive-wide morgue discovery, request pacing, raw source persistence, parsing, classification, scoring, document construction, Mongo writes, and crawl file/user cache records. The source-of-truth flow is raw file first, process later: `raw_morgue_files` drives artifact regeneration, while `artifacts` is the API-facing read model.

`api` owns Mongo reads, API-specific Pydantic response DTOs, and gallery HTTP endpoints. It must not import `crawl_service`.

`frontend` owns the React/Vite gallery UI and consumes only Gallery API responses.

`admin-frontend` owns the React/Vite crawl operations dashboard and consumes the API admin status endpoint.

Use the existing docs as source of truth for contracts:

- `docs/reference/README.md`
- `crawl_service/docs/reference/data-types.md`
- `crawl_service/docs/reference/processing-layers.md`
- `crawl_service/docs/reference/artifact_scoring_formula.md`
- `crawl_service/docs/reference/randart_properties.md`
- `api/docs/reference/data-types.md`
- `api/docs/reference/processing-layers.md`
- `frontend/docs/reference/data-types.md`
- `frontend/docs/reference/processing-layers.md`
- `admin-frontend/docs/reference/data-types.md`
- `admin-frontend/docs/reference/processing-layers.md`
- `README.md`
- `crawl_service/README.md`
- `api/README.md`
- `frontend/README.md`
- `admin-frontend/README.md`
- `docs/ops/harness/scenarios.md`

## Routing

- Reports, analysis notes, and repository-facing documents should be written in Korean by default. Preserve original language for code identifiers, commands, API fields, external titles, and direct quotes.
- Cross-project requests route through `dcss-pipeline-orchestrator` first.
- Crawl ingest, processor, parser, scorer, and document-build changes route to `bugfix` with `crawl_service` ownership.
- Gallery read API changes route to `bugfix` with `api` ownership and must preserve frontend response compatibility.
- API response-shape work should compare `api.models`, `api.routes`, `frontend/src/types/artifact.ts`, and `frontend/src/api/artifacts.ts`.
- Frontend display or WebTiles fidelity work routes to `webtiles-ui`.
- Test-only work routes to `test-generation`.
- Review/audit requests route to `code-review`.

## Failure Policy

- Do not add imports from `api` to `crawl_service` or from `api` into `crawl_service`.
- Do not reintroduce old root packages: `morgue`, `application`, `artifacts`, `evaluation`, `documents`, `repositories`, or `cli`.
- Do not run live morgue crawls unless the task needs network behavior or the user explicitly asks for it.
- Prefer mocked or fixture-based tests for parser, importer, repository, and API behavior.
- If scoring changes, compare implementation against `crawl_service/docs/reference/artifact_scoring_formula.md`.
- TODO: No formatter, linter, coverage threshold, CI configuration, deployment gate, or release target is defined.
