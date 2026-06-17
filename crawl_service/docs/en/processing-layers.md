# Crawl Service Processing Layers

This document defines the layers inside `crawl_service` that fetch remote morgue source and store it in MongoDB.

```text
remote morgue
  -> crawl_service.fetcher
  -> crawl_service.worker
  -> crawl_service.repository
  -> MongoDB raw_morgue_files / crawl_errors
```

## Project Boundary

- Module: `crawl_service/`
- Role: query remote morgue root/user directories and persist target txt/lst source plus fetch state.
- Output: persisted raw morgue file records and crawl error event records
- Restriction: does not import `api`, `frontend`, `admin-frontend`, or `arti_parser`. Artifact read-model regeneration belongs to `arti_parser`.

## Internal Layers

- `crawl_service.fetcher`: HTTP fetch for remote morgue root/user directories and txt/lst file text
- `crawl_service.worker`: date filtering, existing raw-file skipping, throttling, and raw ingest orchestration
- `crawl_service.repository`: raw file writes, crawl error log writes, and the minimal reads needed for duplicate checks

## Skip Checks

- A player/name already stored in `raw_morgue_files` with `fetch_status = fetched` is not downloaded again.

## Runtime Configuration

- `MORGUE_BASE_URL`: remote morgue root URL. Default: `https://archive.nemelex.cards/morgue`.

## Operation Scripts

- `python3 -m crawl_service.worker`: fetches remote morgue source and stores it in raw/cache collections.
- `docker compose -f infra/dev/docker-compose.yml run --rm crawl-service`: runs the one-shot crawl job against the dev compose MongoDB.

## Related Docs

- [Crawl Service Data Types](./data-types.md)
