# `worker.py`

`worker.py`는 remote morgue user scan과 raw file ingest를 조율하는 background worker입니다.

## 책임

- remote morgue root user list를 주기적으로 스캔합니다.
- 대상 user directory에서 `.txt`, `.lst` 파일 목록을 확인합니다.
- 같은 pass 안의 중복 파일명과 이미 fetched 상태로 저장된 파일을 건너뜁니다.
- HTTP 요청 pacing, 날짜 필터, user skip mode를 적용합니다.
- fetch 결과와 실패 상태를 repository에 기록합니다.

## 비소유 책임

- HTTP API를 제공하지 않습니다.
- artifact parsing/scoring/storage를 수행하지 않습니다.

## 관련 문서

- [Processing Layers](processing-layers.md)
- [Data Types](data-types.md)
