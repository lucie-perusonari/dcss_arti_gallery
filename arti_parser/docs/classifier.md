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

## 장비 분류 정책

장비 artifact는 `weapon`, `armour`, `jewellery`, `staff`, `talisman`, `misc`, `unknown`으로
분류합니다. `item_subtype`은 UI 표시와 필터에 쓰는 세부 이름이며, 장신구, staff, talisman은 원문
bracket subtype을 우선 사용하고, armour는 slot 또는 base item을 사용합니다.

Weapon brand는 property token 또는 이름의 `of <brand>` 꼴에서 추론합니다. Brand는
`all_attributes`에는 들어갈 수 있지만 base intrinsic 속성과는 별개입니다. Morgue 표기 차이를
흡수하기 위해 다음 alias도 brand로 인식합니다.

- `flame` -> `flaming`
- `freeze` -> `freezing`
- `drain` -> `draining`
- `elec` -> `electrocution`
- `holy` -> `holy wrath`
- `protect` -> `protection`

원문 token은 보존하되, 같은 의미의 alias는 canonical brand로 묶어서 집계할 수 있어야 합니다.

Armour는 `armour_slot` 기준으로 UI 필터와 평가 보조 정보를 만듭니다. Body armour는 방해도 기준으로
경갑과 중갑을 나누며, 저장소 기준 `ER`은 `abs(ev_penalty) / 10`으로 환산합니다. Evaluator는
`ER >= 14`인 body armour를 중갑으로 봅니다.

Jewellery는 `jewellery_slot`을 `ring` 또는 `amulet`으로 단순화합니다. 원본 subtype은 display와
base intrinsic attribute 판정에 필요하므로 유지합니다.

Staff는 일반 weapon이 아니라 caster weapon으로 분류합니다. Staff subtype 자체는 마법 school과 원본
속성을 줄 수 있습니다.

## 후보 제외와 예외

- 고정 아티팩트는 저장 대상에서 제외합니다.
- `cursed` randart는 저장하되 표시 이름에서 `cursed` 접두사를 제거합니다.
- `cursed`/`chaotic` prefix는 item status로 보고 artifact 이름, base item 추론, token 표시에서
  제거합니다.
- Ashenzari skill boost는 artifact 고유 속성으로 보지 않고 `ignored_attributes`에만 보존합니다.
- DCSS `0.29` 이상 정식 release/trunk만 처리합니다.
- 변종 version suffix가 보이면 저장하지 않습니다.

## 변경 시 주의점

- 평가 입력은 `random_attributes`이므로 base/random 분리가 깨지면 점수가 왜곡됩니다.
- base subtype intrinsic 속성은 `BASE_SUBTYPE_ATTRIBUTES`, base item intrinsic 속성은
  `BASE_ITEM_ATTRIBUTES`에 의존합니다.
- slot 판정 데이터는 `constants.py`의 DCSS 정적 상수와 호환 alias에서 파생한 값을 사용합니다.
