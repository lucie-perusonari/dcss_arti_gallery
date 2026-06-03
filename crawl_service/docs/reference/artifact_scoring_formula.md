# DCSS Randart 명품 점수 공식 초안

이 문서는 DCSS 랜덤 아티팩트(randart)를 “명품” 관점에서 평가하기 위한
점수 공식을 정의한다.

## 참고한 판단 문화

디시인사이드 로그라이크 갤러리의 `돌품명품` 글들은 보통 아이템 스크린샷을
올리고 추천/댓글로 “이게 명품인가”를 판정하는 형식이다. 특히 2019년
`돌품명품대회` 공지성 글은 무기/방어구/장신구별 배점과 보너스 조건을 둔다.

확인한 예시는 다음과 같다.

- `돌품명품) 체이신도 돌품명품 출품합니다.`: 조회, 추천, 댓글이 붙은 출품형 글
- `ㄷㅈ) 돌품명품`: 높은 추천을 받은 단일 아이템 스크린샷 글
- `돌품명품 가능?`: “가능?”이라는 제목으로 아이템의 명품성을 묻는 글
- `돌품명품 심플이즈베스트`: 복잡한 옵션보다 깔끔한 강점을 강조하는 제목

따라서 명품 점수는 단순 전투력만 보지 않는다. 실제로 쓸 만한가, 특정 빌드에
딱 맞는가, 페널티가 거슬리지 않는가, 보기만 해도 자랑할 만한가를 같이 본다.

디시 대회식 배점에서 참고할 핵심은 다음이다.

- 무기/방어구는 강화 수치, base type, brand/ego를 별도 축으로 본다.
- 보조 방어구와 장신구는 slot 가치가 높아 가점을 받는다.
- 추천수와 댓글수도 점수화되어 “성능 + 커뮤니티 반응”을 함께 본다.
- 특이한 조합, 저주 옵션, 감정 결과, 스크린샷 품질 같은 보너스 항목이 있다.

영어권 커뮤니티의 유사 표현과 Reddit `r/dcss`의 좋은 randart 사례는
[`reddit_randart_language.md`](../research/randart-corpus/reddit_randart_language.md)에 따로 정리했다.

## 총점

```text
luxury_score = round(
    base_fit
  + power
  + synergy
  + purity
  + flex
  + timing
)
```

총점 범위는 `0..100`으로 clamp한다.

| 항목 | 배점 | 의미 |
| --- | ---: | --- |
| `base_fit` | 20 | 아이템 베이스/슬롯 자체가 좋은가 |
| `power` | 30 | 옵션의 순수 성능 합 |
| `synergy` | 20 | 빌드와 속성이 얼마나 맞물리는가 |
| `purity` | 15 | 페널티와 잡옵이 적고 깔끔한가 |
| `flex` | 10 | 보기 드문 고점/자랑거리/밈성이 있는가 |
| `timing` | 5 | 그 시점에 먹으면 게임을 바꾸는가 |

## 등급

| 점수 | 등급 | 판정 |
| ---: | --- | --- |
| `90..100` | `돌품명품` | 올려도 반응 나올 만한 명품 |
| `80..89` | `명품` | 대부분의 상황에서 강한 고급품 |
| `65..79` | `실전템` | 잘 쓰면 좋지만 자랑감은 약함 |
| `45..64` | `애매템` | 빌드나 상황을 많이 탐 |
| `0..44` | `돌품` | 페널티/안티시너지/낮은 베이스가 큼 |

`grade`는 실전성 등급이다. 커뮤니티식 명품 판정은 `random_attributes` 기반
희소도 점수인 `rarity_score`와 결합한 `luxury_grade`를 별도로 쓴다. 기본
아이템 intrinsic, ring subtype 효과, staff/talisman 기본 효과, armour base에서
온 속성은 희소도 점수에 넣지 않는다. 단, 무기/방어구의 높은 강화 수치는
명품성을 만드는 핵심 신호이므로 `rarity_score`에도 반영한다.

## 희소도 점수

`rarity_score`는 randart 생성으로 붙은 옵션 압축이 얼마나 보기 드문지를 본다.
현재 기준은 `crawl_service/docs/research/randart-corpus/rarity_report.md`의 시뮬레이션 결과를 따른다.

| 신호 | 점수 |
| --- | ---: |
| `Slay+6` 이상 | 45 |
| `Slay+4` 이상 | 25 |
| 장신구/보조 방어구에서 `Slay+3` 이상 | 15 |
| 저항/Will 계열 4종 이상 | 30 |
| 저항/Will 계열 3종 이상 | 20 |
| 장신구에서 `Slay + stat + 저항/Will` 압축 | 15 |
| 무기 `+9` 이상 | 30 |
| 무기 `+7..+8` | 20 |
| 무기 `+5..+6` | 10 |
| 보조 방어구 `+4` 이상 | 25 |
| 보조 방어구 `+2..+3` | 10 |
| body armour/shield `+15` 이상 | 45 |
| body armour/shield `+10..+14` | 35 |
| body armour/shield `+7..+9` | 25 |
| body armour/shield `+5..+6` | 10 |
| 위 희소 신호가 있고 페널티가 없음 | 5 |
| 페널티 있음 | `-10..-25` |

`luxury_grade`는 다음 기준으로 정한다.

| 조건 | 등급 |
| --- | --- |
| `practical_score >= 80` and `rarity_score >= 60` | `전설급` |
| `rarity_score >= 45` and `practical_score >= 55` | `돌품명품 후보` |
| `practical_score >= 65` and `rarity_score >= 30` | `명품` |
| `practical_score >= 65` | `실전템` |
| `rarity_score >= 30` | `희귀 잡템` |
| `practical_score >= 45` | `애매템` |
| otherwise | `돌품` |

## 1. Base Fit: 0..20

베이스 자체가 좋은지 본다. 같은 옵션이어도 `broad axe`, `eveningstar`,
`gold dragon scales`, `cloak`, `boots`, `ring`, `amulet`처럼 원래 좋은 베이스가
더 높은 점수를 받는다.

```text
base_fit = slot_value + base_item_value + enchant_value + ego_or_brand_value
```

### 공통 슬롯값

| 슬롯 | 점수 |
| --- | ---: |
| amulet | 7 |
| ring | 6 |
| cloak/boots/gloves/helmet | 6 |
| body armour/shield | 5 |
| weapon | 5 |
| staff/talisman | 4 |

### 베이스 아이템값

| 구분 | 점수 |
| --- | ---: |
| 최상급 베이스 | 6 |
| 좋은 베이스 | 4 |
| 평범한 베이스 | 2 |
| 나쁜 베이스 | 0 |

예:

- 최상급 무기: `broad axe`, `eveningstar`, `demon whip`, `triple sword`, `hand cannon`
- 좋은 방어구: `cloak`, `boots`, `gloves`, `helmet`, `kite shield`, 고급 dragon armour
- 좋은 장신구: 기본 intrinsic이 이미 쓸 만한 ring/amulet

### 강화/브랜드/ego

| 조건 | 점수 |
| --- | ---: |
| 무기/방어구 강화가 상한에 가까움 | `0..5` |
| 좋은 무기 브랜드: speed, heavy, electrocution, freezing, flaming, holy 등 | `0..4` |
| 좋은 방어구 ego: resistance, willpower, stealth, flying, archmagi 등 | `0..4` |

`base_fit`은 최종 `20`으로 clamp한다.

## 2. Power: 0..30

옵션의 순수 성능이다. 기본 intrinsic을 제외한 `random_attributes`를 우선 평가한다.

```text
power = min(30, offense + defense + utility)
```

### 공격 점수

| 속성 | 점수 |
| --- | ---: |
| `Slay+n` | `4 * n`, 최대 16 |
| `Str+n` melee/ranged 빌드 | `1.5 * n`, 최대 9 |
| `Dex+n` short blade/ranged/EV 빌드 | `1.5 * n`, 최대 9 |
| `Int+n` caster 빌드 | `1.5 * n`, 최대 9 |
| 좋은 무기 브랜드 | `4..10` |
| spell school 보너스가 주력 주문과 맞음 | `3..8` |

### 방어 점수

| 속성 | 점수 |
| --- | ---: |
| `AC+n` | `2 * n`, 최대 12 |
| `EV+n` | `2 * n`, 최대 12 |
| `SH+n` | `1.5 * n`, 최대 9 |
| `Will+` | 5 |
| `Will++` 이상 | 9 |
| `rF+`, `rC+` | 각 4 |
| `rF++`, `rC++` | 각 7 |
| `rElec` | 6 |
| `rPois` | 4 |
| `rCorr` | 3 |
| `rN+` | 2 |
| `rN++` | 4 |
| `rN+++` | 6 |

### 유틸 점수

| 속성 | 점수 |
| --- | ---: |
| `SInv` | 3 |
| `Fly` | 2 |
| `Regen+` | 5 |
| `RegenMP+` | 5 |
| `Rampage` | 5 |
| `Reflect` | 6 |
| `Wiz` | 5 |
| `MP+n` | `n`, 최대 8 |
| `Stlth+` | 2 |
| `Stlth++` 이상 | 4 |

## 3. Synergy: 0..20

명품성의 핵심이다. “강한 옵션”보다 “내 캐릭터가 지금 원하는 옵션”이 더 중요하다.

```text
synergy = archetype_match + hole_cover + stack_quality + anti_synergy_guard
```

| 항목 | 점수 |
| --- | ---: |
| 주력 빌드와 핵심 옵션이 맞음 | `0..8` |
| 현재 부족한 저항/Will/방어를 정확히 메움 | `0..6` |
| 같은 방향의 옵션이 예쁘게 중첩됨 | `0..4` |
| 안티시너지가 없음 | `0..2` |

예:

- 중갑 melee에게 `Slay`, `rF`, `rC`, `Will`, `AC`, `Reflect`는 높은 synergy.
- 딥엘 법사에게 `Int`, `Wiz`, `RegenMP`, spell school은 높은 synergy.
- 은신 암살자에게 `Dex`, `Stlth`, `SInv`, `Will`은 높은 synergy.
- `Int+8` plate armour는 power는 높아도 build context가 없으면 synergy가 낮다.

빌드 정보가 없으면 `synergy` 기본값은 `8`로 둔다. 즉 아이템 단독 평가에서는
과하게 빌드 특화 점수를 주지 않는다.

## 4. Purity: 0..15

“심플이즈베스트” 계열의 명품성을 반영한다. 좋은 옵션이 많아도 치명적 페널티가
있으면 명품성이 꺾인다.

```text
purity = clamp(15 - penalty_points - junk_points, 0, 15)
```

### 페널티

| 속성 | 감점 |
| --- | ---: |
| `*Slow` | 8 |
| `^Drain` | 7 |
| `Fragile` | 10 |
| `-Tele` | 6 |
| `-Cast` | 8 |
| `Will-` | 6 |
| `rF-`, `rC-` | 각 6 |
| `rPois-`, `rElec-` | 각 5 |
| `Str-n`, `Dex-n`, `Int-n` | `n`, 최대 8 |
| `Stlth-` | 2 |

### 잡옵

빌드와 상관없는 주문 계열, 이미 충분한 저항의 과잉 중첩, 의미 없는 스탯은
각 `1..3`점 감점한다. 단, 밈성 있는 극단값은 `flex`에서 일부 회복할 수 있다.

## 5. Flex: 0..10

디시 “돌품명품” 감성에 가까운 자랑거리 점수다.

| 조건 | 점수 |
| --- | ---: |
| 극단적 고점: `Slay+6` 이상, `Int+9`, `Dex+9`, `AC+8`급 | `3..5` |
| 보기 드문 조합이 실전적으로 맞물림 | `2..4` |
| 페널티까지 포함해 이야기거리가 있음 | `1..3` |
| 이름/스크린샷/상황이 웃김 | `1..2` |

`flex`는 성능 점수를 대체하지 않는다. 실전성이 낮으면 최대 4점까지만 준다.

## 6. Timing: 0..5

언제 먹었는지에 따른 체감 점수다.

| 조건 | 점수 |
| --- | ---: |
| D:1~Lair 전 핵심 결핍을 해결 | 5 |
| Lair/Orc/S-branch 전에 큰 전력 상승 | 4 |
| Vaults/Depths 전후에도 즉시 채용 | 3 |
| Zot/extended에서만 의미 있음 | 1..2 |
| 이미 비슷한 상위템이 있음 | 0 |

획득 시점 정보가 없으면 기본값 `2`를 사용한다.

## 아이템 타입별 가중치

동일 속성이라도 타입마다 가치가 다르다.

```text
typed_score = luxury_score * type_multiplier
```

| 타입 | 보정 |
| --- | ---: |
| jewellery | `1.05` |
| cloak/boots/gloves/helmet | `1.05` |
| weapon | `1.00` |
| shield/body armour | `0.98` |
| staff/talisman | `0.95` |

장신구와 보조 방어구는 슬롯 기회비용이 낮고 오래 쓰기 쉬워 약간 올린다.
staff/talisman은 빌드 의존성이 강해 단독 평가에서는 약간 낮춘다.

## 최종 공식

```text
raw_score =
    base_fit
  + min(30, offense + defense + utility)
  + synergy
  + purity
  + flex
  + timing

luxury_score = clamp(round(raw_score * type_multiplier), 0, 100)
```

## 판정 예시

### 반지: `rF++ rCorr Slay+3 Stlth-`

```text
base_fit = 12    # ring + useful subtype
power    = 22    # rF++ 7, rCorr 3, Slay+3 12
synergy  = 12    # 대부분의 전투 빌드에 좋음
purity   = 13    # Stlth-만 약한 흠
flex     = 4     # rF++ + Slay 조합
timing   = 2     # 시점 모름
type     = 1.05

score = round(65 * 1.05) = 68
grade = 실전템
```

이 반지는 강하지만 `돌품명품`이라고 부르려면 `Will+`, `AC/EV`, 추가 저항,
또는 초반 획득 같은 맥락이 더 필요하다.

### 무기: `+9 broad axe of holy wrath {SInv Str+5 *Slow}`

```text
base_fit = 19    # 좋은 베이스, 높은 강화, 좋은 브랜드
power    = 25    # 무기 자체 고점 + Str+5 + SInv
synergy  = 14    # melee/extended에서 강함
purity   = 7     # *Slow가 큰 흠
flex     = 5     # +9 holy broad axe의 자랑거리
timing   = 2
type     = 1.00

score = 72
grade = 실전템
```

`*Slow`가 없거나 `rN/Will/rF` 같은 방어 옵션이 붙으면 `명품`권으로 올라간다.

## 구현 시 주의점

1. 원본 아이템 intrinsic과 randart 추가 속성을 먼저 분리해야 한다.
2. 빌드 정보가 없을 때는 단독 평가 모드로 계산하고 `synergy`를 보수적으로 준다.
3. 같은 속성의 과잉 중첩은 diminishing return을 적용한다.
4. 페널티는 단순 감점이 아니라 특정 빌드에서는 치명 감점으로 승격할 수 있다.
5. `luxury_score`와 별도로 `practical_score`, `meme_score`, `risk_score`를 저장하면
   UI에서 “왜 명품/돌품인지” 설명하기 쉽다.

## 참고 링크

- 디시인사이드 로그라이크 갤러리, `돌품명품대회를 개최합니다.`:
  <https://gall.dcinside.com/mgallery/board/view/?id=rlike&no=236434>
- 디시인사이드 로그라이크 갤러리, `돌품명품) 체이신도 돌품명품 출품합니다.`:
  <https://gall.dcinside.com/board/view/?id=rlike&no=517964>
- 디시인사이드 로그라이크 갤러리, `돌품명품 가능?`:
  <https://gall.dcinside.com/mgallery/board/view/?id=rlike&no=478064>
- 디시인사이드 로그라이크 갤러리, `돌품명품 심플이즈베스트`:
  <https://gall.dcinside.com/mgallery/board/view/?id=rlike&no=395290>
