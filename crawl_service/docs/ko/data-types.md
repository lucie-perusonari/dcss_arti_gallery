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

`crawl_service`가 MongoDB `raw_morgue_files` 컬렉션에 저장하는 원본 morgue 파일입니다.
이 record는 중복 다운로드 방지와 후속 artifact 처리 입력으로 사용할 수 있는 raw source입니다.

- 정의 위치: `crawl_service.repository`
- 필드:
  - `player: str`: player directory 이름
  - `name: str`: 원격 파일명
  - `url: str`: 원격 파일 URL
  - `extension: str`: 원문 종류. 현재 `txt` 또는 `lst`
  - `text: str`: 파일 본문
  - `content_hash: str`: 원문 본문의 SHA-256 hash
  - `fetch_status: str`: 원본 확보 상태. 현재 `fetched`
  - `fetched_at: str | None`: fetch 성공 시각

## `CrawlErrorRecord`

`crawl_service` worker가 fetch 실패 이벤트를 `crawl_errors`에 append-only로 저장하는 record입니다.
성공/재시도 판단에는 사용하지 않고 운영 관측용으로만 사용합니다.

- 정의 위치: `crawl_service.repository`
- 필드:
  - `player: str`
  - `stage: str`: 실패 단계. 예: `fetch_user_directory`, `fetch_file`
  - `message: str`
  - `occurred_at: str`
  - `name: str | None`
  - `url: str | None`
  - `extension: str | None`
  - `error_type: str | None`
  - `user_url: str | None`
