# Crawl Service Processing Layers

이 문서는 `crawl_service` 안에서 remote morgue 원본을 저장하고, 저장된 원본에서 artifact read model을 재생성하는 계층을 정의합니다.

핵심 원칙은 **remote morgue 원본을 먼저 영속화하고, 이후 처리 단계는 저장된 원본만 입력으로 삼는다**는 것입니다.
`raw_morgue_files`는 원본 추적과 재처리의 기준이고, `artifacts`는 API/frontend를 위한 재생성 가능한 read model입니다.

```text
remote morgue
  -> crawl_service.cli.worker
  -> raw_morgue_files
       fetch_status / fetch_error
       process_status / process_error
       content_hash
       parser_version / scoring_version
  -> crawl_service.core.processor
  -> artifacts
```

## Project Boundary

- 모듈: `crawl_service/`
- 역할: remote morgue root user list를 주기적으로 조회하고, 대상 user의 txt/lst 파일 원본을 `raw_morgue_files`에 저장한다.
- 출력: persisted raw morgue file records, crawl file/user state records
- 제한: `api`, `frontend`, `admin-frontend`의 타입이나 컴포넌트를 import하지 않는다.

## Internal Layers

- `crawl_service.morgue`: 원격 morgue root/user 디렉터리와 파일 HTTP fetch
- ingest flow: remote morgue 파일 원문 저장, content hash 생성, fetch 상태 기록
- `crawl_service.artifacts`: txt/lst 원문에서 artifact raw evidence를 추출하고 이름/속성/분류/평가/`ArtifactDocument` 생성을 담당
- `crawl_service.core.processor`: `raw_morgue_files` 원본을 읽어 artifact read model 재생성
- `crawl_service.core.repository`: raw file 저장, artifact write, source별 replace, crawl file/user cache record 저장
- `crawl_service.cli.worker`: remote morgue 원문 ingest orchestration
- `crawl_service.core.observability`: worker pass summary logging

## Ingest And Processing State

- fetch 성공: `raw_morgue_files.fetch_status = fetched`, `process_status = pending`
- fetch 실패: `raw_morgue_files.fetch_status = failed`, `fetch_error` 저장, processing 상태는 오염시키지 않음
- processing 성공: `artifacts`를 source별로 replace하고 `process_status = processed`, 현재 parser/scoring version 저장
- processing 실패: `process_status = failed`, `process_error` 저장, fetch 상태는 유지
- 재처리 대상: fetched raw file 중 `process_status`가 `pending`/`failed`이거나 parser/scoring version이 현재 값과 다른 record

## Runtime Configuration

- `MORGUE_BASE_URL`: remote morgue root URL. 기본값은 `https://archive.nemelex.cards/morgue`.
- `CRAWL_START_DATE`: 처리 대상 user/file 시작일. 기본값은 `2026-01-01`.
- `MORGUE_REQUEST_DELAY_SECONDS`: HTTP 요청 사이 최소 delay. 기본값은 `1.0`.
- `CRAWL_LOOP_INTERVAL_SECONDS`: worker pass 사이 대기 시간. 기본값은 `604800`초(7일).
- `MORGUE_REQUEST_TIMEOUT_SECONDS`: HTTP 요청 timeout. 기본값은 morgue fetcher 기본값.
- `MORGUE_USER_AGENT`: remote morgue 요청 user agent.
- `CRAWL_USER_SKIP_MODE`: `conservative` 또는 `modified_at`. 기본값은 `conservative`.
- `CRAWL_LOG_LEVEL`: worker logging level. 기본값은 `INFO`.

## 운영 스크립트

- `python3 -m crawl_service.cli.worker`: remote morgue 원문을 fetch해 `raw_morgue_files`에 저장한다.
- `crawl_service/run_raw_crawler.sh`: raw ingest worker wrapper. `DETACH=1`이면 백그라운드로 실행하고 `.logs/crawl_raw_only.log`에 기록한다.
- `crawl_service/process_raw_morgue_files.sh`: 저장된 fetched raw file을 별도 batch로 처리한다. `PROCESS_LIMIT` 기본값은 `1000`, `ONCE=1`이면 한 batch만 처리한다.

## Related Docs

- [Crawl Service Data Types](./data-types.md)
- [Artifact Scoring Formula](./artifact_scoring_formula.md)
- [Randart Properties](./randart_properties.md)
- [DCSS Item Data](./dcss_item_data.md)
