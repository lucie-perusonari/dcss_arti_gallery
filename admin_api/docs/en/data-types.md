# Admin API Data Types

This document defines the public response DTOs owned by `admin_api`.

`admin_api` does not import `crawl_service`.

## `CrawlStatus`

- Defined in: `admin_api.models.CrawlStatus`
- Purpose: admin dashboard status response
- Fields:
  - `artifactCount: int`
  - `crawlActive: bool`
  - `rawFiles: RawFileStatus`
  - `latest: LatestActivity`
  - `recentErrors: list[CrawlError]`

`crawlActive` is computed by comparing the current `raw_morgue_files` total with a sample observed at least three
minutes earlier by the admin API process. It does not read crawl service internals or Docker state.

## `RawFileStatus`

- Defined in: `admin_api.models.RawFileStatus`
- Fields:
  - `total: int`
  - `fetched: int`
  - `fetchFailed: int`
  - `processPending: int`
  - `processProcessed: int`
  - `processFailed: int`

## `LatestActivity`

- Defined in: `admin_api.models.LatestActivity`
- Fields:
  - `fetchedAt: str | None`
  - `processedAt: str | None`

## `CrawlError`

- Defined in: `admin_api.models.CrawlError`
- Fields:
  - `kind: str`
  - `player: str`
  - `name: str | None`
  - `message: str`
  - `at: str | None`

## `GalleryApiMetrics`

- Defined in: `admin_api.models.GalleryApiMetrics`
- Purpose: Gallery API metrics response for the admin dashboard
- Fields:
  - `status: str`
  - `windowSeconds: int`
  - `requestRatePerSecond: float | None`
  - `errorRatePerSecond: float | None`
  - `p95LatencySeconds: float | None`
  - `inFlightRequests: float | None`
  - `error: str | None`

`status` is `ok` when Prometheus queries succeed and `unavailable` when they fail. `admin_api` queries the internal
Prometheus HTTP API read-only; it does not scrape or store metrics itself.

## Related Docs

- [Admin API Processing Layers](./processing-layers.md)
- [Admin Frontend Data Types](../../../admin-frontend/docs/en/data-types.md)
