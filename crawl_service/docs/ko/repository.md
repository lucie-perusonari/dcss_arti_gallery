# `repository.py`

`repository.py`는 remote morgue ingest 결과를 MongoDB에 저장하고 조회하는 persistence 계층입니다.

## 책임

- `raw_morgue_files`에 fetched raw source record를 저장합니다.
- `crawl_errors`에 fetch 실패 이벤트를 append-only로 저장합니다.
- worker가 중복 다운로드를 피하는 데 필요한 최소 조회를 제공합니다.

## 비소유 책임

- MongoDB index DDL은 `infra/`가 소유합니다.
- raw source 이후 artifact read model 재생성은 `arti_parser`가 소유합니다.

## 관련 문서

- [Processing Layers](processing-layers.md)
- [Data Types](data-types.md)
