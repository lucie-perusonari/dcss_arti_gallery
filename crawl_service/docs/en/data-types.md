# Crawl Service Data Types

This document defines the data types that `crawl_service` creates or stores during remote morgue ingest.
Artifact parsing, scoring, document shapes, and artifact read-model storage are owned by `arti_parser`.

## `MorgueFile`

A txt/lst file discovered in a remote morgue user directory fetched over HTTP.

- Defined in: `crawl_service.fetcher`
- Fields:
  - `name: str`: remote file name
  - `url: str`: remote file URL
  - `extension: str`: file extension derived from `name`

## `MorgueUser`

A player directory discovered in a remote morgue root directory fetched over HTTP.

- Defined in: `crawl_service.fetcher`
- Fields:
  - `nickname: str`: player directory name
  - `url: str`: player morgue directory URL
  - `modified_at: str`: raw `Date` column from the root index

## `RawMorgueFileRecord`

The raw morgue source or fetch-failure record stored by `crawl_service` in MongoDB `raw_morgue_files`.
This record supports duplicate-download checks and can be used as input for downstream artifact processing.

- Defined in: `crawl_service.repository`
- Fields:
  - `player: str`
  - `name: str`
  - `url: str`
  - `extension: str`: currently `txt` or `lst`
  - `text: str`: file body; empty on fetch failure
  - `content_hash: str`: SHA-256 hash of the file body; empty on fetch failure
  - `fetch_status: str`: currently `fetched` or `failed`
  - `fetched_at: str | None`: successful fetch timestamp
  - `fetch_error: str | None`: network/source fetch failure reason

## `CrawlFileRecord`

The cache record that stores ingest completion or failure state for each remote morgue file.
The raw body belongs to `RawMorgueFileRecord`; this record is for operational status.

- Defined in: `crawl_service.repository`
- Fields:
  - `player: str`
  - `name: str`
  - `url: str`
  - `status: str`
  - `fetched_at: str | None`
  - `error: str | None`

## `CrawlUserRecord`

The cache record that stores the root-index `Date` and scan result for each user directory.
It is used for duplicate user scan prevention when `CRAWL_USER_SKIP_MODE=modified_at`.

- Defined in: `crawl_service.repository`
- Fields:
  - `player: str`
  - `url: str`
  - `observed_at: str`
  - `status: str`
  - `scanned_at: str | None`
  - `stored_files: int`: number of newly stored raw files in that scan
  - `error: str | None`
