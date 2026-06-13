# Crawl Service Processing Layers

This document defines the layers inside `crawl_service` that fetch remote morgue source and store it in MongoDB.

```text
remote morgue
  -> crawl_service.fetcher
  -> crawl_service.worker
  -> crawl_service.repository
  -> MongoDB raw_morgue_files / crawl_files / crawl_users
```

## Project Boundary

- Module: `crawl_service/`
- Role: query remote morgue root/user directories and persist target txt/lst source plus fetch state.
- Output: persisted raw morgue file records and crawl file/user state records
- Restriction: does not import `api`, `frontend`, `admin-frontend`, or `arti_parser`. Artifact read-model regeneration belongs to `arti_parser`.

## Internal Layers

- `crawl_service.fetcher`: HTTP fetch for remote morgue root/user directories and txt/lst file text
- `crawl_service.worker`: date filtering, duplicate-file skipping, throttling, and raw ingest orchestration
- `crawl_service.repository`: raw file writes, crawl file/user cache writes, and the minimal reads needed for duplicate checks

## Duplicate Checks

- Duplicate file names in the same user-directory pass are processed once.
- A player/name already stored in `raw_morgue_files` with `fetch_status = fetched` is not downloaded again.
- With `CRAWL_USER_SKIP_MODE=modified_at`, a completed user whose `crawl_users.observed_at` matches the remote Date is skipped.

## Runtime Configuration

- `MORGUE_BASE_URL`: remote morgue root URL. Default: `https://archive.nemelex.cards/morgue`.
- `CRAWL_START_DATE`: start date for eligible user/file data. Default: `2026-01-01`.
- `MORGUE_REQUEST_DELAY_SECONDS`: minimum delay between HTTP requests. Default: `1.0`.
- `CRAWL_LOOP_INTERVAL_SECONDS`: delay between worker passes. Default: `604800` seconds (7 days).
- `MORGUE_REQUEST_TIMEOUT_SECONDS`: HTTP request timeout. Default: the fetcher default.
- `MORGUE_USER_AGENT`: user agent for remote morgue requests.
- `CRAWL_USER_SKIP_MODE`: `conservative` or `modified_at`. Default: `conservative`.
- `CRAWL_LOG_LEVEL`: worker logging level. Default: `INFO`.

## Operation Scripts

- `python3 -m crawl_service.worker`: fetches remote morgue source and stores it in raw/cache collections.
- `crawl_service/run_raw_crawler.sh`: raw ingest worker wrapper. With `DETACH=1`, it runs in the background.

## Related Docs

- [Crawl Service Data Types](./data-types.md)
