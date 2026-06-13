# evaluator.py

`evaluator.py`는 `random_attributes`와 item metadata를 사용해 artifact 자체의 절대 가치를
점수화합니다. 평가는 100점 만점의 상대 점수가 아니라 각 아이템 가치 요소의 합산 점수입니다.

base item의 intrinsic 속성이 아니라 실제 랜덤 속성을 기준으로 평가하는 것이 핵심 계약입니다. 다만
weapon base tier나 staff subtype처럼 아이템 자체의 사용 가치를 결정하는 metadata는 별도 base
score로 반영합니다.

## 주요 함수

- `evaluate_artifact_data`: 평가 공개 함수입니다.
- `weapon` evaluator: 일반 무기의 공격 가치를 계산합니다.
- `staff` evaluator: caster weapon인 magical staff의 가치를 계산합니다.
- `armour` evaluator: 방어구의 enchantment, 저항, slay, regen 같은 가치를 계산합니다.
- `jewellery` evaluator: 장신구의 옵션 조합 가치를 계산합니다.
- fallback evaluator: `talisman`, `misc`, 미분류 장비를 보수적으로 계산합니다.
- penalty evaluator: 장비군별로 위험도가 다른 penalty token을 감점합니다.

## 출력

- `total`: 하한 0의 절대 점수입니다. 100점 만점으로 clamp하지 않습니다.
- `practical_score`: 현재 `total`과 같은 절대 점수입니다.
- `rarity_score`: 후속 작업에서 재정의할 예정이며, 현재 절대 가치 평가의 중심 축이 아닙니다.
- `offense`, `defense`, `utility`, `penalty`, `base_fit`: 세부 점수입니다.
- `grade`, `luxury_grade`: 후속 작업에서 점수 분포를 보고 재정의합니다.

## 공통 원칙

- 평가는 source, player, `.txt`/`.lst` 출처와 무관해야 합니다.
- 장비군별 evaluator를 사용합니다. 일반 무기, staff, armour, jewellery, 기타 장비는 서로 다른
  기준으로 평가합니다.
- 최종 점수는 가치 요소의 합산이며, 하한은 0입니다.
- 알 수 없는 token은 추정 가점이나 추정 감점을 하지 않고 0점 처리합니다.
- grade label은 절대 점수 분포를 확인한 뒤 별도 작업으로 정합니다.

## 공통 Penalty 기준

Penalty는 weapon, staff, armour, jewellery, fallback 장비군에서 기본적으로 같은 기준을 사용합니다.
장비군별로 직접 관련된 일부 penalty만 override합니다.

Penalty는 주요 저항 1개를 기준 단위로 해석합니다. 주요 저항 1개는 대략 `+12`점입니다. 심각한
penalty는 주요 저항 3개 손실에 준하고, `Bane`은 주요 저항 2개 손실에 준합니다.

- `*Slow`, `-Tele`, `*Silence`: `-36`
- `Bane`: `-24`
- `Harm`: `-24`
- `-Cast`: `-20`
- `*Corrode`: `-18`
- `*Rage`: `-24`
- `rF-`, `rC-`, `Will-`, `rElec-`, `rPois-`, `rCorr-`: step당 `-12`
- `rN-`: step당 `-6`
- `Str-`, `Dex-`, `Int-`: point당 `-2`
- `^Fragile`, `^Drain`, `^Contam`: `-8`
- `*Noise`: `-5`
- `Stlth-`: step당 `-2`

Penalty token은 반드시 감점합니다. `^Fragile`, `^Drain`, `^Contam`처럼 장비를 벗을 때 주로 발생하는
penalty도 예외 없이 감점하되, `*Slow`, `-Tele`, `*Silence`보다 낮게 봅니다.

## 공통 Attribute 기준

Attribute도 먼저 공통 table로 정의하고, 장비군별 evaluator가 multiplier나 override를 적용합니다.
이렇게 하면 같은 token의 기본 가치를 한 곳에서 설명하고, weapon처럼 일부 가치가 낮아지는 장비군만
명시적으로 조정할 수 있습니다.

### 공통 저항/방어 Attribute

- `rF+`, `rC+`, `Will+`: step당 `+12`
- `rN+`: step당 `+6`
- `rElec`, `rPois`, `rCorr`: `+12`
- `AC+`, `EV+`, `SH+`: point당 `+3`

### 공통 주요 Utility

- `Regen+`: `+24`
- `SInv`, `Reflect`, `Wiz`, `RegenMP`: `+18`

### 공통 낮은 Utility

- `Fly`, `+Blink`, `+Inv`, `Rampage`, `Clar`, `Wildshape`, `Chemistry`, `Acrobat`, `Spirit`: `+6`
- `MP+`: point당 `+1`

### 공통 Stat

- `Str+`, `Dex+`, `Int+`: point당 `+2`
- `Str-`, `Dex-`, `Int-`: point당 `-2`

Stat 6 point를 주요 저항 1개와 비슷한 가치로 봅니다.

### 장비군별 조정

- weapon은 저항/방어/utility 계열의 가치를 공통값의 `0.5`배로 낮추거나, weapon 기준에서 무의미한
  token은 0점 처리합니다.
- weapon의 공격 stat은 별도 기준을 사용합니다. `Str+`, `Dex+`는 point당 `+3`, `Slay+`는 point당
  `+9`, `Int+`는 0점입니다.
- staff는 caster 관련 token을 override합니다. `Archmagi`, `Wiz`, `RegenMP`, `Int+`, `MP+`,
  spell school 조합은 staff 기준을 사용합니다.
- armour와 jewellery는 공통 저항/방어/utility/stat 기준을 기본으로 사용하고, 각 장비군의 핵심
  attribute만 override합니다.

## Weapon 평가 기준

Weapon은 공격 도구로 평가합니다. 무기 자체의 가치는 `base weapon`, `enchantment`, `brand`,
`Slay`/`Str`/`Dex`, 일부 예외 유틸리티, 명시적 penalty만 반영합니다.

무기에 붙은 저항, `Will+`, `SInv`, `MP+`, `Stlth+`, `Fly` 같은 방어/유틸 옵션은 weapon 자체
가치에서 낮게 봅니다. 기본적으로 공통값의 `0.5`배를 적용합니다.

### Base Weapon

Base weapon은 tier가 아니라 weapon별 점수표를 사용합니다. 판단 기준은 공격력과 최소 공속입니다.
명중률은 v1 기준에서 제외합니다.

구현 시 evaluator 또는 constants에 `WEAPON_BASE_SCORES` 같은 명시 table을 둡니다. 이 table은 각
weapon의 damage와 min delay를 기준으로 계산하거나 수동으로 고정합니다. 공식 data에서 min delay를
직접 제공하지 않는 경우에는 base delay에서 추정한 min delay를 사용합니다.

- damage가 높을수록 가점합니다.
- min delay가 낮을수록 가점합니다.
- 명중률은 점수에 반영하지 않습니다.
- unknown weapon base는 낮은 안전값을 사용합니다.

### Enchantment

- positive enchantment: enchant point당 `+3`
- negative enchantment: enchant point당 `-3`

Enchantment는 중요하지만 `Slay`보다 압도적으로 강하지 않습니다.

### Brand

- `speed`: `+30`
- normal attack brand: `+15`
- weak/situational brand: `+8`
- no brand: `+0`
- unknown brand: `+0`

Normal attack brand는 `elec`, `heavy`, `flame`, `freeze`, `holy`, `vampirism`, `antimagic`,
`spectral`, `drain`, `venom`, `pain` 계열을 포함합니다.

Weak/situational brand는 `chaos`, `protection`, `distortion` 계열을 포함합니다.

### 공격 Attribute

- `Slay+`: point당 `+9`
- `Str+`: point당 `+3`
- `Dex+`: point당 `+3`
- `Int+`: `+0`

`Str`/`Dex`는 v1에서 stat 3당 `Slay` 1과 같은 가치로 봅니다.

### Weapon Utility

- weapon의 저항/방어/utility 계열 token은 공통 attribute 기준의 `0.5`배를 적용합니다.
- `Regen+`: `+12`
- `SInv`, `Reflect`, `Wiz`, `RegenMP`: `+9`
- low utility: `+3`
- `MP+`: point당 `+0.5`

### Penalty

Weapon은 공통 penalty 기준을 사용합니다. 다만 weapon 공격성과 직접 연결되는 `Str-`, `Dex-`는
point당 `-4`로 더 크게 감점하고, `Int-`는 point당 `-1`로 낮게 감점합니다.

### Unknown / New Token

Weapon evaluator가 모르는 token은 0점 처리합니다. 모르는 token에 대해 추정 가점이나 추정 감점을
하지 않습니다.

### Final

```text
weapon_total = max(0, base + enchantment + brand + offense + utility - penalty)
```

## Staff 평가 기준

Staff는 일반 weapon이 아니라 caster weapon으로 평가합니다. Staff suffix/subtype 자체에는 기본점을
주지 않고, 실제 가치는 `Archmagi`, `Wiz`, `RegenMP`, spell school token의 조합과 일부 caster
stat에서 발생합니다.

### Staff Subtype

Staff suffix/subtype 자체는 0점입니다. `staff of fire`, `staff of earth`, `staff of
conjuration`이라는 사실만으로 점수를 주지 않습니다.

### Caster Attribute

- `Archmagi`: `+30`
- `Wiz`: `+24`
- `RegenMP`: `+20`
- `Int+`: point당 `+3`
- `MP+`: point당 `+1`
- `Str+`, `Dex+`: `+0`

`Archmagi`, `Wiz`, `RegenMP`는 높은 가점을 줍니다. `Int+`는 가점을 주지만 이 세 token보다 낮게
봅니다. `MP+`는 caster utility로 평가하되 `Int+`보다도 낮은 가중치를 사용합니다.

### Spell School 조합

Spell school token은 단순히 여러 개가 있다고 더 높게 평가하지 않습니다. 의미 있는 조합일 때만
보너스를 줍니다.

- `Conj`와 직접 화력 학파가 함께 있으면 조합 보너스를 줍니다.
- 예: `Fire + Conj`, `Ice + Conj`, `Earth + Conj`, `Alch + Conj`
- 속성 학파끼리 여러 개 있는 경우에는 약한 조합 보너스를 줍니다.
- 예: `Fire + Ice`, `Fire + Air`, `Ice + Earth`
- 같은 계열이 중첩되거나 조합이 늘어나는 경우에는 추가 점수를 받을 수 있습니다.

점수는 다음 기준을 사용합니다.

- single school token: `+5`
- `Conj` + direct damage school 조합: `+18`
- elemental school끼리의 조합: `+8`
- 추가 school 조합: 조합당 `+4`

Direct damage school은 `Fire`, `Ice`, `Earth`, `Alch`, `Air`를 포함합니다. Elemental school은
`Fire`, `Ice`, `Earth`, `Air`를 포함합니다.

### 방어/저항 Attribute

Staff의 방어/저항 옵션은 spell school 단일 가점과 비슷한 낮은 가중치로 평가합니다.

- `rF+`, `rC+`, `rN+`, `Will+`는 step이 중첩될수록 추가 점수를 줍니다.
- `rElec`, `rPois`, `rCorr`, `SInv`는 단일 저항/유틸 가점으로 평가합니다.
- 여러 방어/저항 옵션이 함께 있으면 조합 가치를 약하게 추가할 수 있습니다.
- 방어/저항 옵션은 `Archmagi`, `Wiz`, `RegenMP`, 의미 있는 school 조합보다 낮게 봅니다.

점수는 다음 기준을 사용합니다.

- `rF+`, `rC+`, `rN+`, `Will+`: step당 `+5`
- `rElec`, `rPois`, `rCorr`, `SInv`: `+5`
- 방어/저항 옵션 2개 이상: 추가 `+4`
- 방어/저항 옵션 3개 이상: 추가 `+4`

### Penalty

Staff는 공통 penalty 기준을 사용합니다. 다만 caster 기능을 막는 penalty와 caster stat 관련 penalty는
staff 전용 가중치로 override합니다.

- `*Silence`는 최악의 penalty로 봅니다.
- `-Cast`는 `*Silence` 다음으로 크게 감점합니다.
- `rF-`, `rC-`, `rN-`, `Will-`, `rElec-`, `rPois-`, `rCorr-` 같은 저항 감소는 평범하게 나쁜
  penalty로 봅니다.
- `Int-`는 3 point당 저항 감소 1 step과 비슷한 가치로 감점합니다.
- `MP-`는 `Int-`보다 낮은 가중치로 감점합니다.

Override 점수는 다음 기준을 사용합니다.

- `*Silence`: `-40`
- `-Cast`: `-30`
- `Int-`: 3 point당 `-8`
- `MP-`: point당 `-1`

그 밖의 penalty는 공통 penalty 기준을 그대로 사용합니다.

### Staff Final

```text
staff_total = max(0, caster_attribute + school + defense + penalty)
```

## Armour 평가 기준

Armour는 방어 장비로 평가합니다. 가장 중요한 값은 armour base item의 기본 방어도이며, 그와 거의
비슷한 수준으로 저항 보유 여부를 중요하게 봅니다.

### Base Armour AC

Armour evaluator는 `base_item`별 기본 방어도 table을 사용해야 합니다. 현재 `dcss_data.py`는 armour
slot mapping만 제공하므로, 구현 시 evaluator 또는 constants에 `ARMOUR_BASE_AC` 같은 명시 테이블을
추가합니다.

기본 방어도는 armour 가치의 중심입니다. Body armour는 기본 방어도 차이가 크므로 base AC가 점수에
강하게 반영되어야 합니다. Cloak, boots, gloves, helmet 같은 보조 방어구는 base AC 차이가 작으므로
slot별 기본값을 사용합니다.

점수는 기본 방어도 1당 `+3`을 기준으로 합니다. 보조 방어구처럼 base AC가 낮은 slot도 장착 slot 자체의
가치를 반영하기 위해 최소 base score를 둡니다.

- body armour: `base_ac * 3`
- shield: `base_ac * 3`
- cloak, boots, gloves, helmet: 최소 `+15`
- orb/scarf/기타 방어 slot: 최소 `+10`
- unknown armour base: `+10`

### Enchantment / AC

Armour enchantment는 weapon enchantment와 유사한 가중치로 봅니다. 차이는 armour enchantment가
실질적으로 AC와 같은 가치라는 점입니다.

- positive enchantment: enchant point당 `+3`
- `AC+`: point당 `+3`
- negative enchantment: enchant point당 `-3`
- `AC-`: point당 `-3`

### 저항

저항 보유 여부는 기본 방어도와 거의 비슷한 수준으로 중요합니다.

- `rF+`, `rC+`, `rN+`, `Will+`는 step이 중첩될수록 추가 점수를 줍니다.
- `rElec`, `rPois`, `rCorr`는 단일 저항으로 가점합니다.
- 여러 저항이 함께 있으면 조합 가치를 추가로 줄 수 있습니다.

점수는 다음 기준을 사용합니다.

- `rF+`, `rC+`, `Will+`: step당 `+12`
- `rN+`: step당 `+6`
- `rElec`: `+12`
- `rPois`: `+10`
- `rCorr`: `+8`
- 저항 2종 이상: 추가 `+8`
- 저항 3종 이상: 추가 `+8`

### Armour에서 중요한 Random Attribute

- `Slay+`는 높은 가치를 가집니다.
- `Regen+`은 높은 가치를 가집니다.
- `SInv`, `Rampage`, `+Inv`, `+Blink`는 유효한 utility로 평가합니다.
- `Str+`, `Dex+`, `Int+` 같은 단순 stat은 크게 영향을 주지 않습니다.

점수는 다음 기준을 사용합니다.

- `Regen+`: `+16`
- `Slay+`: point당 `+9`
- `EV+`, `SH+`: point당 `+3`
- `SInv`: `+6`
- `Rampage`: `+6`
- `+Inv`, `+Blink`: `+4`
- `MP+`: point당 `+1`
- `Str+`, `Dex+`, `Int+`: point당 `+1`

### Armour Penalty

Armour penalty는 반드시 감점합니다. 저항 감소와 `-Tele`, `*Slow`, `*Silence`, `Harm`, `Bane` 같은
강한 penalty는 장비 자체 가치를 크게 낮춥니다. 단순 stat 감소는 낮은 가중치로 감점합니다.
Armour는 공통 penalty 기준을 그대로 사용합니다.

### Armour Final

```text
armour_total = max(0, base_ac + enchantment_or_ac + resistance + key_attributes - penalty)
```

## Jewellery 평가 기준

Jewellery는 base AC나 enchantment가 없으므로 옵션 조합 자체로 평가합니다. 특히 `Regen+`은 매우 높은
가치를 가지며, 저항과 `Will+`도 높은 가치로 봅니다.

### Base Jewellery

Ring/amulet 자체에는 높은 기본점을 주지 않습니다. Jewellery의 가치는 대부분 random attribute에서
발생합니다.

### 핵심 Attribute

- `Regen+`은 매우 높은 가치를 가집니다.
- `rF+`, `rC+`, `Will+`, `rElec`, `rPois`, `rCorr`는 높은 가치를 가집니다.
- `rN+`은 위 주요 저항보다 낮게 평가합니다.
- `Slay+`, `AC+`, `EV+`, `SH+`는 point 4당 주요 저항 하나와 비슷한 가치로 봅니다.

점수는 다음 기준을 사용합니다.

- `Regen+`: `+24`
- `rF+`, `rC+`, `Will+`: step당 `+12`
- `rElec`, `rPois`, `rCorr`: `+12`
- `rN+`: step당 `+6`
- `Slay+`, `AC+`, `EV+`, `SH+`: point당 `+3`

### Stat

`Str+`, `Dex+`, `Int+`는 jewellery에서 의미가 있지만 주요 저항, `Regen+`, `Slay+`, `AC+`보다 낮게
봅니다. Stat 감소는 반드시 감점합니다.

점수는 다음 기준을 사용합니다.

- `Str+`, `Dex+`, `Int+`: point당 `+2`
- `Str-`, `Dex-`, `Int-`: point당 `-2`

Stat 6 point를 주요 저항 1개와 비슷한 가치로 봅니다.

### Utility

Jewellery에서는 `SInv`, `Reflect`, `Wiz`, `RegenMP`를 높은 utility로 평가합니다. 나머지 utility는
그보다 낮게 평가합니다.

- high utility: `SInv`, `Reflect`, `Wiz`, `RegenMP`: `+18`
- low utility: `Fly`, `+Blink`, `+Inv`, `Rampage`, `Clar`, `Wildshape`, `Chemistry`, `Acrobat`,
  `Spirit`: `+6`
- `MP+`: point당 `+1`

High utility는 주요 저항 약 1.5개 수준으로 봅니다. Low utility는 주요 저항보다 낮게 봅니다.

### Jewellery Penalty

Penalty는 반드시 감점합니다. `*Slow`, `Bane`, `-Tele`, `*Silence`, `Harm` 같은 강한 penalty는 큰
감점을 적용합니다. 저항 감소와 stat 감소도 감점합니다.

Jewellery penalty는 weapon/armour와 같은 공통 penalty 기준을 사용합니다.

### Jewellery Final

```text
jewellery_total = max(0, resistance + combat_stats + stat + utility - penalty)
```

## Talisman / Misc / Fallback 평가 기준

`talisman`, `misc`, 미분류 장비는 별도 장비군 고유 점수표를 만들지 않고 앞서 정한 공통 기준에 따라
보수적으로 처리합니다.

- 저항, `Will+`, `Regen+`, `Slay+`, `AC+`, `EV+`, `SH+`, utility는 jewellery 기준을 재사용합니다.
- positive stat은 jewellery 기준을 재사용합니다.
- penalty는 weapon/armour/jewellery와 같은 공통 penalty 기준을 재사용합니다.
- 알 수 없는 token은 0점 처리합니다.

```text
fallback_total = max(0, shared_positive_attributes - shared_penalty)
```

## 변경 시 주의점

- 평가 입력은 반드시 `classification.random_attributes`여야 합니다.
- staff subtype처럼 아이템 자체 가치를 결정하는 metadata는 random attribute가 아니어도 base score로
  반영할 수 있습니다.
- scoring formula 변경은 기존 저장 문서 재평가가 필요하므로 `CURRENT_SCORING_VERSION` 갱신을
  검토합니다.
- 등급 label은 frontend 표시와 맞물릴 수 있습니다.
