# Crawl Service Processing Layers

This document defines the layers inside `crawl_service` that persist remote morgue source first and regenerate
artifact read models from the stored source later.

The core principle is: **persist remote morgue source first, then make every processing step read only persisted
source**. `raw_morgue_files` is the source of truth for traceability and reprocessing. `artifacts` is a reproducible
read model for the API and frontend.

```text
remote morgue
  -> crawl_service.cli.worker
  -> raw_morgue_files
       fetch_status / fetch_error
       process_status / process_error
       content_hash
       parser_version / scoring_version
  -> crawl_service.core.processor
  -> artifacts
```

## Project Boundary

- Module: `crawl_service/`
- Role: periodically read the remote morgue root user list and persist target users' `txt`/`lst` file source into
  `raw_morgue_files`
- Output: persisted raw morgue file records and crawl file/user state records
- Restriction: does not import `api`, `frontend`, or `admin-frontend` types or components

## Internal Layers

- `crawl_service.morgue`: HTTP fetch for remote morgue root/user directories and file text
- ingest flow: store remote morgue source, compute content hashes, and record fetch state
- `crawl_service.artifacts`: extract artifact raw evidence from txt/lst source, parse names/attributes/classification, evaluate, and build `ArtifactDocument` values
- `crawl_service.core.processor`: read `raw_morgue_files` source and regenerate artifact read models
- `crawl_service.core.repository`: save raw files, write artifacts, replace by source, and save crawl file/user cache records
- `crawl_service.cli.worker`: orchestrate remote morgue source ingest
- `crawl_service.core.observability`: worker pass logging

## Ingest And Processing State

- Fetch success: `raw_morgue_files.fetch_status = fetched`, `process_status = pending`
- Fetch failure: `raw_morgue_files.fetch_status = failed`, `fetch_error` is stored, and processing state is not
  polluted
- Processing success: artifacts are replaced per source, `process_status = processed`, and current parser/scoring
  versions are stored
- Processing failure: `process_status = failed`, `process_error` is stored, and fetch state is preserved
- Reprocessing target: fetched raw files whose `process_status` is `pending`/`failed`, or whose parser/scoring version
  differs from the current version

## Runtime Configuration

- `MORGUE_BASE_URL`: remote morgue root URL. Default: `https://archive.nemelex.cards/morgue`.
- `CRAWL_START_DATE`: start date for eligible user/file data. Default: `2026-01-01`.
- `MORGUE_REQUEST_DELAY_SECONDS`: minimum delay between HTTP requests. Default: `1.0`.
- `CRAWL_LOOP_INTERVAL_SECONDS`: delay between worker passes. Default: `604800` seconds (7 days).
- `MORGUE_REQUEST_TIMEOUT_SECONDS`: HTTP request timeout. Default: the morgue fetcher default.
- `MORGUE_USER_AGENT`: user agent for remote morgue requests.
- `CRAWL_USER_SKIP_MODE`: `conservative` or `modified_at`. Default: `conservative`.
- `CRAWL_LOG_LEVEL`: worker logging level. Default: `INFO`.

## Operation Scripts

- `python3 -m crawl_service.cli.worker`: fetches remote morgue source and stores it in `raw_morgue_files`.
- `crawl_service/run_raw_crawler.sh`: raw ingest worker wrapper. With `DETACH=1`, it runs in the background and writes
  `.logs/crawl_raw_only.log`.
- `crawl_service/process_raw_morgue_files.sh`: processes stored fetched raw files as separate batches.
  `PROCESS_LIMIT` defaults to `1000`; `ONCE=1` processes one batch and exits.

## Related Docs

- [Crawl Service Data Types](./data-types.md)
- [Artifact Scoring Formula](./artifact_scoring_formula.md)
- [Randart Properties](./randart_properties.md)
- [DCSS Item Data](./dcss_item_data.md)
