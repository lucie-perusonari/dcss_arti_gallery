# evaluator.py

`evaluator.py`는 item metadata와 장비군별 평가 attribute를 사용해 artifact 자체의 절대 가치를
점수화합니다. 평가는 100점 만점의 상대 점수가 아니라 각 아이템 가치 요소의 합산 점수입니다.

weapon/staff/fallback은 실제 랜덤 속성을 기준으로 평가하고, armour/jewellery는 base item intrinsic
옵션까지 포함한 `all_attributes`를 기준으로 평가합니다. Armour와 jewellery는 `ring of poison
resistance`, `amulet of reflection`, dragon scales intrinsic resistance 같은 base option 자체가
실사용 가치의 일부이므로 점수에 포함합니다.

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

Penalty는 주요 저항 1개를 기준 단위로 해석합니다. 주요 저항 1개는 대략 `+10`점입니다. 심각한
penalty는 주요 저항 3개 손실에 준하고, `Bane`은 주요 저항 2개 손실에 준합니다.

- `*Slow`, `-Tele`, `*Silence`: `-36`
- `Bane`: `-24`
- `Harm`: `-24`
- `-Cast`: `-20`
- `*Corrode`: `-18`
- `*Rage`: `-24`
- `rF-`, `rC-`, `Will-`, `rCorr-`: step당 `-15`
- `rElec-`, `rPois-`: step당 `-19.5`
- `rN-`: step당 `-7.5`
- `Str-`, `Dex-`, `Int-`: 총 감소량 4까지는 0점, 4를 넘는 초과분만 point당 `-1.67`
- `^Fragile`, `^Drain`, `^Contam`: `0`
- `*Noise`: `-5`
- `Stlth-`: step당 `-2`

Penalty token은 기본적으로 감점합니다. 다만 `^Fragile`, `^Drain`, `^Contam`처럼 장비를 벗을 때
주로 발생하는 transient penalty는 현재 평가에서 0점으로 취급합니다.

## 공통 Attribute 기준

Attribute도 먼저 공통 table로 정의하고, 장비군별 evaluator가 multiplier나 override를 적용합니다.
이렇게 하면 같은 token의 기본 가치를 한 곳에서 설명하고, weapon처럼 일부 가치가 낮아지는 장비군만
명시적으로 조정할 수 있습니다.

### 공통 저항/방어 Attribute

- `rF+`, `rC+`, `Will+`, `rCorr`: 첫 step `+10`, 추가 step당 `+15`
- `rN+`: 첫 step `+5`, 추가 step당 `+7.5`
- `rElec`, `rPois`: `+13`
- `AC+`, `EV+`, `SH+`: point당 `+3`

### 공통 주요 Utility

- `Regen+`: `+15`
- 그 밖의 utility는 장비군별 override가 없으면 `+0`

### 공통 낮은 Utility

- `Fly`, `+Blink`, `+Inv`, `Rampage`, `Clar`, `Wildshape`, `Chemistry`, `Acrobat`, `Spirit`: `+0`
- `MP+`: point당 `+1.11`

### 공통 Stat

- `Str+`, `Dex+`, `Int+`: point당 `+1.67`
- `Str-`, `Dex-`, `Int-`: 총 감소량 4까지는 0점, 4를 넘는 초과분만 point당 `-1.67`

Stat 6 point를 주요 저항 1개와 비슷한 가치로 봅니다. Armour에서는 stat 가중치를 weapon 유효
stat의 50%로 낮춥니다.

### 장비군별 조정

- weapon은 저항/방어/utility 계열의 가치를 공통값의 `0.5`배로 낮추거나, weapon 기준에서 무의미한
  token은 0점 처리합니다.
- weapon의 공격 stat은 별도 기준을 사용합니다. `Slay+`는 point당 `+2.5`입니다. `Str+`와
  `Dex+`는 무기별 유효 stat만 point당 `+2.5`로 반영하고, 둘 다 유효한 무기는 더 높은 한쪽만
  반영합니다. `Int+`는 0점입니다. Stat 감소는 공통 stat penalty에서만 처리합니다.
- staff는 caster 관련 token을 override합니다. `Archmagi`, `Wiz`, `RegenMP`, `Int+`, `MP+`,
  spell school 조합은 staff 기준을 사용합니다.
- armour와 jewellery는 공통 저항/방어/stat 기준을 기본으로 사용하고, utility는 명시된 핵심
  attribute만 점수화합니다.

## Weapon 평가 기준

Weapon은 공격 도구로 평가합니다. 무기 자체의 가치는 `enchantment`, `brand`, `Slay`/`Str`/`Dex`,
일부 예외 유틸리티, 명시적 penalty만 반영합니다.

무기에 붙은 저항, `Will+`, `SInv`, `MP+`, `Stlth+`, `Fly` 같은 방어/유틸 옵션은 weapon 자체
가치에서 낮게 봅니다. 기본적으로 공통값의 `0.5`배를 적용합니다.

### Base Weapon

Weapon base item은 `damage * (10 / min_delay)`를 기준 power로 계산합니다. `min_delay`는 현재
DCSS weapon speed에서 추정한 최저 공격 delay입니다.

`DCSS_WEAPON_STATS`의 base damage, hit 보정, speed 값을 기준으로 하며, 최저 공격 delay는
`max(3, speed // 2)`로 계산합니다. 같은 weapon skill 안의 damage 등급은 게임 정보 참고 문서인
`.agents/skills/dcss-item-audit/references/equipment-reference.md`의 무기 표를 참고합니다.

양손 무기는 같은 weapon skill의 한손 종결 weapon power를 기준점으로 삼습니다. 기준점보다 높은
초과분은 절반만 인정하고, shield를 들 수 없는 opportunity cost로 별도 감점을 적용합니다.

```text
weapon_power = damage * (10 / min_delay)
two_handed_power = one_handed_endgame_power + max(0, weapon_power - one_handed_endgame_power) * 0.5 - 3
weapon_base = clamp(round(adjusted_power * 0.6), 6, 16)
```

### Enchantment

- positive enchantment: enchant point당 `+3`
- negative enchantment: enchant point당 `-3`

Enchantment는 중요하지만 `Slay`보다 압도적으로 강하지 않습니다.

### Brand

- `speed`: weapon base score의 `+52%`
- `holy`, `holy wrath`: weapon base score의 `+35%`
- other non-speed brand: weapon base score의 `+25%`
- no brand: `+0`
- unknown brand: `+0`

Normal attack brand는 `elec`, `heavy`, `flame`, `freeze`, `holy`, `vampirism`, `antimagic`,
`spectral`, `drain`, `venom`, `pain` 계열을 포함합니다.

Weak/situational brand는 `chaos`, `protection`, `distortion` 계열을 포함합니다.

### 공격 Attribute

- `Slay+`: point당 `+2.5`
- 유효 `Str+`: point당 `+2.5`
- 유효 `Dex+`: point당 `+2.5`
- `Int+`: `+0`

`Slay+4`는 weapon에서 주요 저항 1개와 같은 가치로 봅니다. `Str+4`와 `Dex+4`도 해당 무기에서
유효한 stat일 때만 주요 저항 1개와 같은 가치로 봅니다. Strength 무기는 `Str`, Dexterity 무기는
`Dex`, flexible 무기는 `Str`/`Dex` 중 더 높은 쪽만 반영합니다.

### Weapon Utility

- weapon의 저항/방어/utility 계열 token은 공통 attribute 기준의 `0.5`배를 적용합니다.
- `Regen+`: `+12`
- `SInv`, `Reflect`, `Wiz`, `RegenMP`: `+9`
- low utility: `+3`
- `MP+`: point당 `+0.5`

### Penalty

Weapon은 공통 penalty 기준을 사용합니다. `Str-`, `Dex-`, `Int-`는 개별 항목에서 즉시 감점하지
않고, 총 stat 감소량이 4를 넘는 초과분만 공통 stat penalty로 감점합니다.

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

Staff는 공통 penalty 기준을 사용합니다. 다만 caster 기능을 막는 penalty는 staff 전용 가중치로
override합니다.

- `*Silence`는 최악의 penalty로 봅니다.
- `-Cast`는 `*Silence` 다음으로 크게 감점합니다.
- `rF-`, `rC-`, `rN-`, `Will-`, `rElec-`, `rPois-`, `rCorr-` 같은 저항 감소는 양수 저항보다
  더 큰 가중치로 감점합니다.
- `Int-`는 다른 stat 감소와 같이 총 stat 감소량 기준으로만 감점합니다.
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

Armour는 방어 장비로 평가합니다. Base item 자체는 고정 가산점만 주고, 저항 보유 여부와 random
attribute가 실제 점수 차이를 만들도록 봅니다.

### Base Armour AC

Armour evaluator는 `base_item`별 기본 방어도 table을 사용해야 합니다. 현재 `constants.py`는
`DCSS_ARMOUR_STATS`와 armour slot mapping을 함께 제공하므로 evaluator가 이 값을 우선 사용합니다.

Body armour의 base item 자체는 `AC`와 `ev_penalty`에서 계산합니다. Base AC 차이는 일반 `AC+`보다
크게 보므로 `AC * 1.75`를 base score의 중심으로 사용합니다. `ev_penalty`는 10으로 나눠 방해 수치
`ER`로 환산하고, `ER >= 14`인 body armour를 heavy armour로 봅니다.

점수는 다음 기준을 사용합니다.

- light body armour: `max(0, round(AC * 1.75 - ER * 0.25))`
- heavy body armour: `max(0, round(AC * 1.75 - max(0, ER - 14) * 0.5))`
- shield: `clamp(round(6 + AC * 0.6 - ER * 0.3), 6, 14)`
- cloak, boots, gloves, helmet: `+8`
- orb/scarf: `+6`
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

- `rF+`, `rC+`, `Will+`, `rCorr`: 첫 step `+10`, 추가 step당 `+15`
- `rN+`: 첫 step `+5`, 추가 step당 `+7.5`
- `rElec`: `+13`
- `rPois`: `+13`
- 저항 2종 이상: 추가 `+8`
- 저항 3종 이상: 추가 `+8`

### Armour에서 중요한 Random Attribute

- `Slay+`는 4 point를 주요 저항 1개와 비슷한 가치로 봅니다.
- `Regen+`은 높은 가치를 가집니다.
- `SInv`, `Rampage`, `+Inv`, `+Blink` 같은 utility는 일단 0점으로 보류합니다.
- `Str+`, `Dex+`, `Int+` 같은 단순 stat은 크게 영향을 주지 않습니다.

점수는 다음 기준을 사용합니다.

- `Regen+`: `+15`
- `Slay+`: point당 `+2.5`
- `Slay-`: point당 `-4`
- `EV+`, `SH+`: point당 `+3`
- `MP+`: point당 `+1.11`
- `Str+`, `Dex+`, `Int+`: point당 `+1.25`
- 그 밖의 utility: `+0`

### Armour Penalty

Armour penalty는 반드시 감점합니다. 저항 감소와 `-Tele`, `*Slow`, `*Silence`, `Harm`, `Bane` 같은
강한 penalty는 장비 자체 가치를 크게 낮춥니다. 저항 감소는 양수 저항보다 더 큰 가중치로
감점합니다. 단순 stat 감소는 총 감소량이 4를 넘을 때만 낮은 가중치로 감점합니다.
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

- `Regen+`: `+15`
- `rF+`, `rC+`, `Will+`, `rCorr`: 첫 step `+10`, 추가 step당 `+15`
- `rElec`, `rPois`: `+13`
- `rN+`: 첫 step `+5`, 추가 step당 `+7.5`
- `Slay+`: point당 `+2.5`
- `AC+`, `EV+`, `SH+`: point당 `+3`

### Stat

`Str+`, `Dex+`, `Int+`는 jewellery에서 의미가 있지만 주요 저항, `Regen+`, `Slay+`, `AC+`보다 낮게
봅니다. Stat 감소는 총 감소량이 4를 넘는 경우에만 감점합니다.

점수는 다음 기준을 사용합니다.

- `Str+`, `Dex+`, `Int+`: point당 `+1.67`
- `Str-`, `Dex-`, `Int-`: 총 감소량 4까지는 0점, 4를 넘는 초과분만 point당 `-1.67`

Stat 6 point를 주요 저항 1개와 비슷한 가치로 봅니다.

### Utility

Jewellery에서는 `SInv`, `Reflect`, `Wiz`, `RegenMP`를 높은 utility로 평가합니다. 나머지 utility는
그보다 낮게 평가합니다.

- amulet의 `Reflect`, `RegenMP`: `+10`
- `Regen+`: `+15`
- `MP+`: point당 `+1.11`
- 그 밖의 utility: `+0`

`Reflect`, `RegenMP`는 주요 저항 1개, `Regen+`은 주요 저항 1.5개 수준으로 봅니다.

### Jewellery Penalty

Penalty는 반드시 감점합니다. `*Slow`, `Bane`, `-Tele`, `*Silence`, `Harm` 같은 강한 penalty는 큰
감점을 적용합니다. 저항 감소는 양수 저항보다 더 큰 가중치로 감점하고, stat 감소는 총 감소량 4를
넘는 초과분만 감점합니다.

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

- weapon/staff/fallback 평가 입력은 `classification.random_attributes`입니다.
- armour/jewellery 평가 입력은 base item 옵션을 포함한 `classification.all_attributes`입니다.
- staff subtype처럼 아이템 자체 가치를 결정하는 metadata는 random attribute가 아니어도 base score로
  반영할 수 있습니다.
- scoring formula 변경 뒤 기존 저장 문서 재평가가 필요하면 대상 `artifact_processing_files`
  record를 제거하거나 상태를 미완료로 되돌려 재처리 대상에 포함시킵니다.
- 등급 label은 frontend 표시와 맞물릴 수 있습니다.
