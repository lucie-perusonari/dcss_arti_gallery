# Crawl Service

`crawl_service` owns remote morgue user/file discovery, txt/lst source fetch, raw file MongoDB writes,
crawl file/user cache records, and the background worker.

It is a long-running worker project that does not expose an HTTP API and should not be imported directly by `api`,
`frontend`, `admin-frontend`, or `arti_parser`.

## Modules

- [`fetcher.py`](docs/ko/fetcher.md): query remote morgue root/user directories, extract txt/lst file entries, and fetch file text
- [`repository.py`](docs/ko/repository.md): store morgue ingest state in `raw_morgue_files`, `crawl_files`, and `crawl_users`
- [`worker.py`](docs/ko/worker.md): orchestrate archive user list scans and raw morgue file ingest
- [`tests/`](docs/ko/tests.md): fetcher, repository, and worker behavior checks

## Data Flow

The core flow is that the worker fetches remote morgue source and stores it in MongoDB.

1. The worker reads the remote morgue root user list.
2. It reads txt/lst file entries from eligible user directories.
3. It skips duplicate file names in the same pass and raw files already stored as fetched.
4. It stores new raw source or fetch failure state in `raw_morgue_files`.
5. It stores per-file state in `crawl_files` and user scan state in `crawl_users`.

Artifact parsing, scoring, and artifact document construction are not `crawl_service` responsibilities.

## Runtime

Dependencies use the repository-root `requirements.txt`.

```sh
python3 -m pip install -r requirements.txt
```

Local MongoDB:

```sh
docker compose -f infra/dev/docker-compose.yml up -d mongo mongo-indexes
```

Worker:

```sh
python3 -m crawl_service.worker
python3 -m crawl_service.worker --once
```

The default worker scans the archive's full user directory list once a week and opens target user directories to check
for missing raw files. With `--once`, it runs one crawl pass and exits. With `CRAWL_USER_SKIP_MODE=modified_at`, it
skips players whose user directory `Date` matches the previous scan. It processes only user/file data from
`2026-01-01` onward and keeps a default 1-second delay between HTTP requests.

In Docker Compose, the crawler performs live morgue crawl work, so it is not part of the default stack. It runs only as
a `jobs` profile one-shot service.

```sh
docker compose -f infra/dev/docker-compose.yml run --rm crawl-service
docker compose -f infra/prod/docker-compose.yml run --rm crawl-service
```

Use the compose `arti-parser` job to regenerate the artifact read model from stored raw source.

Key environment variables:

| Environment variable | Default | Description |
| --- | --- | --- |
| `MONGODB_URI` | `mongodb://localhost:27018` | MongoDB connection string. Compose injects `mongodb://mongo:27017` internally. |
| `MONGODB_DATABASE` | `dcss_arti_gallery` | Database name. |
| `MONGODB_RAW_FILES_COLLECTION` | `raw_morgue_files` | Collection storing raw morgue source. |
| `MONGODB_CRAWL_FILES_COLLECTION` | `crawl_files` | File-level crawl status collection. |
| `MONGODB_CRAWL_USERS_COLLECTION` | `crawl_users` | User-directory scan status collection. |
| `MORGUE_BASE_URL` | `https://archive.nemelex.cards/morgue` | Remote morgue root URL. |
| `MORGUE_REQUEST_DELAY_SECONDS` | `1.0` | Minimum delay between HTTP requests. |
| `MORGUE_REQUEST_TIMEOUT_SECONDS` | `20.0` | HTTP request timeout. |
| `MORGUE_USER_AGENT` | `dcss-arti-gallery-crawler/0.1` | User agent for remote morgue requests. |
| `CRAWL_START_DATE` | `2026-01-01` | Start date for eligible user/file data. |
| `CRAWL_LOOP_INTERVAL_SECONDS` | `604800` | Delay between worker passes. |
| `CRAWL_USER_SKIP_MODE` | `conservative` | Either `conservative` or `modified_at`. |
| `CRAWL_LOG_LEVEL` | `INFO` | Worker logging level. |
| `CRAWL_ONCE` | `false` | If `1`, `true`, `yes`, or `on`, run one crawl pass and exit. |

## Tests

```sh
python3 -m unittest discover -s crawl_service/tests -t .
```

## Related Shared Docs

- [Processing Layers](docs/en/processing-layers.md)
- [Data Types](docs/en/data-types.md)
