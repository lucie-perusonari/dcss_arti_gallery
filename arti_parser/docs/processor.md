# processor.py

`processor.py`는 raw morgue text 하나를 storage-ready `ArtifactDocument` 목록으로 변환하는
서비스 진입점입니다. 실제 추출은 `extractor.py`에 위임합니다.

## 주요 구성

- `MorgueRawText`: processor가 받는 raw input DTO입니다.
- `ArtifactProcessor`: raw text를 artifact 문서 목록으로 변환합니다.

## 공개 동작

- `documents_from_raw_text`: `extract_artifact_documents`를 호출해 `ArtifactDocument` 목록을 반환합니다.
- `supported_extensions`: 현재 `txt`, `lst`를 반환합니다.

## 변경 시 주의점

- 새 확장자를 지원하려면 `supported_extensions`뿐 아니라 `extractor.py`의 확장자별 block 추출도
  함께 구현해야 합니다.
