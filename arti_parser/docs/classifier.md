# classifier.py

`classifier.py`는 파싱된 artifact를 갤러리 필터와 평가에 필요한 item metadata로 분류합니다.
특히 base intrinsic attribute와 실제 random attribute를 분리합니다.

## 주요 구성

- `ArtifactClassification`: item class/subtype, slot, brand, attribute 분리 결과입니다.
- `classify_artifact`: 분류 공개 함수입니다.

## 분류 결과

- `item_class`: `weapon`, `armour`, `jewellery`, `staff`, `talisman`, `misc`, `unknown`.
- `item_subtype`: class별 UI 표시와 필터에 쓰는 subtype입니다.
- `weapon_subtype`: weapon일 때 `melee` 또는 `ranged`.
- `armour_subtype`: armour일 때 `hat`, `helmet`, `pair of gloves`처럼 같은 slot 안의 원본 장비 타입입니다.
- `armour_slot`: armour일 때 `shield`, `helmet`, `boots`, `gloves`, `cloak`, `orb`,
  `body armour` 등입니다.
- `jewellery_slot`: jewellery일 때 `ring` 또는 `amulet`.
- `brand`: property token이나 이름에서 추론한 weapon brand입니다.
- `all_attributes`: visible token, brand, base intrinsic attribute를 합친 전체 속성입니다.
- `base_attributes`: base subtype/item이 원래 가지는 intrinsic 속성입니다.
- `random_attributes`: 평가에 들어가는 실제 랜덤 속성입니다.

## 변경 시 주의점

- 평가 입력은 `random_attributes`이므로 base/random 분리가 깨지면 점수가 왜곡됩니다.
- base subtype intrinsic 속성은 `BASE_SUBTYPE_ATTRIBUTES`, base item intrinsic 속성은
  `BASE_ITEM_ATTRIBUTES`에 의존합니다.
- slot 판정 데이터는 `constants.py`의 DCSS 정적 상수와 호환 alias에서 파생한 값을 사용합니다.
