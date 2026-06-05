---
name: dcss-pipeline-orchestrator
description: Coordinate cross-layer DCSS artifact pipeline work across crawl, parsing, scoring, persistence, API, and WebTiles UI specialists.
---

# DCSS Pipeline Orchestrator

## When to Use

Use this skill when a request spans more than one repository boundary or needs routing across existing specialist skills.

Route here for:

- changes that cross `crawl_service/`, `api/`, `frontend/`, and `infra/`
- API/UI contract changes involving `ArtifactDocument`
- crawl-to-persistence workflow changes
- tasks that need implementation plus explicit review or validation planning
- harness updates that affect `.agents/skills/`, `docs/ops/harness/`, module `docs/`, or `_workspace/`

Do not use this skill for a narrow single-layer fix when `bugfix`, `test-generation`, `code-review`, or `webtiles-ui` directly covers the task.

## Required Inputs

- user request and expected observable outcome
- relevant contract docs:
  - `docs/README.md`
  - `crawl_service/docs/ko/processing-layers.md`
  - `api/docs/ko/processing-layers.md`
  - `frontend/docs/ko/processing-layers.md`
  - `crawl_service/docs/ko/artifact_scoring_formula.md` for scoring changes
  - `frontend/docs/ko/style-sources.md` for WebTiles UI changes
- current code slice for every touched boundary
- existing tests or validation commands from `docs/ops/harness/validation.md`

## Workflow

1. Classify the request against `docs/ops/harness/team-spec.md`.
2. Read the smallest relevant code and docs before editing.
3. Select specialist behavior:
   - `bugfix` for implementation or behavior changes
   - `test-generation` when regression coverage is needed
   - `webtiles-ui` for DCSS/WebTiles frontend fidelity
   - `code-review` for findings-first review or high-risk contract checks
4. Preserve the service boundaries:
   - `crawl_service` orchestrates morgue fetch/cache/progress/persist work and owns artifact document construction.
   - `api` serves persisted reads through API-owned DTOs and does not import `crawl_service`.
   - `frontend` reads only from the gallery API for persisted artifact data.
5. Write `_workspace/handoffs/` artifacts for multi-phase work or non-obvious decisions.
6. Run scoped validation first, then broader validation for shared contracts.
7. Summarize changed boundaries, commands run, and residual risks.

## Handoff Outputs

Use deterministic files only when they add continuity or audit value:

- `_workspace/handoffs/YYYYMMDD-HHMM-{slug}-analysis.md`
- `_workspace/handoffs/YYYYMMDD-HHMM-{slug}-implementation.md`
- `_workspace/handoffs/YYYYMMDD-HHMM-{slug}-review.md`
- `_workspace/handoffs/YYYYMMDD-HHMM-{slug}-validation.md`

Each handoff should include request summary, boundaries touched, files inspected or changed, tests run, assumptions, and open risks.

## Validation

Use `docs/ops/harness/validation.md` as the command matrix.

Common gates:

```sh
python3 -m unittest discover -s api/tests -t .
python3 -m unittest discover -s crawl_service/tests -t .
cd frontend && npm run build
```

For API/UI detail alignment, use API contract tests and `cd frontend && npm run build`.

## Expected Output

- selected specialist route and rationale
- implementation or review result
- handoff files when useful
- validation commands and results
- explicit note when live crawl or integration validation was intentionally skipped
