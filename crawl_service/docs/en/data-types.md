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

The raw morgue source stored by `crawl_service` in MongoDB `raw_morgue_files`.
This record supports duplicate-download checks and can be used as input for downstream artifact processing.

- Defined in: `crawl_service.repository`
- Fields:
  - `player: str`
  - `name: str`
  - `url: str`
  - `extension: str`: currently `txt` or `lst`
  - `text: str`: file body
  - `content_hash: str`: SHA-256 hash of the file body
  - `fetch_status: str`: currently `fetched`
  - `fetched_at: str | None`: successful fetch timestamp

## `CrawlErrorRecord`

The append-only record that stores fetch failure events in `crawl_errors`.
It is used only for operations visibility, not for success or retry decisions.

- Defined in: `crawl_service.repository`
- Fields:
  - `player: str`
  - `stage: str`: failure stage, such as `fetch_user_directory` or `fetch_file`
  - `message: str`
  - `occurred_at: str`
  - `name: str | None`
  - `url: str | None`
  - `extension: str | None`
  - `error_type: str | None`
  - `user_url: str | None`
