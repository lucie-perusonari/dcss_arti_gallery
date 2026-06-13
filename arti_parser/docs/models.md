# models.py

`models.py`는 MongoDB `artifacts` 컬렉션에 저장되는 artifact occurrence document shape를
정의합니다. 현재 문서는 raw source에서 관측된 occurrence 단위이며, canonical dedupe 설계는
상위 [ISSUE.md](../ISSUE.md)에 별도 이슈로 둡니다.

## 주요 모델

- `ArtifactDocumentSource`: 원본 player, file, URL, line metadata입니다.
- `ArtifactDocumentAttribute`: property token, normalized key/value, visible description입니다.
- `ArtifactDocumentEvaluation`: 점수와 등급 결과입니다.
- `ArtifactDocument`: 갤러리/API가 읽는 artifact occurrence read model 본문입니다.

## `ArtifactDocument` 핵심 필드

- `id`: artifact 문서 식별자입니다.
- `name`, `base_item`, `base_subtype`: 이름과 base item 정보입니다.
- `item_class`, `item_subtype`, `weapon_subtype`, `armour_slot`, `jewellery_slot`: 필터와 렌더링에
  쓰는 분류 필드입니다.
- `attributes`: property token별 normalized 값과 description입니다.
- `all_attributes`, `base_attributes`, `random_attributes`: 전체, intrinsic, random 속성입니다.
- `evaluation`: 점수와 등급입니다.
- `visible_item_description`, `visible_description_labels`, `raw_text_block`: UI 표시와 디버깅용
  원문 근거입니다.
- `item_location`, `item_source`: `.lst` 또는 `.txt`에서 확인한 위치/상점/source 정보입니다.
- `source`: player, source file, URL, line metadata입니다.

## 변경 시 주의점

- 모델은 `ConfigDict(frozen=True)`로 불변에 가깝게 사용됩니다.
- `to_dict`는 MongoDB 저장 전 `model_dump` 결과를 반환합니다.
- 필드 변경은 `api` response model, frontend TypeScript type, mock artifact 생성 스크립트와
  함께 맞춰야 합니다.
