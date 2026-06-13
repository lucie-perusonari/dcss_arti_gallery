# Crawl Service

`crawl_service` owns remote morgue user/file discovery, txt/lst source fetch, raw file MongoDB writes,
crawl file/user cache records, and the background worker.

It is a long-running worker project that does not expose an HTTP API and should not be imported directly by `api`,
`frontend`, `admin-frontend`, or `arti_parser`.

## Responsibilities

- `fetcher.py`: query remote morgue root/user directories, extract txt/lst file entries, and fetch file text
- `repository.py`: store morgue ingest state in `raw_morgue_files`, `crawl_files`, and `crawl_users`
- `worker.py`: orchestrate archive user list scans and raw morgue file ingest

## Data Flow

The core flow is that the worker fetches remote morgue source and stores it in MongoDB.

1. The worker reads the remote morgue root user list.
2. It reads txt/lst file entries from eligible user directories.
3. It skips duplicate file names in the same pass and raw files already stored as fetched.
4. It stores new raw source or fetch failure state in `raw_morgue_files`.
Artifact parsing, scoring, artifact document generation, and `artifacts` storage belong to `arti_parser`.
5. It stores per-file state in `crawl_files` and user scan state in `crawl_users`.

Artifact parsing, scoring, and artifact document construction are not `crawl_service` responsibilities.

## Runtime

Dependencies use the repository-root `requirements.txt`.

```sh
python3 -m pip install -r requirements.txt
```

Local MongoDB:

```sh
eval "$(infra/dev/mongo_up.sh)"
```

Worker:

```sh
python3 -m crawl_service.worker
```

The worker scans the archive's full user directory list once a week and opens target user directories to check for
missing raw files. With `CRAWL_USER_SKIP_MODE=modified_at`, it skips players whose user directory `Date` matches the
previous scan. It processes only user/file data from `2026-01-01` onward and keeps a default 1-second delay between
HTTP requests.

Wrapper script:

```sh
crawl_service/run_raw_crawler.sh
```

- `crawl_service/run_raw_crawler.sh`: runs the worker and stores fetched raw files only.
- `DETACH=1 crawl_service/run_raw_crawler.sh`: runs the raw crawler in the background and writes `.logs/crawl_raw_only.log`.

## Tests

```sh
python3 -m unittest discover -s crawl_service/tests -t .
```

## Related Shared Docs

- [Processing Layers](docs/en/processing-layers.md)
- [Data Types](docs/en/data-types.md)
