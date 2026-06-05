# Crawl Service

`crawl_service` owns remote morgue fetch, raw file storage, processing of stored raw text, artifact document
generation, MongoDB writes, crawl file/user cache, and the background worker.

It is a long-running worker project that does not expose an HTTP API and should not be imported directly by `api`
or the frontend.

## Responsibilities

- `morgue`: query morgue directories, extract `txt`/`lst` file lists, convert raw text
- `processor.py`: regenerate artifact read models from stored raw morgue sources
- `domain/artifacts`: extract randart blocks, parse structured artifact information, build `RandomArtifact`
- `domain/evaluation`: evaluate artifacts based on `RandomArtifact.random_attributes`
- `domain/documents`: Pydantic-backed storage document models
- `repository.py`: raw file, artifact read model, and crawl cache repositories
- `worker.py`: archive user list scan, raw ingest, pending raw processing orchestration
- `observability.py`: worker pass logging and runtime summary formatting

## Data Flow

The core flow is: store the raw source first, then process the stored source later.

1. The worker fetches remote morgue files.
2. It stores the raw text, content hash, and fetch status in `raw_morgue_files`.
3. `crawl_service.processor` parses, classifies, evaluates, and builds documents from the stored raw source.
4. The result is regenerated into the `artifacts` read model.
5. Successfully stored files are cached in `crawl_files`, and user scan state is stored in `crawl_users`.

Network failures are recorded in fetch status and `fetch_error`. Processing failures are recorded separately in
process status and `process_error`.

## Runtime

Dependencies:

```sh
python3 -m pip install -r requirements.txt
```

Local MongoDB:

```sh
eval "$(infra/mongo/mongo_up.sh)"
```

Worker:

```sh
python3 -m crawl_service.worker
```

The worker scans the archive's full user directory list every three hours and reopens target directories by default
to check for missing files. Files already stored in `raw_morgue_files` are not downloaded again.
Set `CRAWL_USER_SKIP_MODE=modified_at` to query only players whose user directory `Date` changed.
It processes only user/file data from `2026-01-01` onward, keeps a default 1-second delay between HTTP requests, and
uses `CRAWL_PROCESS_LIMIT` to control throughput.

## Tests

```sh
python3 -m unittest discover -s crawl_service/tests -t .
```

When scoring changes, compare evaluator tests against [Artifact Scoring Formula](docs/en/artifact_scoring_formula.md).
When DCSS item data changes, follow the regeneration procedure in [DCSS Item Data](docs/en/dcss_item_data.md).

## Related Shared Docs

- [Processing Layers](docs/en/processing-layers.md)
- [Data Types](docs/en/data-types.md)
- [Artifact Scoring Formula](docs/en/artifact_scoring_formula.md)
- [Randart Properties](docs/en/randart_properties.md)
- [DCSS Item Data](docs/en/dcss_item_data.md)
