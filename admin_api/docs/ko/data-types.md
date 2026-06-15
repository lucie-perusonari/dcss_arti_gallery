# Admin API 데이터 타입

이 문서는 `admin_api`가 소유하는 공개 응답 DTO를 정의합니다.

`admin_api`는 `crawl_service`를 import하지 않습니다.

## `CrawlStatus`

- 정의 위치: `admin_api.models.CrawlStatus`
- 용도: admin dashboard 상태 응답
- 필드:
  - `artifactCount: int`
  - `crawlActive: bool`
  - `rawFiles: RawFileStatus`
  - `crawlFiles: dict[str, int]`
  - `crawlUsers: dict[str, int]`
  - `latest: LatestActivity`
  - `recentErrors: list[CrawlError]`

`crawlActive`는 admin API 프로세스가 관측한 `raw_morgue_files` 총 개수를 3분 이상 지난 샘플과 비교해
증가했으면 `true`로 계산합니다. 별도 crawl service 내부 상태나 Docker 상태를 읽지 않습니다.

## `RawFileStatus`

- 정의 위치: `admin_api.models.RawFileStatus`
- 필드:
  - `total: int`
  - `fetched: int`
  - `fetchFailed: int`
  - `processPending: int`
  - `processProcessed: int`
  - `processFailed: int`

## `LatestActivity`

- 정의 위치: `admin_api.models.LatestActivity`
- 필드:
  - `fetchedAt: str | None`
  - `processedAt: str | None`
  - `scannedAt: str | None`

## `CrawlError`

- 정의 위치: `admin_api.models.CrawlError`
- 필드:
  - `kind: str`
  - `player: str`
  - `name: str | None`
  - `message: str`
  - `at: str | None`

## `GalleryApiMetrics`

- 정의 위치: `admin_api.models.GalleryApiMetrics`
- 용도: admin dashboard의 Gallery API metrics 응답
- 필드:
  - `status: str`
  - `windowSeconds: int`
  - `requestRatePerSecond: float | None`
  - `errorRatePerSecond: float | None`
  - `p95LatencySeconds: float | None`
  - `inFlightRequests: float | None`
  - `error: str | None`

`status`는 Prometheus query가 성공하면 `ok`, 실패하면 `unavailable`입니다. `admin_api`는 Prometheus를 scrape하거나
저장하지 않고, 내부 Prometheus HTTP API를 read-only로 query합니다.

## 연계 문서

- [Admin API Processing Layers](./processing-layers.md)
- [Admin Frontend Data Types](../../../admin-frontend/docs/ko/data-types.md)
