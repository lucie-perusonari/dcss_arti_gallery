# `repository.py`

`repository.py`는 MongoDB crawl 상태 컬렉션을 읽는 Admin API persistence 계층입니다.

## 책임

- `raw_morgue_files`, `artifact_processing_files`, `crawl_errors`, `artifacts`에서 dashboard 요약에 필요한 값을 읽습니다.
- fetch/process/crawl 상태 count와 latest activity를 계산합니다. process 상태는 `artifact_processing_files`를 우선 사용하고,
  record가 없으면 legacy `raw_morgue_files.process_status`를 fallback으로 사용합니다.
- 최근 오류 목록을 admin 응답에 맞게 정리합니다.

## 비소유 책임

- crawl 상태 쓰기는 `crawl_service`가 소유합니다.
- collection index DDL은 `infra/`가 소유합니다.

## 관련 문서

- [Processing Layers](processing-layers.md)
