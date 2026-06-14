# 크롤 서비스

`crawl_service`는 remote morgue user/file 목록 조회, txt/lst 원문 fetch, raw file MongoDB 저장,
crawl file/user cache 기록, background worker를 소유합니다.

HTTP API를 제공하지 않는 상주 worker 프로젝트이며, `api`, `frontend`, `admin-frontend`, `arti_parser`가 직접 의존해야 하는 대상이 아닙니다.

## 모듈

- [`fetcher.py`](docs/ko/fetcher.md): remote morgue root/user directory 조회, txt/lst 파일 목록 추출, 파일 본문 fetch
- [`repository.py`](docs/ko/repository.md): `raw_morgue_files`, `crawl_files`, `crawl_users`에 morgue ingest 상태 저장
- [`worker.py`](docs/ko/worker.md): archive user list scan과 raw morgue file ingest orchestration
- [`tests/`](docs/ko/tests.md): fetcher, repository, worker 동작 검증

English version: [README.en.md](README.en.md)

## 책임

- remote morgue user/file 목록을 조회하고 txt/lst 원문을 가져옵니다.
- raw morgue 원본과 crawl file/user cache 상태를 MongoDB에 저장합니다.
- background worker로 archive user list scan과 raw morgue file ingest를 조율합니다.
- artifact parsing, scoring, artifact document 생성, `artifacts` 저장은 `arti_parser` 책임입니다.

## 데이터 흐름

핵심 흐름은 worker가 원격 morgue 원본을 가져와 MongoDB에 저장하는 것입니다.

1. worker가 remote morgue root user list를 조회합니다.
2. 대상 user directory에서 txt/lst 파일 목록을 조회합니다.
3. 같은 pass 안의 중복 파일명과 이미 저장된 fetched raw file은 skip합니다.
4. 새 파일 원문 또는 fetch 실패 상태를 `raw_morgue_files`에 저장합니다.
5. 파일별 상태는 `crawl_files`, user scan 상태는 `crawl_users`에 기록합니다.
artifact parsing, scoring, artifact document 생성, `artifacts` 저장은 `arti_parser` 책임입니다.

## 실행

dependencies는 repository root의 `requirements.txt`를 사용합니다.

```sh
python3 -m venv .venv
.venv/bin/python -m pip install --upgrade pip
.venv/bin/python -m pip install -r requirements.txt
```

local MongoDB:

```sh
docker compose -f infra/dev/docker-compose.yml up -d mongo mongo-indexes
```

worker:

```sh
python3 -m crawl_service.worker
python3 -m crawl_service.worker --once
```

기본 worker는 archive의 전체 user directory list를 주 1회 훑고, 대상 user directory를 열어 누락 raw file을 확인합니다.
`--once`를 지정하면 한 번의 crawl pass만 실행하고 종료합니다.
`CRAWL_USER_SKIP_MODE=modified_at`이면 user directory Date가 이전 scan과 같은 player를 skip합니다.
2026-01-01 이후 user/file 데이터만 처리하며 모든 HTTP 요청 사이에 기본 1초 delay를 둡니다.

Docker Compose에서 crawler는 live morgue crawl을 수행하므로 기본 stack에는 포함되지 않고 `jobs` profile의
one-shot job으로만 실행합니다.
네트워크 동작 확인이 필요하거나 사용자가 명시적으로 요청한 경우가 아니라면, 검증 목적으로 live morgue
crawl을 실행하지 않습니다.

```sh
docker compose -f infra/dev/docker-compose.yml run --rm crawl-service
docker compose -f infra/prod/docker-compose.yml run --rm crawl-service
```

저장된 raw source를 artifact read model로 재생성하려면 compose의 `arti-parser` job을 실행합니다.

주요 환경 변수:

| 환경 변수 | 기본값 | 설명 |
| --- | --- | --- |
| `MONGODB_URI` | `mongodb://localhost:27018` | MongoDB 연결 문자열입니다. compose 내부에서는 `mongodb://mongo:27017`을 주입합니다. |
| `MONGODB_DATABASE` | `dcss_arti_gallery` | 사용할 database 이름입니다. |
| `MONGODB_RAW_FILES_COLLECTION` | `raw_morgue_files` | raw morgue 원본 저장 컬렉션입니다. |
| `MONGODB_CRAWL_FILES_COLLECTION` | `crawl_files` | 파일별 crawl 상태 컬렉션입니다. |
| `MONGODB_CRAWL_USERS_COLLECTION` | `crawl_users` | user directory scan 상태 컬렉션입니다. |
| `MORGUE_BASE_URL` | `https://archive.nemelex.cards/morgue` | 원격 morgue root URL입니다. |
| `MORGUE_REQUEST_DELAY_SECONDS` | `1.0` | HTTP 요청 사이 최소 delay입니다. |
| `MORGUE_REQUEST_TIMEOUT_SECONDS` | `20.0` | HTTP 요청 timeout입니다. |
| `MORGUE_USER_AGENT` | `dcss-arti-gallery-crawler/0.1` | remote morgue 요청 user agent입니다. |
| `CRAWL_START_DATE` | `2026-01-01` | 대상 user/file 시작일입니다. |
| `CRAWL_LOOP_INTERVAL_SECONDS` | `604800` | worker pass 사이 대기 시간입니다. |
| `CRAWL_USER_SKIP_MODE` | `conservative` | `conservative` 또는 `modified_at`입니다. |
| `CRAWL_LOG_LEVEL` | `INFO` | worker logging level입니다. |
| `CRAWL_ONCE` | `false` | `1`, `true`, `yes`, `on`이면 한 번의 crawl pass만 실행하고 종료합니다. |

## 테스트

```sh
python3 -m unittest discover -s crawl_service/tests -t .
```

## 관련 상세 문서

- [Processing Layers](docs/ko/processing-layers.md)
- [Data Types](docs/ko/data-types.md)
