# 크롤 서비스

`crawl_service`는 remote morgue user/file 목록 조회, txt/lst 원문 fetch, raw file MongoDB 저장,
crawl file/user cache 기록, background worker를 소유합니다.

HTTP API를 제공하지 않는 상주 worker 프로젝트이며, `api`, `frontend`, `admin-frontend`, `arti_parser`가 직접 의존해야 하는 대상이 아닙니다.

## 모듈

- [`fetcher.py`](docs/ko/fetcher.md): remote morgue root/user directory 조회, txt/lst 파일 목록 추출, 파일 본문 fetch
- [`repository.py`](docs/ko/repository.md): `raw_morgue_files`, `crawl_files`, `crawl_users`에 morgue ingest 상태 저장
- [`worker.py`](docs/ko/worker.md): archive user list scan과 raw morgue file ingest orchestration
- [`run_raw_crawler.sh`](docs/ko/run_raw_crawler.md): raw crawler 실행 wrapper
- [`run_raw_crawler_dev.sh`](docs/ko/run_raw_crawler.md): dev MongoDB 기본값으로 raw crawler 실행
- [`run_raw_crawler_prod.sh`](docs/ko/run_raw_crawler.md): prod MongoDB 값을 명시적으로 받아 raw crawler 실행
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

wrapper script:

```sh
crawl_service/run_raw_crawler.sh
```

- `crawl_service/run_raw_crawler.sh`: 호환용 dev wrapper입니다. 내부적으로 `run_raw_crawler_dev.sh`를 실행합니다.
- `crawl_service/run_raw_crawler_dev.sh`: dev MongoDB 기본값 `mongodb://localhost:27018`과 `dcss_arti_gallery`를 사용합니다.
- `MONGODB_URI=<prod-uri> crawl_service/run_raw_crawler_prod.sh`: 운영 MongoDB URI를 명시적으로 받아 실행합니다.
- `DETACH=1 crawl_service/run_raw_crawler_dev.sh`: dev raw crawler를 백그라운드로 실행하고 `.logs/crawl_raw_only_dev.log`에 기록합니다.
- `DETACH=1 MONGODB_URI=<prod-uri> crawl_service/run_raw_crawler_prod.sh`: prod raw crawler를 백그라운드로 실행하고 `.logs/crawl_raw_only_prod.log`에 기록합니다.

Docker Compose에서 crawler는 live morgue crawl을 수행하므로 기본 stack에는 포함되지 않고 `jobs` profile의
one-shot job으로만 실행합니다.

```sh
docker compose -f infra/dev/docker-compose.yml run --rm crawl-service
docker compose -f infra/prod/docker-compose.yml run --rm crawl-service
```

저장된 raw source를 artifact read model로 재생성하려면 `arti_parser/process_raw_morgue_files.sh`를 사용합니다.

## 테스트

```sh
python3 -m unittest discover -s crawl_service/tests -t .
```

## 관련 상세 문서

- [Processing Layers](docs/ko/processing-layers.md)
- [Data Types](docs/ko/data-types.md)
