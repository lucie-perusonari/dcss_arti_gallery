# Harness Scenario Tests

Use these scenarios to check whether the repo-local harness routes work to the right specialist behavior and preserves the DCSS artifact pipeline boundaries.

## Normal Flow: Cross-Layer Crawl Persistence Change

Prompt:

```text
Change the crawl flow so raw morgue files are stored first, artifacts are regenerated from stored raw files, and the frontend loads the read model through the API server.
```

Expected routing:

- Start with `dcss-pipeline-orchestrator`.
- Use `bugfix` for repository/API/crawl/frontend behavior changes.
- Use `test-generation` for repository and API/crawl regression coverage.
- Use `code-review` behavior if API/frontend contract risk remains after implementation.

Expected artifacts:

- Optional `_workspace/handoffs/YYYYMMDD-HHMM-crawl-persistence-analysis.md` if the task spans multiple turns.
- Code changes that preserve `crawl_service` as raw-source writer/processor and `api` as persisted read service.
- Validation notes with affected project tests and `cd frontend && npm run build`.

Pass criteria:

- Frontend does not call the crawl service directly.
- API reads persisted artifacts from repository.
- Crawl service stores source raw text in `raw_morgue_files` before artifact conversion.
- `crawl_service.processor` owns raw record to artifact document conversion and can reprocess without remote fetch.
- Fetch failure state and processing failure state remain separate.
- Regression tests cover the new repository/API or crawl behavior.

## Normal Flow: WebTiles Detail UI Change

Prompt:

```text
Adjust the artifact detail panel so all random attributes are visible on mobile without losing the DCSS WebTiles look.
```

Expected routing:

- Use `webtiles-ui`.
- Add `bugfix` only if backend fields or frontend API types must change.

Expected artifacts:

- Frontend code/CSS changes.
- Build result from `cd frontend && npm run build`.
- Screenshot or manual state notes when layout fidelity is the main risk.

Pass criteria:

- The first screen remains the usable gallery.
- Detail text still comes from `dcssDescription` or `rawDescription`.
- No decorative replacement breaks WebTiles density or tile usage.

## Failure Flow: Missing Live Crawl Access

Prompt:

```text
Verify that live crawling works against the public morgue archive.
```

Expected routing:

- Use `dcss-pipeline-orchestrator`, then `bugfix` or direct validation depending on the task.
- If live network access is unavailable or not explicitly required, fall back to mocked tests and state that live crawl validation was skipped.

Expected artifacts:

- Validation notes that distinguish mocked crawl coverage from live network verification.
- No change to parser/evaluator/document logic unless a concrete failure is reproduced.

Pass criteria:

- The harness does not invent live crawl results.
- The response names the skipped validation and the command or setup needed to run it locally.

## Near Miss: Findings-Only Review

Prompt:

```text
Review this diff for bugs before I merge it.
```

Expected routing:

- Use `code-review` directly.
- Do not use `bugfix` unless the user asks for fixes after findings.

Pass criteria:

- Findings lead the response.
- File and line evidence is included.
- No files are edited during the review.
