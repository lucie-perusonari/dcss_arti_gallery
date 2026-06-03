---
name: code-review
description: Review DCSS artifact crawler, evaluator, API, persistence, and WebTiles-style gallery changes for defects and contract regressions.
---

# Code Review

## When to Use

Use this skill when the user asks for a review, audit, pre-merge check, risk assessment, or "look over this" style request.

This is a findings-first review. Do not rewrite code unless the user explicitly asks for fixes.

## Required Inputs

- The user request and review scope
- Current diff or named files
- Relevant docs for the touched layer:
  - `docs/reference/README.md`
  - relevant module `docs/reference/data-types.md`
  - relevant module `docs/reference/processing-layers.md`
  - `crawl_service/docs/reference/artifact_scoring_formula.md`
  - `crawl_service/docs/reference/randart_properties.md`
  - `frontend/public/STYLE_SOURCES.md` for WebTiles UI changes
- Relevant tests and validation output, if available

## Workflow

1. Identify changed files with `git status --short` and inspect only relevant diffs or files.
2. Map each change to its pipeline boundary.
3. Check for behavior regressions, contract mismatches, scoring mistakes, missing persistence handling, API/frontend type drift, and missing tests.
4. For frontend changes, check layout fidelity, text overflow risk, keyboard/mouse ergonomics, API fallback behavior, and tile/font/source assumptions.
5. Lead with findings ordered by severity. Use file and line references.
6. Add open questions or assumptions only after findings.
7. Keep summary secondary and brief.

## Review Criteria

- Morgue parsing must keep enough raw evidence to debug source-specific failures.
- Randart scoring must not over-score base item intrinsic properties.
- API response fields must stay aligned with `ArtifactDocument` and frontend TypeScript types.
- Gallery UI should preserve the DCSS/WebTiles item description feel where that is the requested surface.
- Tests should cover parser fixtures, classifier/evaluator invariants, API document shape, or frontend build failures according to the changed layer.

## Expected Output

Use this shape:

```text
Findings
- [severity] path:line - issue, impact, and why it matters.

Open Questions
- Question or assumption, if any.

Summary
- Brief change summary or residual risk.
```

If no issues are found, state that clearly and mention remaining test gaps or residual risk.
