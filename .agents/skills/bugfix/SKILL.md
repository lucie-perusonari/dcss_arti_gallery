---
name: bugfix
description: Fix defects or implement narrow single-boundary behavior changes in the DCSS artifact crawl, parser, API, or gallery pipeline.
---

# Bugfix

## When to Use

Use this skill when a request asks for a defect fix, a focused implementation change, or a behavior adjustment that fits one project boundary or one adjacent API/UI contract boundary.

Route here for:

- remote morgue discovery, crawl writer flow, and file fetching
- raw morgue source persistence and crawl status recording
- txt/lst artifact extraction, parsing, classification, base/random attribute separation, scoring, and `ArtifactDocument` construction in `arti_parser`
- `artifacts` read-model persistence and regeneration in `arti_parser`
- Gallery API or Admin API endpoint behavior
- frontend or admin frontend API integration behavior
- Mongo lifecycle scripts under `infra/` when they affect local persistence flows

Do not use this skill for a findings-only code review. Use `code-review` instead. Do not use this skill as the first stop for multi-project ownership, root `scripts/` migration, or data-flow changes; start with `dcss-pipeline-orchestrator`. For pure WebTiles layout fidelity work, use `webtiles-ui` first and add this skill only when data behavior also changes.

## Required Inputs

- User request and expected observable behavior
- Smallest relevant code slice
- Relevant contract docs:
  - `README.md`
  - affected service `README.md`
  - affected service `docs/ko/processing-layers.md` and `docs/ko/data-types.md`, when present
  - relevant `arti_parser/docs/*.md`, `arti_parser/models.py`, and `arti_parser/processor.py` for artifact parsing, scoring, or document construction changes
  - `admin_api/docs/ko/data-types.md` and `admin-frontend/docs/ko/data-types.md` for admin status contract changes
- Existing tests or validation commands for the affected layer, when the current task explicitly asks for them

## Workflow

1. Localize the behavior to one project boundary before editing. If the requested change spans multiple ownership boundaries, switch to `dcss-pipeline-orchestrator`.
2. Reproduce with the narrowest safe fixture, local reasoning path, or existing test when validation is explicitly requested.
3. Preserve the layer contract documented in the affected service README or docs.
4. Make the smallest code change that fixes the behavior without merging parser, classifier, evaluator, repository, API, and UI responsibilities.
5. Add or update focused regression coverage only when the user request, task instructions, or related context explicitly asks for tests.
6. Run scoped validation only when explicitly requested or required by task context; choose the smallest matching command before broader validation.
7. Record a handoff under `_workspace/handoffs/` when the fix spans multiple layers or leaves an important decision trail.

## Boundary Rules

- Parser changes should preserve raw morgue evidence: source file, URL, line number, visible description, and location when available.
- Classifier changes must keep `all_attributes`, `base_attributes`, and `random_attributes` meaningfully separate.
- Evaluator changes should score `RandomArtifact.random_attributes`, not intrinsic base item properties, unless the scoring spec is intentionally updated.
- Artifact document and artifact read-model regeneration changes belong in `arti_parser`, not `crawl_service`, and must be reflected in persisted Mongo shape, `api/models.py`, and frontend API usage when the public shape changes.
- API response changes must be reflected in `api/models.py`, `api/`, `frontend/src/types/artifact.ts`, and frontend API usage.
- Admin API response changes must be reflected in `admin_api/models.py`, `admin_api/`, `admin-frontend/src/types/status.ts`, and admin frontend API usage.
- Crawl service changes should keep `crawl_service` as the morgue fetch/cache/progress/raw-source persist orchestrator only; it must not import `arti_parser` or own artifact processing/storage.
- Admin status changes must not require `admin_api` to import crawl internals.
- Do not add new root `scripts/` entrypoints. Apply the shared script policy: `.sh` run scripts go under the owning service or `infra/dev` for cross-service dev orchestration, mock/test helpers go in tests, and generators go with the generated artifact owner.
- Network-facing validation should use mocked tests when validation is explicitly requested; live crawling still requires an explicit user request.

## Validation

When validation is explicitly requested or required by task context, choose the smallest matching command from the affected service README.

For cross-service changes, combine the relevant test or build commands from each affected service README.

## Expected Output

- Code change scoped to one affected project boundary or one adjacent contract boundary
- Tests or a clear reason tests were not added
- Commands run and results
- Remaining risks or TODOs, if any
