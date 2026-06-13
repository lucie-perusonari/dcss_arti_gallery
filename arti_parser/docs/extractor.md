# extractor.py

`extractor.py`는 `.txt`, `.lst` raw text에서 artifact 후보 block을 찾고 최종
`ArtifactDocument` 조립을 지휘하는 중심 모듈입니다.

## 주요 구성

- `MorgueRawText`: extractor가 요구하는 raw input protocol입니다.
- `extract_artifact_documents`: raw text 하나를 artifact 문서 목록으로 변환하는 공개 함수입니다.
- `_txt_blocks`: morgue `.txt`의 `Inventory:` 섹션에서 item block을 추출합니다.
- `_lst_blocks`: `.lst` 파일의 level, 좌표, shop 문맥을 유지하며 item block을 추출합니다.
- `_description_lines`: visible description, label, bracket subtype을 추출합니다.
- `_artifact_document_from_parts`: parser, classifier, evaluator 결과를 `ArtifactDocument`로 합칩니다.

## 처리 흐름

1. raw 확장자에 따라 `.txt` 또는 `.lst` block을 찾습니다.
2. block title에서 artifact 후보 이름을 얻습니다.
3. `parser.py`로 display name, enchantment, base item, property token을 파싱합니다.
4. unrandart와 일반 magic item을 제외합니다.
5. `classifier.py`로 item metadata와 base/random attribute를 분리합니다.
6. `evaluator.py`로 점수와 등급을 계산합니다.
7. source metadata, visible description, raw block, 위치 정보를 포함한 문서를 만듭니다.

## 변경 시 주의점

- `extract_artifact_documents`는 같은 raw file 안의 중복 document id를 dedupe하고
  `evaluation.total` 내림차순으로 반환합니다.
- artifact id는 source file, line, raw name 기반 key에서 만들어집니다.
- `.lst`의 `item_location`, `item_source`는 갤러리의 위치/상점 표시 근거입니다.
