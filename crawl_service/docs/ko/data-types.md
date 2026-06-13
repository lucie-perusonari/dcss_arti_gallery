# Crawl Service Data Types

이 문서는 `crawl_service`가 remote morgue ingest 과정에서 생성하거나 저장하는 데이터 타입을 정의합니다.
Artifact parsing/scoring/document 타입은 `arti_parser` 문서가 소유합니다.

## `MorgueFile`

HTTP로 조회한 원격 morgue user directory에서 발견한 txt/lst 파일 항목입니다.

- 정의 위치: `crawl_service.fetcher`
- 필드:
  - `name: str`: 원격 파일명
  - `url: str`: 원격 파일 URL
  - `extension: str`: 파일 확장자. `name`에서 계산되는 property

## `MorgueUser`

HTTP로 조회한 원격 morgue root directory에서 발견한 player directory 항목입니다.

- 정의 위치: `crawl_service.fetcher`
- 필드:
  - `nickname: str`: player directory 이름
  - `url: str`: player morgue directory URL
  - `modified_at: str`: root index의 Date 컬럼 원문

## `RawMorgueFileRecord`

`crawl_service`가 MongoDB `raw_morgue_files` 컬렉션에 저장하는 원본 morgue 파일 또는 fetch 실패 기록입니다.
이 record는 중복 다운로드 방지와 후속 artifact 처리 입력으로 사용할 수 있는 raw source입니다.

- 정의 위치: `crawl_service.repository`
- 필드:
  - `player: str`: player directory 이름
  - `name: str`: 원격 파일명
  - `url: str`: 원격 파일 URL
  - `extension: str`: 원문 종류. 현재 `txt` 또는 `lst`
  - `text: str`: 파일 본문. fetch 실패 시 빈 문자열
  - `content_hash: str`: 원문 본문의 SHA-256 hash. fetch 실패 시 빈 문자열
  - `fetch_status: str`: 원본 확보 상태. 현재 `fetched` 또는 `failed`
  - `fetched_at: str | None`: fetch 성공 시각
  - `fetch_error: str | None`: 네트워크/원본 확보 실패 원인

## `CrawlFileRecord`

`crawl_service`가 remote morgue 파일별 ingest 완료 또는 실패 상태를 저장하는 cache record입니다.
원본 본문은 `RawMorgueFileRecord`가 소유하고, 이 record는 운영 상태 확인용입니다.

- 정의 위치: `crawl_service.repository`
- 필드:
  - `player: str`
  - `name: str`
  - `url: str`
  - `status: str`
  - `fetched_at: str | None`
  - `error: str | None`

## `CrawlUserRecord`

`crawl_service` worker가 user directory별 root index Date와 scan 결과를 저장하는 cache record입니다.
`CRAWL_USER_SKIP_MODE=modified_at`일 때 중복 user scan 방지에 사용됩니다.

- 정의 위치: `crawl_service.repository`
- 필드:
  - `player: str`
  - `url: str`
  - `observed_at: str`: root morgue index의 user directory Date
  - `status: str`
  - `scanned_at: str | None`
  - `stored_files: int`: 해당 scan에서 새로 저장한 raw file 수
  - `error: str | None`
