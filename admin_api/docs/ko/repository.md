# `repository.py`

`repository.py`는 MongoDB crawl 상태 컬렉션을 읽는 Admin API persistence 계층입니다.

## 책임

- `raw_morgue_files`, `crawl_files`, `crawl_users`, `artifacts`에서 dashboard 요약에 필요한 값을 읽습니다.
- fetch/process/crawl 상태 count와 latest activity를 계산합니다.
- 최근 오류 목록을 admin 응답에 맞게 정리합니다.

## 비소유 책임

- crawl 상태 쓰기는 `crawl_service`가 소유합니다.
- collection index DDL은 `infra/`가 소유합니다.

## 관련 문서

- [Processing Layers](processing-layers.md)
