# worker.py

`worker.py`는 기존 호출 호환을 위한 batch entrypoint alias입니다. 새 처리 로직을 담기보다
`batch.py`를 재노출하는 얇은 wrapper 역할을 합니다.

## 주요 구성

- `ArtifactProcessingWorker = ArtifactProcessingBatchProcessor`
- `ArtifactProcessingConfig`, `ArtifactProcessingSummary`, `main`, `processing_summary_message` re-export.
- `python3 -m arti_parser.worker` 실행 지원.

## 변경 시 주의점

- 기존 운영 스크립트나 배포 설정이 `worker.py`를 호출할 수 있으므로 제거에 주의합니다.
- 새 batch 동작은 `batch.py`에 두고 이 파일은 호환 계층으로 유지합니다.
