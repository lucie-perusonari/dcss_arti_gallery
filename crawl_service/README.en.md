# Crawl Service

`crawl_service` owns remote morgue user/file discovery, txt/lst source fetch, raw file MongoDB writes,
crawl file/user cache records, and the one-shot worker.

It is a one-shot worker project that does not expose an HTTP API and should not be imported directly by `api`,
`frontend`, `admin-frontend`, or `arti_parser`.

## Modules

- [`fetcher.py`](docs/ko/fetcher.md): query remote morgue root/user directories, extract txt/lst file entries, and fetch file text
- [`repository.py`](docs/ko/repository.md): store morgue ingest state in `raw_morgue_files` and `crawl_errors`
- [`worker.py`](docs/ko/worker.md): orchestrate archive user list scans and raw morgue file ingest
- [`tests/`](docs/ko/tests.md): fetcher, repository, and worker behavior checks

## Data Flow

The core flow is that the worker fetches remote morgue source and stores it in MongoDB.

1. The worker reads the remote morgue root user list.
2. It reads txt/lst file entries from eligible user directories.
3. It skips raw files already stored as fetched.
4. It stores new raw source in `raw_morgue_files`.
5. It appends fetch failure events to `crawl_errors`.

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
```

The worker scans the archive's full user directory list once, opens target user directories to check for missing raw
files, and exits. It processes only file data from `2026-01-01` onward and keeps a default 1-second delay between HTTP
requests.

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
| `MORGUE_BASE_URL` | `https://archive.nemelex.cards/morgue` | Remote morgue root URL. |

## Tests

```sh
python3 -m unittest discover -s crawl_service/tests -t .
```

## Related Shared Docs

- [Processing Layers](docs/en/processing-layers.md)
- [Data Types](docs/en/data-types.md)
