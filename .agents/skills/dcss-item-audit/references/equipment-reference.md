# DCSS 장비 정리

이 문서는 DCSS 장비를 `dcss_arti_gallery`의 artifact 파싱, 분류, 평가, UI 표시 관점에서 정리한
참고 문서입니다. 기준은 현재 저장소의 `arti_parser.constants`, `arti_parser.classifier`,
`frontend` 무기 필터 정책입니다.

## 기본 분류

장비 artifact는 갤러리에서 다음 `item_class`로 분류합니다.

- `weapon`: 근접/원거리 무기
- `armour`: 방어구, 방패, 보조 방어 장비
- `jewellery`: 반지와 목걸이
- `staff`: 마법 지팡이
- `talisman`: 변신 talisman
- `misc`: misc 계열 artifact
- `unknown`: 위 기준으로 분류되지 않은 장비

`item_subtype`은 UI 표시와 필터에 쓰는 세부 이름입니다. 장신구, staff, talisman은 원문 bracket
subtype을 우선 사용하고, armour는 slot 또는 base item을 사용합니다.

## 무기

무기 하위 필터는 DCSS weapon skill 기준으로 나눕니다. 표의 `Damage`, `명중`, `기본 공속`은
`DCSS_WEAPON_STATS`의 base damage, hit 보정, speed 값입니다. `최소 공속`은 evaluator 기준인
`max(3, speed // 2)`로 계산합니다. 등급은 같은 weapon skill 안에서 damage를 기준으로 나눈 상대 등급입니다.

### Short Blades

| 무기 | Damage | 명중 | 기본 공속 | 최소 공속 | Damage 등급 |
| --- | ---: | ---: | ---: | ---: | --- |
| `dagger` | 4 | +6 | 10 | 5 | 하위 |
| `quick blade` | 4 | +6 | 15 | 7 | 하위 |
| `short sword` | 5 | +4 | 10 | 5 | 중위 |
| `athame` | 6 | +5 | 13 | 6 | 상위 |
| `rapier` | 7 | +4 | 12 | 6 | 최상위 |

`quick blade`는 damage 자체는 낮지만 매우 빠른 무기입니다. Damage 등급만 보면 하위이고, 실제 평가는
속도와 brand 효율을 함께 봐야 합니다.

### Long Blades

| 무기 | Damage | 명중 | 기본 공속 | 최소 공속 | Damage 등급 |
| --- | ---: | ---: | ---: | ---: | --- |
| `falchion` | 8 | +2 | 13 | 6 | 하위 |
| `long sword` | 10 | +1 | 14 | 7 | 중위 |
| `scimitar` | 12 | 0 | 14 | 7 | 중위 |
| `demon blade` | 13 | -1 | 13 | 6 | 상위 |
| `eudemon blade` | 14 | -2 | 12 | 6 | 상위 |
| `double sword` | 15 | -1 | 15 | 7 | 상위 |
| `great sword` | 17 | -3 | 17 | 8 | 최상위 |
| `triple sword` | 19 | -4 | 18 | 9 | 최상위 |

### Axes

| 무기 | Damage | 명중 | 기본 공속 | 최소 공속 | Damage 등급 |
| --- | ---: | ---: | ---: | ---: | --- |
| `hand axe` | 7 | +3 | 13 | 6 | 하위 |
| `war axe` | 11 | 0 | 15 | 7 | 중위 |
| `broad axe` | 13 | -2 | 16 | 8 | 상위 |
| `battleaxe` | 15 | -4 | 17 | 8 | 상위 |
| `executioner's axe` | 18 | -6 | 19 | 9 | 최상위 |

### Maces & Flails

| 무기 | Damage | 명중 | 기본 공속 | 최소 공속 | Damage 등급 |
| --- | ---: | ---: | ---: | ---: | --- |
| `club` | 5 | +3 | 13 | 6 | 하위 |
| `whip` | 6 | +2 | 11 | 5 | 하위 |
| `mace` | 8 | +3 | 14 | 7 | 중위 |
| `flail` | 10 | 0 | 14 | 7 | 중위 |
| `demon whip` | 11 | +1 | 11 | 5 | 중위 |
| `sacred scourge` | 12 | 0 | 11 | 5 | 중위 |
| `dire flail` | 13 | -3 | 13 | 6 | 상위 |
| `morningstar` | 13 | -2 | 15 | 7 | 상위 |
| `eveningstar` | 15 | -1 | 15 | 7 | 상위 |
| `great mace` | 17 | -4 | 17 | 8 | 상위 |
| `giant club` | 20 | -6 | 16 | 8 | 최상위 |
| `giant spiked club` | 22 | -7 | 18 | 9 | 최상위 |

`giant club`과 `giant spiked club`은 `maces & flails` 계열의 대형 고데미지 무기입니다.

### Polearms

| 무기 | Damage | 명중 | 기본 공속 | 최소 공속 | Damage 등급 |
| --- | ---: | ---: | ---: | ---: | --- |
| `spear` | 6 | +4 | 11 | 5 | 하위 |
| `trident` | 9 | +1 | 13 | 6 | 중위 |
| `demon trident` | 12 | +1 | 13 | 6 | 중위 |
| `halberd` | 13 | -3 | 15 | 7 | 상위 |
| `trishula` | 13 | 0 | 13 | 6 | 상위 |
| `partisan` | 14 | +1 | 17 | 8 | 상위 |
| `glaive` | 15 | -3 | 17 | 8 | 상위 |
| `bardiche` | 18 | -6 | 19 | 9 | 최상위 |

### Staves

| 무기 | Damage | 명중 | 기본 공속 | 최소 공속 | Damage 등급 |
| --- | ---: | ---: | ---: | ---: | --- |
| `staff` | 5 | +5 | 12 | 6 | 하위 |
| `quarterstaff` | 10 | +3 | 13 | 6 | 중위 |
| `lajatang` | 16 | -3 | 14 | 7 | 최상위 |

### Ranged Weapons

| 무기 | Damage | 명중 | 기본 공속 | 최소 공속 | Damage 등급 |
| --- | ---: | ---: | ---: | ---: | --- |
| `sling` | 7 | 0 | 14 | 7 | 하위 |
| `shortbow` | 8 | +2 | 14 | 7 | 하위 |
| `orcbow` | 11 | -3 | 15 | 7 | 중위 |
| `longbow` | 14 | 0 | 17 | 8 | 상위 |
| `arbalest` | 16 | -2 | 19 | 9 | 상위 |
| `hand cannon` | 16 | +3 | 19 | 9 | 상위 |
| `triple crossbow` | 23 | -2 | 23 | 11 | 최상위 |

## Weapon Brand

무기 brand는 property token 또는 이름의 `of <brand>` 꼴에서 추론합니다. Brand는
`all_attributes`에는 들어갈 수 있지만, base intrinsic 속성과는 별개입니다.

현행 DCSS의 `scroll of brand weapon`은 비-artefact 무기에만 사용할 수 있으며, artefact의 고정
brand나 unrand 전용 효과를 새로 부여하지 않습니다. Scroll 재브랜딩 pool은 근접/원거리 여부와 무기
skill별 특수 brand에 따라 달라집니다.

### Scroll로 부여 가능한 Brand

| Brand | 대상 | 비고 |
| --- | --- | --- |
| `flaming` | 근접, 원거리 | 화염 추가 피해 |
| `freezing` | 근접, 원거리 | 냉기 추가 피해 |
| `heavy` | 근접, 원거리 | 높은 피해와 느린 공격 |
| `draining` | 근접, 원거리 | 음에너지 계열 debuff |
| `electrocution` | 근접, 원거리 | 확률적 전기 추가 피해 |
| `chaos` | 근접, 원거리 | 무작위 효과, 평가상 불안정 brand |
| `venom` | 근접 | 독 부여 |
| `protection` | 근접 | 공격 시 방어 보조 |
| `spectral` | 근접 | spectral weapon 생성 |
| `vampirism` | 근접 | 생명력 흡수 |
| skill 특수 brand | 근접 | `devious`, `valour`, `concussion`, `sundering`, `entangling`, `rebuke` 등 버전별 특수 brand |

### Scroll로 직접 부여되지 않는 주요 Brand

| Brand | 주된 출처/성격 | 처리 기준 |
| --- | --- | --- |
| `speed` | 자연 생성, randart, 버전별 ego table | scroll pool에는 없음 |
| `holy wrath` | TSO blessing, holy weapon, 일부 생성/artefact | 일반 scroll brand로 보지 않음 |
| `pain` | Kiku 계열 gift/무기, 일부 생성/artefact | 일반 scroll brand로 보지 않음 |
| `antimagic` | Trog gift, 일부 생성/artefact | 일반 scroll brand로 보지 않음 |
| `distortion` | Lugonu 계열, Abyss/특수 생성, 일부 artefact | 일반 scroll brand로 보지 않음 |
| `vorpal` | 구버전 brand | 현행 데이터에서는 legacy token으로 취급 |
| `reaping`, `penetration`, `sunder`, `shock`, `anguish`, `deathbane` | 버전/변종/특수 artifact 계열 | 파서는 token을 보존하되 일반 scroll brand로 분류하지 않음 |

### 파서 Alias

파서는 morgue 표기 차이를 흡수하기 위해 다음 alias도 brand로 인식합니다.

- `flame` -> `flaming`
- `freeze` -> `freezing`
- `drain` -> `draining`
- `elec` -> `electrocution`
- `holy` -> `holy wrath`
- `protect` -> `protection`

UI나 평가 로직에서 brand를 표시할 때는 원문 token을 보존하되, 같은 의미의 alias는 canonical brand로
묶어서 집계하는 것이 안전합니다.

## 방어구

방어구는 `armour_slot` 기준으로 UI 필터와 평가 보조 정보를 만듭니다.

### Body Armour

Body armour는 기본적으로 방해도 기준으로 경갑과 중갑을 나눕니다. 저장소 기준 `ER`은
`abs(ev_penalty) / 10`으로 환산하며, evaluator는 `ER >= 14`인 body armour를 중갑으로 봅니다.

#### 경갑

| 방어구 | AC | ER | 기본 속성 | 비고 |
| --- | ---: | ---: | --- | --- |
| `robe` | 2 | 0 | - | 주문/회피 친화 |
| `animal skin` | 2 | 0 | - | 초경량 body armour |
| `steam dragon scales` | 5 | 0 | `rSteam` | 방해도 없는 dragon scales |
| `leather armour` | 3 | 4 | - | 낮은 방해도 |
| `troll leather armour` | 3 | 4 | `Regen+` | 구버전 `troll skin` 포함 |
| `acid dragon scales` | 6 | 5 | `rCorr` | 낮은 방해도와 부식 저항 |
| `ring mail` | 5 | 7 | - | 경갑과 중갑 사이의 저방해 armour |
| `quicksilver dragon scales` | 9 | 7 | `Will+` | 높은 AC 대비 낮은 방해도 |
| `swamp dragon scales` | 7 | 7 | `rPois` | 독 저항 |
| `fire dragon scales` | 8 | 9 | `rF++`, `rC-` | 화염 특화, 냉기 페널티 |
| `scale mail` | 6 | 10 | - | 중간 방해도 |
| `ice dragon scales` | 9 | 11 | `rC++`, `rF-` | 냉기 특화, 화염 페널티 |
| `pearl dragon scales` | 10 | 11 | `rN+` | 높은 AC의 경갑 쪽 dragon scales |

#### 중갑

| 방어구 | AC | ER | 기본 속성 | 비고 |
| --- | ---: | ---: | --- | --- |
| `chain mail` | 8 | 14 | - | evaluator의 중갑 시작점 |
| `shadow dragon scales` | 11 | 15 | `Stlth+` | 은밀 보정이 있는 중갑 |
| `storm dragon scales` | 10 | 15 | `rElec` | 전기 저항 |
| `plate armour` | 10 | 18 | - | 표준 고방어 중갑 |
| `crystal plate armour` | 14 | 23 | - | 최고 AC, 매우 높은 방해도 |
| `gold dragon scales`, `golden dragon scales` | 12 | 23 | `rF+`, `rC+`, `rPois` | 다중 저항, 매우 높은 방해도 |

### Shields and Offhand

Offhand 장비는 body armour와 달리 방어구 방해도 기준의 경갑/중갑으로 나누지 않습니다. 대신 한 손을
점유하는 장비로 보고, 방패는 `AC`와 `ER`를 함께 표시합니다.

| 방어구 | AC | ER | 분류 | 비고 |
| --- | ---: | ---: | --- | --- |
| `buckler` | 3 | 5 | shield | 가장 작은 방패 |
| `kite shield` | 8 | 10 | shield | 표준 방패 |
| `tower shield` | 13 | 15 | shield | 가장 큰 방패, 높은 방해도 |
| `orb` | 0 | 0 | orb | 방패가 아니며 orb ego/artefact 효과가 핵심 |

`orb`는 DCSS 상수상 offhand 계열이지만 갤러리 문서와 UI에서는 별도 armour slot으로 다룰 수 있습니다.
`shield`는 구버전/표기 호환 이름으로 `kite shield`와 같은 계열로 취급합니다.

### Helmet

머리 슬롯은 방해도가 없고, base item의 AC와 착용 가능 크기 차이가 주된 구분점입니다.

| 방어구 | AC | ER | 비고 |
| --- | ---: | ---: | --- |
| `cap` | 0 | 0 | 작은 머리 방어구, 기본 AC 없음 |
| `hat` | 0 | 0 | 초소형 종족까지 가능한 유연한 머리 방어구 |
| `helmet` | 1 | 0 | 기본 AC가 있는 표준 머리 방어구 |

### Boots

발/하체 슬롯은 일반 `boots`와 종족 전용 `barding` 계열을 분리해서 봅니다.

| 방어구 | AC | ER | 분류 | 비고 |
| --- | ---: | ---: | --- | --- |
| `boots` | 1 | 0 | boots | 일반 발 방어구 |
| `barding` | 4 | 6 | barding | 나가/팔렌토가 계열 하체 방어구 |
| `centaur barding` | 4 | 6 | barding | 구버전/종족 표기 호환 |

### Gloves

손 슬롯은 현재 기본적으로 `gloves`만 다룹니다.

| 방어구 | AC | ER | 비고 |
| --- | ---: | ---: | --- |
| `gloves` | 1 | 0 | 일반 손 방어구 |

### Cloak

Cloak 슬롯은 일반 AC 장비와 AC가 없는 특수 ego 기반 장비로 갈립니다.

| 방어구 | AC | ER | 비고 |
| --- | ---: | ---: | --- |
| `cloak` | 1 | 0 | 기본 AC가 있는 등 방어구 |
| `scarf` | 0 | 0 | AC 대신 scarf ego/artefact 속성이 핵심 |

## 방어구 원본 속성

일부 base armour는 원래 intrinsic 속성을 갖습니다. 이 속성은 `base_attributes`로 분리하고, 평가에서
랜덤 속성과 혼동하지 않아야 합니다.

- `acid dragon scales`: `rCorr`
- `fire dragon scales`: `rF++`, `rC-`
- `gold dragon scales`, `golden dragon scales`: `rF+`, `rC+`, `rPois`
- `ice dragon scales`: `rC++`, `rF-`
- `pearl dragon scales`: `rN+`
- `quicksilver dragon scales`: `Will+`
- `shadow dragon scales`: `Stlth+`
- `steam dragon scales`: `rSteam`
- `storm dragon scales`: `rElec`
- `swamp dragon scales`: `rPois`
- `troll leather armour`, `troll skin`: `Regen+`

## 장신구

장신구는 `jewellery_slot`으로 `ring` 또는 `amulet`을 가집니다. UI의 하위 필터도 세부 subtype이 아니라
`ring`/`amulet`으로 단순화합니다.

장신구 artifact는 원본 subtype이 중요합니다. 예를 들어 `ring of protection from fire` 기반 artifact는
상세 설명에 `[ring of protection from fire]`처럼 원본 형태를 표시합니다.

### Ring 원본 속성

- `ring of dexterity`: `Dex`
- `ring of evasion`: `EV`
- `ring of intelligence`: `Int`
- `ring of magical power`: `MP`
- `ring of poison resistance`: `rPois`
- `ring of protection`: `AC`
- `ring of protection from cold`: `rC`
- `ring of protection from fire`: `rF`
- `ring of resist corrosion`: `rCorr`
- `ring of see invisible`: `SInv`
- `ring of strength`: `Str`
- `ring of willpower`: `Will`
- `ring of wizardry`: `Wiz`

### Amulet 원본 속성

- `amulet of dissipation`: `Dissipate`
- `amulet of faith`: `Faith`
- `amulet of guardian spirit`: `Spirit`
- `amulet of magic regeneration`: `RegenMP`
- `amulet of reflection`: `Reflect`, `SH`
- `amulet of regeneration`: `Regen`
- `amulet of the acrobat`: `Acrobat`

## Staff

Staff는 일반 weapon이 아니라 caster weapon으로 분류합니다. Staff subtype 자체는 마법 school과 원본
속성을 줄 수 있습니다.

- `staff of air`: `Air`, `rElec`
- `staff of alchemy`: `Alch`, `rPois`
- `staff of cold`: `Ice`, `rC`
- `staff of conjuration`: `Conj`
- `staff of death`: `Necro`, `rN`
- `staff of earth`: `Earth`
- `staff of fire`: `Fire`, `rF`
- `staff of poison`: `Alch`, `rPois`

## Ashenzari Curse

Ashenzari가 저주한 장비는 morgue에서 일반 artifact와 비슷하게 보일 수 있지만, 아이템 고유 속성과
Ashenzari가 임시로 부여한 skill boost를 분리해야 합니다.

### 아이템 변화

Ashenzari curse가 걸린 장비는 다음처럼 표시/동작합니다.

| 변화 | 설명 | 파서 처리 |
| --- | --- | --- |
| `cursed` prefix | 이름 앞에 `cursed`가 붙을 수 있음 | randart 정체성이 아니라 item status로 보고 표시 이름에서는 제거 |
| 장착 해제 제한 | curse가 유지되는 동안 장비를 자유롭게 해제할 수 없음 | artifact 속성으로 저장하지 않음 |
| artefact화 | 원래 non-artefact 장비도 curse 후 artefact처럼 이름과 property block을 가질 수 있음 | randart 후보로 파싱하되 Ash curse group token은 분리 |
| curse group token 추가 | `{rF+ Int+4, Cun, Self}`처럼 property block에 group 약어가 속성처럼 추가됨 | `ignored_attributes`에만 보존하고 `all_attributes`/평가/UI token에서는 제외 |

예를 들어 Ashenzari가 저주한 randart는 이름과 일반 artefact property block을 가질 수 있지만,
개별 skill 이름은 `{Fighting+3 Long Blades+2}` 같은 property block token으로 추가되지 않습니다.
실제 morgue에서는 `{..., Self, Comp}`, `{..., Elem, Fort}`처럼 curse group 약어가 property block에
추가되고, 아이템 설명문에서 해당 group이 올리는 skill 목록을 풉니다.

### Curse Group과 Skill Boost

Ashenzari는 탐험 중 장비에 걸 curse를 제안합니다. Curse는 장비를 벗을 수 없게 만들고, piety에 비례해
정해진 skill group에 보너스를 줍니다. 실제 morgue의 아이템 줄에서는 상승 skill 이름이 아니라
다음 group 약어가 property block token으로 나타납니다.

| Property token | Curse group | 설명문에서 풀리는 skill |
| --- | --- | --- |
| `Melee` | `Melee Combat` | `Short Blades`, `Long Blades`, `Axes`, `Maces & Flails`, `Polearms`, `Staves`, `Unarmed Combat` |
| `Range` | `Ranged Combat` | 현행: `Ranged Weapons`, `Throwing`; 구버전: `Slings`, `Bows`, `Crossbows`, `Throwing` |
| `Elem` | `Elements` | `Fire Magic`, `Ice Magic`, `Air Magic`, `Earth Magic` |
| `Sorc` | `Sorcery` | 현행: `Conjurations`, `Alchemy`; 구버전은 poison/transmutation 계열 변동 가능 |
| `Comp` | `Companions` | 현행: `Summonings`, `Necromancy`, `Forgecraft`; 구버전: `Summonings`, `Necromancy` |
| `Bglg` | `Beguiling` | 현행: `Hexes`, `Translocations`; 구버전: `Conjurations`, `Hexes`, `Translocations` |
| `Self` | `Introspection` | `Fighting`, `Spellcasting` |
| `Fort` | `Fortitude` | `Armour`, `Shields` |
| `Cun` | `Cunning` | `Dodging`, `Stealth` |
| `Dev` | `Devices` | 현행: `Evocations`, `Shapeshifting` |
| `Evo` | `Evocations` | 구버전: `Evocations` |

DCSS 소스 기준으로 curse가 부여하는 group과 skill은 `god-abil.cc`의 `_ashenzari_curses`에서 정해집니다.
아이템 설명 문자열은 `describe.cc`의 `_describe_item_curse()`가 만들며, group 안의 skill 이름은
`skills.cc`의 `skill_name()` 결과를 그대로 사용합니다.

| 표기 범주 | 실제 morgue 문자열 |
| --- | --- |
| item property block | `{rCorr Int+4, Cun, Self}`, `{^Contam Int+6, Self, Comp}`, `{rF+++ rC+ Int-2 Forge Fire, Bglg, Comp}` |
| curse 설명 문장 | `It has a curse which improves the following skills:` |
| group/skill 목록 | `<Curse name>: <skill_name>, <skill_name>` |
| skill 이름 | 설명문에만 등장하며 artifact property token으로 저장하지 않음 |

### 실제 아이템 문자열

Ashenzari skill boost는 item property block 안에 `<skill><signed integer>` 형태로 추가되지 않습니다.
대신 property block에는 curse group 약어가 일반 속성처럼 섞여 들어가고, 설명문에는 group별 skill 목록이
별도로 붙습니다.

예:

```text
h - the cursed scarf of Supernal Understanding (worn) {repulsion, rC+, Sorc, Dev}
It has a curse which improves the following skills:
Sorcery: Conjurations and Alchemy.
Devices: Evocations and Shapeshifting.

q - the cursed +0 pair of boots of Ashenzari's Affliction (worn) {Self, Melee}
It has a curse which improves the following skills:
Introspection: Fighting and Spellcasting.
Melee Combat: Short Blades, Long Blades, Axes, Maces & Flails, Polearms,
Staves and Unarmed Combat.
```

파서는 property block의 다음 token들을 Ashenzari curse group metadata로 식별합니다.

| Token | 처리 |
| --- | --- |
| `Self`, `Melee`, `Range`, `Elem`, `Sorc`, `Comp`, `Bglg`, `Fort`, `Cun`, `Dev` | 현행/최근 morgue의 Ashenzari group token. `ignored_attributes`에 보존하고 표시/평가 속성에서 제외 |
| `Evo` | 구버전 morgue의 Evocations group token. `ignored_attributes`에 보존하고 표시/평가 속성에서 제외 |

따라서 `{Fighting+3}`, `{Air Magic+2}`, `{Maces & Flails+4}` 같은 signed skill token은 확인한 실제
morgue에서 Ashenzari가 item property block에 추가하는 문자열이 아닙니다. 실제 속성으로 처리해야 하는
문자열은 `{..., Self, Comp}` 같은 curse group 약어입니다. 설명문에 나오는 `Fighting`, `Spellcasting`,
`Maces & Flails` 같은 skill 이름은 group token의 의미를 설명하는 텍스트이며 artifact attribute로
추출하지 않습니다.

### 표시와 평가 기준

- `cursed`/`chaotic` prefix는 item status로 보고 artifact 이름, base item 추론, token 표시에서 제거합니다.
- Ashenzari skill boost는 아이템 자체의 고유 속성이 아니므로 `all_attributes`, `random_attributes`,
  token-row, UI 필터, 점수 평가에 포함하지 않습니다.
- 원문 추적과 디버깅을 위해 property block의 curse group token은 `ignored_attributes`에 보존합니다.
- curse 설명 문장은 group token 매핑 검증 근거로 사용할 수 있지만, 설명문 안의 skill 이름을 별도
  artifact attribute로 추출하지 않습니다.
- curse로 artefact처럼 보이는 non-randart 또는 고정 artifact는 별도 예외 규칙을 적용합니다. 고정 artifact는
  curse 여부와 무관하게 일반 randart 갤러리 대상에서 제외하는 것이 안전합니다.

## 속성 분리 정책

- `all_attributes`: visible token, weapon brand, base intrinsic attribute를 합친 표시 대상 전체 속성
- `base_attributes`: base item 또는 base subtype이 원래 가지는 intrinsic 속성
- `random_attributes`: 평가에 들어가는 실제 랜덤 속성
- `ignored_attributes`: 원문 근거는 보존하지만 표시/평가하지 않는 속성

`random_attributes`는 평가 입력입니다. 원본 속성이 `random_attributes`에 섞이면 원본 아이템 자체가
과평가될 수 있습니다.

## 제외와 예외

- 고정 아티팩트는 저장 대상에서 제외합니다.
- `cursed` randart는 저장하되 표시 이름에서 `cursed` 접두사를 제거합니다.
- Ashenzari skill boost는 artifact 고유 속성으로 보지 않고 `ignored_attributes`에만 보존합니다.
- DCSS `0.29` 이상 정식 release/trunk만 처리합니다.
- 변종 version suffix가 보이면 저장하지 않습니다.

## UI 표시 정책

- 카드의 `token-row`는 `allAttributes` 전체를 한 줄 압축/ellipsis로 표시합니다.
- 장신구 상세 설명은 첫 줄에 원본 subtype을 bracket 형태로 표시합니다.
- 상세 팝업 하단에는 최초 발견 source 기준의 version과 datetime을 표시합니다.
