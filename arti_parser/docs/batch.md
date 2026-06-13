# batch.py

`batch.py`는 MongoDB에 저장된 fetched raw morgue file을 batch 단위로 처리하는 실행
entrypoint입니다. 처리할 raw file을 고르고, `ArtifactProcessor`를 호출하고, 성공/실패 결과를
repository에 기록합니다.

## 주요 구성

- `ArtifactProcessingConfig`: `batch_size`, `scan_batch_size` 설정입니다.
- `ArtifactProcessingSummary`: batch 실행 결과 집계입니다.
- `ArtifactProcessingBatchProcessor`: pending raw file 조회, raw file별 처리, 저장을 조율합니다.
- `processing_summary_message`: 로그에 남길 summary 문자열을 만듭니다.
- `main`: `python3 -m arti_parser.batch` CLI entrypoint입니다.

## 처리 흐름

1. repository에서 pending raw file을 조회합니다.
2. raw file을 `MorgueRawText`로 바꾸고 `ArtifactProcessor.documents_from_raw_text`를 호출합니다.
3. 성공하면 artifact upsert, stale artifact 삭제, 처리 완료 record 저장을 repository에 위임합니다.
4. 예외가 발생하면 실패 record를 저장하고 다음 raw file 처리를 계속합니다.

## 변경 시 주의점

- 이 모듈은 원격 morgue crawl을 수행하지 않습니다.
- raw file 하나의 실패가 batch 전체를 중단하지 않는 동작을 유지해야 합니다.
- CLI 옵션과 환경 변수는 서비스 README의 실행 계약과 함께 갱신해야 합니다.
