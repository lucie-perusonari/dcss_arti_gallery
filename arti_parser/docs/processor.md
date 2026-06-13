# processor.py

`processor.py`는 raw morgue text 하나를 storage-ready `ArtifactDocument` 목록으로 변환하는
서비스 진입점입니다. 실제 추출은 `extractor.py`에 위임하지만, parser/scoring version을
소유한다는 점에서 재처리 계약의 중심입니다.

## 주요 구성

- `CURRENT_PARSER_VERSION`: 추출, 파싱, 분류 결과가 달라질 때 재처리를 유도하는 버전입니다.
- `CURRENT_SCORING_VERSION`: 평가 점수나 등급 결과가 달라질 때 재처리를 유도하는 버전입니다.
- `MorgueRawText`: processor가 받는 raw input DTO입니다.
- `ArtifactProcessor`: raw text를 artifact 문서 목록으로 변환합니다.

## 공개 동작

- `documents_from_raw_text`: `extract_artifact_documents`를 호출해 `ArtifactDocument` 목록을 반환합니다.
- `supported_extensions`: 현재 `txt`, `lst`를 반환합니다.

## 변경 시 주의점

- 새 확장자를 지원하려면 `supported_extensions`뿐 아니라 `extractor.py`의 확장자별 block 추출도
  함께 구현해야 합니다.
- parser/scoring version은 repository의 pending 판정과 저장 문서 metadata에 사용됩니다.
- 파싱 결과 변경은 `CURRENT_PARSER_VERSION`, 평가 결과 변경은 `CURRENT_SCORING_VERSION` 갱신을
  검토합니다.
