# Crawl Service Processing Layers

이 문서는 `crawl_service` 안에서 remote morgue 원본을 fetch하고 MongoDB에 저장하는 계층을 정의합니다.

```text
remote morgue
  -> crawl_service.fetcher
  -> crawl_service.worker
  -> crawl_service.repository
  -> MongoDB raw_morgue_files / crawl_errors
```

## Project Boundary

- 모듈: `crawl_service/`
- 역할: remote morgue root/user directory를 조회하고 대상 txt/lst 원문과 fetch 상태를 저장한다.
- 출력: persisted raw morgue file records, crawl error event records
- 제한: `api`, `frontend`, `admin-frontend`, `arti_parser`를 import하지 않는다. artifact read model 재생성은 `arti_parser`가 소유한다.

## Internal Layers

- `crawl_service.fetcher`: remote morgue root/user directory와 txt/lst 파일 HTTP fetch
- `crawl_service.worker`: 날짜 필터, 기존 raw file skip, throttle, raw ingest orchestration
- `crawl_service.repository`: raw file 저장, crawl error log 저장, 중복 검사에 필요한 최소 조회

## Skip Checks

- `raw_morgue_files`에 같은 player/name이 `fetch_status = fetched`로 있으면 다시 다운로드하지 않는다.

## Runtime Configuration

- `MORGUE_BASE_URL`: remote morgue root URL. 기본값은 `https://archive.nemelex.cards/morgue`.

## 운영 스크립트

- `python3 -m crawl_service.worker`: remote morgue 원문을 fetch해 raw/cache 컬렉션에 저장한다.
- `docker compose -f infra/dev/docker-compose.yml run --rm crawl-service`: dev compose MongoDB에 대해 one-shot crawl job을 실행한다.

## Related Docs

- [Crawl Service Data Types](./data-types.md)
