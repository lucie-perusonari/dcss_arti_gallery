# Crawl Service

`crawl_service` owns remote morgue fetch, raw file storage, processing of stored raw text, artifact document
generation, MongoDB writes, crawl file/user cache, and the background worker.

It is a long-running worker project that does not expose an HTTP API and should not be imported directly by `api`
or the frontend.

## Responsibilities

- `morgue`: query morgue directories, extract `txt`/`lst` file lists, and convert raw text
- `core/processor.py`: regenerate artifact read models from stored raw morgue sources
- `artifacts`: extract artifact raw evidence, parse names/attributes/classification, evaluate, and define Pydantic storage document models
- `core/repository.py`: raw file, artifact read model, and crawl cache repositories
- `cli/worker.py`: archive user list scan and raw morgue file ingest
- `core/observability.py`: worker pass logging and runtime summary formatting

## Data Flow

The core flow is: store the raw source first, then process the stored source later.

1. The worker fetches remote morgue files.
2. It stores the raw text, content hash, and fetch status in `raw_morgue_files`.
3. `crawl_service.core.processor` parses, classifies, evaluates, and builds documents from the stored raw source.
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
python3 -m crawl_service.cli.worker
```

The worker scans the archive's full user directory list once a week and opens target directories to check for missing
files. Files already stored in `raw_morgue_files` are not downloaded again.
Set `CRAWL_USER_SKIP_MODE=modified_at` to query only players whose user directory `Date` changed.
It processes only user/file data from `2026-01-01` onward, keeps a default 1-second delay between HTTP requests, and
only persists source into `raw_morgue_files`.

### Raw Ingest And Separate Processing

Artifact regeneration is run separately through the processor script, not by the worker.

```sh
crawl_service/run_raw_crawler.sh
crawl_service/process_raw_morgue_files.sh
```

- `crawl_service/run_raw_crawler.sh`: runs the worker and stores only fetched raw files.
- `DETACH=1 crawl_service/run_raw_crawler.sh`: runs the raw crawler in the background and writes `.logs/crawl_raw_only.log`.
- `crawl_service/process_raw_morgue_files.sh`: processes fetched/pending or version-mismatched records in
  `raw_morgue_files`.
- `PROCESS_LIMIT=1000`: processor batch size. Default: `1000`.
- `ONCE=1`: process one batch and exit.

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
