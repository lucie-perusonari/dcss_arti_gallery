# `run_raw_crawler.sh`

`run_raw_crawler.sh`는 `crawl_service.worker` 실행을 감싸는 shell wrapper입니다.

## 책임

- raw crawler 실행에 필요한 기본 환경을 준비합니다.
- `DETACH=1`일 때 worker를 백그라운드로 실행하고 `.logs/crawl_raw_only.log`에 기록합니다.
- 명시적인 MongoDB override가 없으면 개발 환경값을 사용합니다.

## 비소유 책임

- 저장된 raw source를 artifact read model로 재생성하지 않습니다. 해당 작업은 `arti_parser/process_raw_morgue_files.sh`가 담당합니다.

## 관련 문서

- [Processing Layers](processing-layers.md)
