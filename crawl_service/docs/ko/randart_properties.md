# DCSS Randart 속성

이 문서는 DCSS 랜덤 아티팩트(randart)에 붙을 수 있는 속성을 개발용으로
분류한 것이다. 기준은 DCSS 공식 소스의 `artefact_prop_type` 및
`artp_data`이며, 여기서는 일반 randart 생성 풀에서 랜덤 추가 속성으로
선택될 수 있는 항목을 중심으로 정리한다.

## 범위

포함 대상:

- randart 생성 시 `artp_data`에서 가중치가 0보다 커서 랜덤 선택될 수 있는 속성
- randart 무기에 자동으로 붙는 무기 브랜드
- randart 방어구에 확률적으로 붙을 수 있는 방어구 ego

제외 대상:

- enum에는 있으나 일반 randart 랜덤 생성 가중치가 0인 속성
- 장신구 기본 타입, 방어구/스태프/탈리스만 고유 속성에서만 오는 속성
- 고정 아티팩트, vault fixed props, 구버전 호환용 속성
- randart spellbook의 주문 목록

주의:

- 모든 속성이 모든 아이템에 붙을 수 있는 것은 아니다.
- morgue나 아이템 설명에는 base item, ego, intrinsic 속성이 randart 속성과
  함께 표시될 수 있으므로, randart 추가 속성만 분리하려면 base subtype과
  intrinsic property를 먼저 제거해야 한다.
- 특히 `AC`, `EV`, `SH`는 randart 설명에 실제로 표시될 수 있다. 다만
  현재 일반 randart 생성 풀에서 랜덤 추가 속성으로 뽑히는 항목이 아니라,
  대개 장신구 base subtype이나 intrinsic property에서 온다.

## 양수 또는 혼합 속성군

### Weapon Brand

randart 무기는 항상 브랜드를 가진다.

예시:

- `flaming`
- `freezing`
- `venom`
- `draining`
- `heavy`
- `speed`
- `antimagic`
- `holy wrath`
- `electrocution`
- `pain`
- `vampirism`
- `protection`
- `spectral`
- `reaping`
- `distortion`
- `chaos`
- `penetration` - crossbow 한정

분류값 제안:

- `kind`: `brand`
- `polarity`: `positive` 또는 `mixed`

### Armour Ego

randart 방어구는 확률적으로 ego를 가질 수 있다. scarf, orb 등 일부 장비는
항상 ego가 필요할 수 있다.

ego가 artefact property와 같은 기능을 가지는 경우에는 아래 속성으로
정규화할 수 있다.

- fire resistance -> `rF`
- cold resistance -> `rC`
- poison resistance -> `rPois`
- corrosion resistance -> `rCorr`
- see invisible -> `SInv`
- invisibility -> `+Inv`
- strength -> `Str`
- dexterity -> `Dex`
- intelligence -> `Int`
- flying -> `Fly`
- willpower -> `Will`
- stealth -> `Stlth`
- positive energy -> `rN`
- archmagi -> `Archmagi`
- harm -> `Harm`
- rampaging -> `Rampage`
- ice/fire/air/earth enhancer -> `Ice`, `Fire`, `Air`, `Earth`

분류값 제안:

- `kind`: `ego`
- `normalized_property`: 대응되는 artefact property가 있으면 해당 표기

### 스탯 속성

| 속성 | 의미 | 값 |
| --- | --- | --- |
| `Str` | 힘 보정 | 부호 정수 |
| `Int` | 지능 보정 | 부호 정수 |
| `Dex` | 민첩 보정 | 부호 정수 |

특징:

- 양수와 음수 모두 가능하다.
- randart 생성에서 같은 stat이 중첩 강화될 수 있다.

분류값 제안:

- `kind`: `stat`
- `polarity`: 값이 양수면 `positive`, 음수면 `negative`

### 전투/자원 보정

| 속성 | 의미 | 값 | 비고 |
| --- | --- | --- | --- |
| `Slay` | 처치 보정 | 부호 정수 | 무기와 스태프에는 랜덤 추가 속성으로 붙지 않음 |
| `MP` | 최대 MP 보정 | 부호 정수 | 무기와 스태프에는 랜덤 추가 속성으로 붙지 않음 |

분류값 제안:

- `kind`: `combat` for `Slay`
- `kind`: `resource` for `MP`
- `polarity`: 값이 양수면 `positive`, 음수면 `negative`

## 저항 속성

| 속성 | 의미 | 값 | 음수 값 |
| --- | --- | --- | --- |
| `rF` | 화염 저항 | 부호 정수 | 화염 취약성 |
| `rC` | 냉기 저항 | 부호 정수 | 냉기 취약성 |
| `rElec` | 전기 저항 | 불리언 | 없음 |
| `rPois` | 독 저항 | 불리언 | 없음 |
| `rN` | 네거티브 에너지 저항 | 양의 정수 | 없음 |
| `Will` | willpower | 부호 정수 | willpower 패널티 |
| `rCorr` | 부식 저항 | 불리언 | 없음 |

특징:

- `rF`, `rC`, `Will`은 음수도 가능하다.
- `rN`은 일반 randart 생성에서는 positive side만 가진다.
- `rElec`, `rPois`, `rCorr`은 boolean positive property다.
- `rCorr`와 `*Corrode`는 충돌하므로 함께 붙지 않는다.

분류값 제안:

- `kind`: `resistance`
- `polarity`: 양수/boolean true면 `positive`, 음수면 `negative`

## 유틸리티 속성

| 속성 | 의미 | 값 | 비고 |
| --- | --- | --- | --- |
| `SInv` | see invisible | boolean | positive |
| `+Inv` | evoke invisibility | boolean | non-swappable item 중심 |
| `Fly` | flight | boolean | positive |
| `+Blink` | evoke blink | boolean | `-Tele`과 충돌 |
| `Regen` | HP regeneration | boolean | talisman에는 제한 |
| `Harm` | harm | boolean | non-swappable item 중심 |
| `Rampage` | rampaging | boolean | non-swappable item 중심 |
| `Archmagi` | archmagi spell power bonus | boolean | robe 한정 |

분류값 제안:

- `kind`: `utility`
- `polarity`: 대부분 `positive`, `Harm`은 빌드에 따라 `mixed`로 취급 가능

## 주문 계열 강화 속성

| Property | Spell School |
| --- | --- |
| `Conj` | Conjurations |
| `Hexes` | Hexes |
| `Summ` | Summonings |
| `Necro` | Necromancy |
| `Tloc` | Translocations |
| `Fire` | Fire Magic |
| `Ice` | Ice Magic |
| `Air` | Air Magic |
| `Earth` | Earth Magic |
| `Alch` | Alchemy |
| `Forge` | Forgecraft |

아이템 제한:

- staves
- orbs
- 일부 방어구 슬롯
  - `Earth`: boots, barding
  - `Fire`: gloves
  - `Air`: cloak
  - `Ice`: helmet, hat

충돌:

- `-Cast`가 있는 아이템에는 enhancer를 붙일 수 없다.
- `*Silence`는 enhancer 계열과 충돌한다.

분류값 제안:

- `kind`: `spell_school`
- `polarity`: `positive`

## 페널티 속성

| Property | Meaning | Value | Notes |
| --- | --- | --- | --- |
| `*Noise` | melee attack noise | positive integer | melee weapon 한정 |
| `-Tele` | prevents teleportation | boolean | `+Blink`와 충돌 |
| `*Rage` | chance to berserk on melee attack | positive integer | melee weapon 한정 |
| `^Contam` | magical contamination risk | boolean-like positive | talisman 제한 |
| `*Corrode` | corrosion risk | boolean | `rCorr`와 충돌 |
| `^Drain` | drain risk | boolean | talisman 제한 |
| `*Slow` | slow risk | boolean | negative |
| `^Fragile` | destroyed when unequipped | boolean | armour/talisman/ring에는 랜덤 생성 제한 |
| `*Silence` | silence risk | boolean | enhancer 계열과 충돌 |
| `Bane` | harmful bane property | boolean | weapon/armour 한정 |

분류값 제안:

- `kind`: `penalty`
- `polarity`: `negative`

## 설명에 직접 표시되는 intrinsic 속성

다음 속성은 randart 설명의 brace 안에 표시될 수 있으므로 파서는 인식해야
한다. 그러나 일반 randart의 랜덤 추가 속성으로 분류하면 안 된다.

| Display Property | Typical Origin | Example Base Subtype | Suggested Origin |
| --- | --- | --- | --- |
| `AC` | ring intrinsic | `ring of protection` | `intrinsic` |
| `EV` | ring intrinsic | `ring of evasion` | `intrinsic` |
| `SH` | amulet intrinsic | `amulet of reflection` | `intrinsic` |

예시:

```text
the ring of Gairch {rPois AC+4}
[ring of protection]
```

이 경우 `AC+4`는 randart가 새로 얻은 추가 속성이 아니라 `ring of protection`
기본 타입에서 온 intrinsic이다. randart 추가 속성으로 남길 것은 `rPois`다.

```text
the amulet "Buosiylo" {Reflect Rampage rC++ Regen+ SH+5}
[amulet of reflection]
```

이 경우 `SH+5`와 `Reflect`는 `amulet of reflection`에서 온 intrinsic/base
속성이다. randart 추가 속성 후보로 남길 것은 `Rampage`, `rC++`, `Regen+`다.

파서 처리 권장:

- property tokenizer는 `AC`, `EV`, `SH`, `Reflect`를 인식한다.
- artifact info에 표시된 bracket subtype을 먼저 읽는다.
- subtype이 `ring of protection`이면 `AC`를 `origin: intrinsic`으로 분류한다.
- subtype이 `ring of evasion`이면 `EV`를 `origin: intrinsic`으로 분류한다.
- subtype이 `amulet of reflection`이면 `SH`와 `Reflect`를 `origin: intrinsic`
  또는 `origin: base_subtype`으로 분류한다.
- randart 분석 결과에는 `origin: randart_property`인 속성만 남긴다.

## 랜덤 생성 후보 속성 집합

파서나 스키마에서 "randart 추가 속성 후보"로 사용할 수 있는 최소 집합은
다음과 같다.

```text
Str
Int
Dex
rF
rC
rElec
rPois
rN
Will
SInv
+Inv
Fly
+Blink
*Noise
-Tele
*Rage
^Contam
Slay
Stlth
MP
Regen
rCorr
*Corrode
^Drain
*Slow
^Fragile
Harm
Rampage
Archmagi
Conj
Hexes
Summ
Necro
Tloc
Fire
Ice
Air
Earth
Alch
Forge
*Silence
Bane
```

추가로 별도 처리할 항목:

```text
weapon brand
armour ego
```

## 일반 랜덤 풀에 없는 속성군

다음 속성은 enum 또는 설명 출력에 존재할 수 있으나, 일반 randart의 랜덤
추가 속성 후보로는 취급하지 않는다. 단, `AC`, `EV`, `SH`처럼 실제 아이템
설명에 표시되는 속성은 파서에서 버리지 말고 `origin`을 별도로 기록한다.

```text
AC
EV
HP
SH
Clar
BAcc
BDam
Delay
RMsl
nupgr
rMut
Acrobat
RegenMP
Wiz
```

버전 호환 또는 현재 일반 생성 가중치 0으로 보는 항목:

```text
+Rage
-Cast
*Tele
Hungry
Acc
*Curse
+Fog
SustAt
+Twstr
Tmut
```

참고:

- `AC`, `EV`, `SH`, `Wiz`, `Acrobat`, `RegenMP` 등은 장신구 기본 타입,
  방어구 ego, amulet/ring intrinsic, 고정 아티팩트 등을 통해 보일 수 있다.
- `-Cast`는 부정 속성 생성 함수가 있지만 일반 랜덤 선택 가중치가 0이다.

## 제안 parser 분류

| Category | Properties |
| --- | --- |
| `brand` | weapon brand |
| `ego` | armour ego |
| `stat` | `Str`, `Int`, `Dex` |
| `resistance` | `rF`, `rC`, `rElec`, `rPois`, `rN`, `Will`, `rCorr` |
| `combat` | `Slay` |
| `resource` | `MP` |
| `utility` | `SInv`, `+Inv`, `Fly`, `+Blink`, `Regen`, `Harm`, `Rampage`, `Archmagi` |
| `spell_school` | `Conj`, `Hexes`, `Summ`, `Necro`, `Tloc`, `Fire`, `Ice`, `Air`, `Earth`, `Alch`, `Forge` |
| `penalty` | `*Noise`, `-Tele`, `*Rage`, `^Contam`, `*Corrode`, `^Drain`, `*Slow`, `^Fragile`, `*Silence`, `Bane` |

## 소스 노트

- `crawl-ref/source/artefact-prop-type.h`: artefact property enum
- `crawl-ref/source/artefact.cc`: `artp_data`, randart property generation,
  item compatibility restrictions
- `crawl-ref/source/describe.cc`: property display formatting
