# Admin Frontend Data Types

This document defines the status types consumed by the crawl operations dashboard.

## `RawFileStatus`

- Defined in: `admin-frontend/src/types/status.ts`
- Fields:
  - `total: number`
  - `fetched: number`
  - `fetchFailed: number`
  - `processPending: number`
  - `processProcessed: number`
  - `processFailed: number`

## `LatestActivity`

- Defined in: `admin-frontend/src/types/status.ts`
- Fields:
  - `fetchedAt?: string | null`
  - `processedAt?: string | null`
  - `scannedAt?: string | null`

## `CrawlError`

- Defined in: `admin-frontend/src/types/status.ts`
- Fields:
  - `kind: string`
  - `player: string`
  - `name?: string | null`
  - `message: string`
  - `at?: string | null`

## `CrawlStatus`

- Defined in: `admin-frontend/src/types/status.ts`
- Fields:
  - `artifactCount: number`
  - `crawlActive: boolean`
  - `rawFiles: RawFileStatus`
  - `crawlFiles: Record<string, number>`
  - `crawlUsers: Record<string, number>`
  - `latest: LatestActivity`
  - `recentErrors: CrawlError[]`

## `GalleryApiMetrics`

- Defined in: `admin-frontend/src/types/status.ts`
- Fields:
  - `status: 'ok' | 'unavailable' | string`
  - `windowSeconds: number`
  - `requestRatePerSecond?: number | null`
  - `errorRatePerSecond?: number | null`
  - `p95LatencySeconds?: number | null`
  - `inFlightRequests?: number | null`
  - `error?: string | null`

## Related Docs

- [Admin Frontend Processing Layers](./processing-layers.md)
- [Admin API Data Types](../../../admin_api/docs/en/data-types.md)
