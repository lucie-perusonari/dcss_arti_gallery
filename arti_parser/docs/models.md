# models.py

`models.py`는 MongoDB `artifacts` 컬렉션에 저장되는 canonical artifact document shape를
정의합니다. raw source에서 관측된 occurrence identity는 `occurrence_id`와 `sources` evidence로
보존합니다.

## 주요 모델

- `ArtifactDocumentSource`: 원본 player, file, URL, line metadata입니다.
- `ArtifactDocumentAttribute`: property token, normalized key/value, visible description입니다.
- `ArtifactDocumentEvaluation`: 점수와 등급 결과입니다.
- `ArtifactDocument`: 갤러리/API가 읽는 canonical artifact read model 본문입니다.

## `ArtifactDocument` 핵심 필드

- `id`: normalized artifact signature 기반 canonical artifact 식별자입니다.
- `occurrence_id`: 대표 occurrence의 source file, line, raw name 기반 식별자입니다.
- `canonical_key`: canonical `id` 계산에 쓰는 normalized artifact signature입니다.
- `name`, `base_item`, `base_subtype`: 이름과 base item 정보입니다.
- `item_class`, `item_subtype`, `weapon_subtype`, `armour_slot`, `jewellery_slot`: 필터와 렌더링에
  쓰는 분류 필드입니다.
- `attributes`: property token별 normalized 값과 description입니다.
- `all_attributes`, `base_attributes`, `random_attributes`: 전체, intrinsic, random 속성입니다.
- `evaluation`: 점수와 등급입니다.
- `visible_item_description`, `visible_description_labels`, `raw_text_block`: UI 표시와 디버깅용
  원문 근거입니다.
- `item_location`, `item_source`: 대표 occurrence에서 확인한 위치/상점/source 정보입니다.
- `source`: 대표 occurrence의 player, source file, URL, line metadata입니다.
- `sources`, `occurrence_ids`, `source_count`, `first_source`, `first_discovered_by`, `known_seeds`, `updated_at`: repository가
  저장 시 추가하는 canonical source evidence metadata입니다.
- `sources[].game_ended_at`, `latest_game_ended_at`: `morgue-<player>-YYYYMMDD-HHMMSS.*` 파일명에서 파싱한
  게임 시각입니다. Gallery API가 최근 게임 범위를 제한할 때 사용합니다.
- `artifact_processing_files.metadata_version`: 저장 문서 보조 metadata가 추가될 때 기존 raw file을
  한 번 다시 처리하기 위한 processing record version입니다.

## 변경 시 주의점

- 모델은 `ConfigDict(frozen=True)`로 불변에 가깝게 사용됩니다.
- `to_dict`는 MongoDB 저장 전 `model_dump` 결과를 반환합니다.
- 필드 변경은 `api` response model과 frontend TypeScript type을 함께 맞춰야 합니다.
