---
name: test-generation
description: Add focused regression and contract tests for the DCSS artifact parser, classifier, evaluator, repository, API, and frontend build surfaces.
---

# Test Generation

## When to Use

Use this skill when a request asks for tests, coverage, regression protection, or when an implementation change needs focused validation.

Prefer this skill for:

- parser fixtures from txt/lst morgue snippets
- randart filtering and classification invariants
- scoring formula regressions
- ArtifactDocument and FastAPI response shape
- repository import/export behavior
- local Mongo script behavior
- frontend type/build validation

## Required Inputs

- Behavior to protect
- Existing tests for the affected layer
- Contract docs for the layer
- Small fixture strings or fake repositories/clients where possible

## Workflow

1. Read the nearest existing test file and match its style.
2. Write the narrowest test that would fail without the desired behavior.
3. Prefer fixtures, fake repositories, and mocked HTTP clients over live network or Docker dependencies.
4. For parser tests, preserve raw line shape and source metadata where relevant.
5. For scoring tests, state whether base attributes or random attributes are expected to influence the result.
6. For API/frontend contract tests, compare `ArtifactDocument` fields with `frontend/src/types/artifact.ts` and run the frontend build when TypeScript shape matters.
7. Run the scoped test command, then broader validation if shared behavior changed.

## Validation Matrix

Use `docs/ops/harness/validation.md` as the source of truth.

Common scoped commands:

```sh
python3 -m unittest discover -s crawl_service/tests/domain/artifacts -t .
python3 -m unittest discover -s crawl_service/tests/domain/evaluation -t .
python3 -m unittest discover -s api/tests -t .
cd frontend && npm run build
```

## Expected Output

- Test files changed or added
- Command results
- Any intentionally untested behavior and why
- Follow-up TODO only when the repository lacks the needed test surface, such as a frontend unit test runner
