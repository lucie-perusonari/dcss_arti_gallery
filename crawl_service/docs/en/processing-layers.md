# Crawl Service Processing Layers

This document defines the layers inside `crawl_service` that persist remote morgue source first and regenerate
artifact read models from the stored source later.

The core principle is: **persist remote morgue source first, then make every processing step read only persisted
source**. `raw_morgue_files` is the source of truth for traceability and reprocessing. `artifacts` is a reproducible
read model for the API and frontend.

```text
remote morgue
  -> crawl_service.worker
  -> raw_morgue_files
       fetch_status / fetch_error
       process_status / process_error
       content_hash
       parser_version / scoring_version
  -> crawl_service.processor
  -> artifacts
```

## Project Boundary

- Module: `crawl_service/`
- Role: periodically read the remote morgue root user list and persist target users' `txt`/`lst` file source into
  `raw_morgue_files`
- Output: persisted raw morgue file records, regenerated artifact MongoDB documents, crawl file/user state records
- Restriction: does not import `api`, `frontend`, or `admin-frontend` types or components

## Internal Layers

- `crawl_service.morgue`: HTTP fetch for remote morgue root/user directories and file text
- ingest flow: store remote morgue source, compute content hashes, and record fetch state
- `crawl_service.domain.artifacts`: extract randart raw info from raw text and build `RandomArtifact`
- `crawl_service.domain.evaluation`: evaluate `RandomArtifact.random_attributes`
- `crawl_service.domain.documents`: build artifact documents for MongoDB storage
- `crawl_service.processor`: read `raw_morgue_files` source and regenerate artifact read models
- `crawl_service.repository`: save raw files, write artifacts, replace by source, and save crawl file/user cache records
- `crawl_service.worker`: orchestrate remote morgue ingest and pending raw processing
- `crawl_service.observability`: worker pass summaries and processing summary logging

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

- `CRAWL_USER_SKIP_MODE`: `conservative` or `modified_at`. Default: `conservative`.
- `CRAWL_PROCESS_LIMIT`: pending raw file limit per worker pass. Default: `100`.
- `CRAWL_LOG_LEVEL`: worker logging level. Default: `INFO`.

## Related Docs

- [Crawl Service Data Types](./data-types.md)
- [Artifact Scoring Formula](./artifact_scoring_formula.md)
- [Randart Properties](./randart_properties.md)
- [DCSS Item Data](./dcss_item_data.md)
