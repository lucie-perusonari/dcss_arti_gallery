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

1. raw text 앞부분에서 DCSS version을 추출하고 처리 대상 version인지 확인합니다.
2. raw 확장자에 따라 `.txt` 또는 `.lst` block을 찾습니다.
3. block title에서 artifact 후보 이름을 얻습니다.
4. `parser.py`로 display name, enchantment, base item, property token을 파싱합니다.
5. `cursed`/`chaotic` 같은 item status prefix를 제거한 이름으로 unrandart와 일반 magic item을 제외합니다.
6. `classifier.py`로 item metadata와 base/random attribute를 분리합니다.
7. `evaluator.py`로 점수와 등급을 계산합니다.
8. source version metadata, visible description, raw block, 위치 정보를 포함한 문서를 만듭니다.

## Version gate

처리 대상은 DCSS `0.29` 이상 정식 release와 trunk morgue입니다. Version 문자열이 없거나
`0.29` 미만이면 artifact 문서를 생성하지 않습니다. `bcrawl`, `bloatcrawl`, `hellcrawl`,
`custom`, `fork` 같은 비표준 suffix가 보이면 변종 데이터로 보고 저장하지 않습니다.

원문 title은 `raw_text_block`과 occurrence evidence에 유지하고, 저장 문서의 `name`에는
출력용 normalized name을 사용합니다.

`.txt` inventory 처리는 `Inventory:` 이후 필요한 item block만 순차적으로 생성합니다.
inventory line 목록과 block 목록을 별도 리스트로 모두 만들지 않아 raw file을 많이 재처리할 때
파일당 중간 할당을 줄입니다.

## 변경 시 주의점

- `extract_artifact_documents`는 발견한 occurrence를 `evaluation.total` 내림차순으로 반환합니다.
- `id`는 normalized artifact signature 기반 canonical key에서 만들어집니다.
- `occurrence_id`는 source file, line, raw name 기반 key에서 만들어집니다.
- `.lst`의 `item_location`, `item_source`는 갤러리의 위치/상점 표시 근거입니다.
