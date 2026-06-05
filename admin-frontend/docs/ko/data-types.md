# Admin Frontend 데이터 타입

이 문서는 crawl operations dashboard가 소비하는 status 타입을 정의합니다.

## `RawFileStatus`

- 정의 위치: `admin-frontend/src/types/status.ts`
- 필드:
  - `total: number`
  - `fetched: number`
  - `fetchFailed: number`
  - `processPending: number`
  - `processProcessed: number`
  - `processFailed: number`

## `LatestActivity`

- 정의 위치: `admin-frontend/src/types/status.ts`
- 필드:
  - `fetchedAt?: string | null`
  - `processedAt?: string | null`
  - `scannedAt?: string | null`

## `CrawlError`

- 정의 위치: `admin-frontend/src/types/status.ts`
- 필드:
  - `kind: string`
  - `player: string`
  - `name?: string | null`
  - `message: string`
  - `at?: string | null`

## `CrawlStatus`

- 정의 위치: `admin-frontend/src/types/status.ts`
- 필드:
  - `artifactCount: number`
  - `rawFiles: RawFileStatus`
  - `crawlFiles: Record<string, number>`
  - `crawlUsers: Record<string, number>`
  - `latest: LatestActivity`
  - `recentErrors: CrawlError[]`

## 연계 문서

- [Admin Frontend Processing Layers](./processing-layers.md)
- [API Data Types](../../../api/docs/ko/data-types.md)
