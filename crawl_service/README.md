# 크롤 서비스

`crawl_service`는 remote morgue fetch, raw file 저장, 저장된 raw text 처리, artifact document 생성,
MongoDB write, crawl file/user cache, background worker를 소유합니다.

HTTP API를 제공하지 않는 상주 worker 프로젝트이며, `api`나 frontend가 직접 import하는 대상이 아닙니다.

English version: [README.en.md](README.en.md)

## 책임

- `morgue`: morgue directory 조회, txt/lst 파일 목록 추출, raw text 변환
- `core/processor.py`: 저장된 raw morgue 원본에서 artifact read model 재생성
- `artifacts`: artifact raw evidence 추출, 이름/속성/분류 파싱, 평가, Pydantic 저장 문서 모델
- `core/repository.py`: raw file, artifact read model, crawl cache repository
- `cli/worker.py`: archive user list scan과 raw morgue file ingest
- `core/observability.py`: worker pass logging과 runtime summary formatting

## 데이터 흐름

핵심 흐름은 원본을 먼저 저장하고 저장된 원본을 나중에 처리하는 것입니다.

1. worker가 remote morgue 파일을 fetch합니다.
2. `raw_morgue_files`에 원문, content hash, fetch 상태를 저장합니다.
3. 저장된 원본을 `crawl_service.core.processor`가 parse/classify/evaluate/document build 단계로 처리합니다.
4. 결과를 `artifacts` read model로 재생성합니다.
5. raw 저장 완료 파일 cache는 `crawl_files`에, user scan 상태는 `crawl_users`에 기록합니다.

네트워크 실패는 fetch 상태와 `fetch_error`에 기록하고, 처리 실패는 process 상태와 `process_error`에 따로 기록합니다.

## 실행

dependencies:

```sh
python3 -m venv .venv

sudo apt update
sudo apt install -y python3-venv python3-pip

rm -rf .venv
python3 -m venv .venv

.venv/bin/python -m pip install --upgrade pip
.venv/bin/python -m pip install -r requirements.txt
```

local MongoDB:

```sh
eval "$(infra/mongo/mongo_up.sh)"
```

worker:

```sh
python3 -m crawl_service.cli.worker
```

worker는 archive의 전체 user directory list를 주 1회 훑고, 대상 user directory를 열어
누락 파일을 확인합니다. 이미 `raw_morgue_files`에 저장된 fetched 파일은 다시 다운로드하지 않습니다.
`CRAWL_USER_SKIP_MODE=modified_at`을 설정하면 user directory Date가 바뀐 player만 조회합니다.
2026-01-01 이후 user/file 데이터만 처리하며 모든 HTTP 요청 사이에 기본 1초 delay를 둡니다.
worker는 원본을 `raw_morgue_files`에 저장하는 것까지만 책임집니다.

### Raw 수집과 별도 처리

artifact 재생성은 worker가 아니라 processor script로 별도 실행합니다.

```sh
crawl_service/run_raw_crawler.sh
crawl_service/process_raw_morgue_files.sh
```

- `crawl_service/run_raw_crawler.sh`: worker를 실행해 fetched raw file만 저장합니다.
- `DETACH=1 crawl_service/run_raw_crawler.sh`: raw crawler를 백그라운드로 실행하고 `.logs/crawl_raw_only.log`에 기록합니다.
- `crawl_service/process_raw_morgue_files.sh`: `raw_morgue_files`의 fetched/pending 또는 version mismatch record를 처리합니다.
- `PROCESS_LIMIT=1000`: processor batch 크기입니다. 기본값은 `1000`입니다.
- `ONCE=1`: processor를 한 batch만 실행하고 종료합니다.

## 테스트

```sh
python3 -m unittest discover -s crawl_service/tests -t .
```

scoring 변경은 evaluator 테스트와 함께 [Artifact Scoring Formula](docs/ko/artifact_scoring_formula.md)를 대조합니다.
DCSS item data 변경은 [DCSS Item Data](docs/ko/dcss_item_data.md)의 regeneration 절차를 따릅니다.

## 관련 공유 문서

- [Processing Layers](docs/ko/processing-layers.md)
- [Data Types](docs/ko/data-types.md)
- [Artifact Scoring Formula](docs/ko/artifact_scoring_formula.md)
- [Randart Properties](docs/ko/randart_properties.md)
- [DCSS Item Data](docs/ko/dcss_item_data.md)
- [Randart Corpus](docs/ko/research/randart-corpus/README.md)
- [Harness Validation](../docs/ops/harness/validation.md)
