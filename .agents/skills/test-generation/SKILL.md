---
name: test-generation
description: Use only when the user explicitly asks to add, update, or design tests for the DCSS artifact pipeline.
---

# Test Generation

## When to Use

Use this skill only when the current request explicitly asks for test creation, test updates, coverage, regression tests, or test strategy.

Do not use this skill for ordinary bug fixes, implementation changes, refactors, documentation updates, or validation decisions unless the current task explicitly requests tests.

Prefer this skill for:

- parser fixtures from txt/lst morgue snippets
- randart filtering and classification invariants
- scoring formula regressions
- ArtifactDocument and FastAPI response shape
- `arti_parser` read-model regeneration and repository behavior
- crawl raw-source repository behavior
- local Mongo lifecycle script behavior
- frontend type/build validation
- mock/fake API behavior owned by test files or test packages

## Required Inputs

- Behavior to protect
- Existing tests for the affected layer
- Affected service README and contract docs for the layer
- Small fixture strings or fake repositories/clients where possible

## Workflow

1. Read the nearest existing test file and match its style.
2. Write the narrowest test that would fail without the desired behavior.
3. Prefer fixtures, fake repositories, and mocked HTTP clients over live network or Docker dependencies.
4. For parser tests, preserve raw line shape and source metadata where relevant.
5. For scoring tests, state whether base attributes or random attributes are expected to influence the result.
6. For API/frontend contract tests, compare `ArtifactDocument` fields with `api` DTOs and `frontend/src/types/artifact.ts`; run frontend build only when build validation is explicitly requested or required by task context.
7. For admin contract tests, compare `admin_api` DTOs with `admin-frontend/src/types/status.ts`.
8. Keep mock server/client helpers and fixture/mock generation logic inside the relevant test file or test package, not in root `scripts/`.
9. Run tests only when the current task explicitly asks for validation, or when the task context or affected service README requires it.

## Validation

Use the affected service README as the source of truth. For cross-service tests, combine the relevant test or build
commands from each affected service README.

## Expected Output

- Test files changed or added
- Command results when tests were explicitly requested or required; otherwise state that tests were not run
- Any intentionally untested behavior and why
- Follow-up TODO only when the repository lacks the needed test surface, such as a frontend unit test runner
