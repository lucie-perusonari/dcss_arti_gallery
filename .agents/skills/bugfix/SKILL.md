---
name: bugfix
description: Fix defects or implement narrow behavior changes in the DCSS artifact crawl, scoring, storage, API, or gallery pipeline.
---

# Bugfix

## When to Use

Use this skill when a request asks for a defect fix, a focused implementation change, or a behavior adjustment in the DCSS random artifact system.

Route here for:

- remote morgue discovery, crawl writer flow, and file fetching
- txt/lst artifact extraction and parsing
- randart classification, base/random attribute separation, or scoring
- ArtifactDocument construction, JSON import/export, persistence, or FastAPI endpoints
- frontend API integration and artifact gallery behavior
- Mongo lifecycle scripts when they affect local persistence flows

Do not use this skill for a findings-only code review. Use `code-review` instead. For pure WebTiles layout fidelity work, use `webtiles-ui` first and add this skill only when code behavior also changes.

## Required Inputs

- User request and expected observable behavior
- Smallest relevant code slice
- Relevant contract docs:
  - `docs/README.md`
  - relevant module `docs/ko/processing-layers.md`
  - relevant module `docs/ko/data-types.md`
  - `crawl_service/docs/ko/artifact_scoring_formula.md` for scoring changes
  - `crawl_service/docs/ko/randart_properties.md` for randart token handling
- Existing tests that cover the affected layer

## Workflow

1. Localize the behavior to one pipeline boundary before editing.
2. Reproduce with the narrowest existing test or a small fixture.
3. Preserve the layer contract documented in the relevant module `docs/ko/processing-layers.md`.
4. Make the smallest code change that fixes the behavior without merging parser, classifier, evaluator, repository, API, and UI responsibilities.
5. Add or update focused regression coverage when the behavior can plausibly break again.
6. Run scoped validation first, then broader validation when contracts or shared code changed.
7. Record a handoff under `_workspace/handoffs/` when the fix spans multiple layers or leaves an important decision trail.

## Boundary Rules

- Parser changes should preserve raw morgue evidence: source file, URL, line number, visible description, and location when available.
- Classifier changes must keep `all_attributes`, `base_attributes`, and `random_attributes` meaningfully separate.
- Evaluator changes should score `RandomArtifact.random_attributes`, not intrinsic base item properties, unless the scoring spec is intentionally updated.
- Crawl document changes must be reflected in `crawl_service/domain/documents/` and `crawl_service/repository.py`.
- API response changes must be reflected in `api/models.py`, `api/`, `frontend/src/types/artifact.ts`, and frontend API usage.
- Crawl service changes should keep `crawl_service` as the fetch/cache/progress/persist orchestrator and must not require `api` to import crawl internals.
- Network-facing changes should be covered with mocked tests unless live crawling is explicitly requested.

## Validation

Choose the smallest matching command from `docs/ops/harness/validation.md`.

Common gates:

```sh
python3 -m unittest discover -s api/tests -t .
python3 -m unittest discover -s crawl_service/tests -t .
cd frontend && npm run build
```

For API/UI display text alignment, use API contract tests and `cd frontend && npm run build`.

## Expected Output

- Code change scoped to the affected layer or adjacent contract boundary
- Tests or a clear reason tests were not added
- Commands run and results
- Remaining risks or TODOs, if any
