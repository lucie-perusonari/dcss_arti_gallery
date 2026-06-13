# Crawl Service Processing Layers

이 문서는 `crawl_service` 안에서 remote morgue 원본을 fetch하고 MongoDB에 저장하는 계층을 정의합니다.

```text
remote morgue
  -> crawl_service.fetcher
  -> crawl_service.worker
  -> crawl_service.repository
  -> MongoDB raw_morgue_files / crawl_files / crawl_users
```

## Project Boundary

- 모듈: `crawl_service/`
- 역할: remote morgue root/user directory를 조회하고 대상 txt/lst 원문과 fetch 상태를 저장한다.
- 출력: persisted raw morgue file records, crawl file/user state records
- 제한: `api`, `frontend`, `admin-frontend`, `arti_parser`를 import하지 않는다. artifact read model 재생성은 `arti_parser`가 소유한다.

## Internal Layers

- `crawl_service.fetcher`: remote morgue root/user directory와 txt/lst 파일 HTTP fetch
- `crawl_service.worker`: 날짜 필터, 중복 파일 skip, throttle, raw ingest orchestration
- `crawl_service.repository`: raw file 저장, crawl file/user cache 저장, 중복 검사에 필요한 최소 조회

## Duplicate Checks

- 같은 user directory pass 안에서 동일 파일명은 한 번만 처리한다.
- `raw_morgue_files`에 같은 player/name이 `fetch_status = fetched`로 있으면 다시 다운로드하지 않는다.
- `CRAWL_USER_SKIP_MODE=modified_at`이면 `crawl_users.observed_at`이 remote Date와 같은 completed user를 skip한다.

## Runtime Configuration

- `MORGUE_BASE_URL`: remote morgue root URL. 기본값은 `https://archive.nemelex.cards/morgue`.
- `CRAWL_START_DATE`: 대상 user/file 시작일. 기본값은 `2026-01-01`.
- `MORGUE_REQUEST_DELAY_SECONDS`: HTTP 요청 사이 최소 delay. 기본값은 `1.0`.
- `CRAWL_LOOP_INTERVAL_SECONDS`: worker pass 사이 대기 시간. 기본값은 `604800`초(7일).
- `MORGUE_REQUEST_TIMEOUT_SECONDS`: HTTP 요청 timeout. 기본값은 fetcher 기본값.
- `MORGUE_USER_AGENT`: remote morgue 요청 user agent.
- `CRAWL_USER_SKIP_MODE`: `conservative` 또는 `modified_at`. 기본값은 `conservative`.
- `CRAWL_LOG_LEVEL`: worker logging level. 기본값은 `INFO`.
- `CRAWL_ONCE`: `1`, `true`, `yes`, `on`이면 한 번의 crawl pass만 실행하고 종료한다.

## 운영 스크립트

- `python3 -m crawl_service.worker`: remote morgue 원문을 fetch해 raw/cache 컬렉션에 저장한다.
- `python3 -m crawl_service.worker --once`: 한 번의 crawl pass만 실행하고 종료한다.
- `crawl_service/run_raw_crawler.sh`: raw ingest worker wrapper. `DETACH=1`이면 백그라운드로 실행한다.

## Related Docs

- [Crawl Service Data Types](./data-types.md)
