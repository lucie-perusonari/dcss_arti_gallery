# Reddit Randart Language And Examples

이 문서는 Reddit `r/dcss`에서 좋은 랜덤 아티팩트(randart)를 표현할 때 쓰이는
영어 표현과, 성능이 좋다고 평가된 아이템 패턴을 정리한 참고 자료다.

조사일: `2026-06-02`

## Purpose

한국 커뮤니티의 `돌품명품`은 "성능이 좋고 자랑할 만한 랜덤 아티팩트"를
말한다. Reddit에는 같은 의미의 고정 용어 하나가 있다기보다, 아이템의 성능,
시점, 빌드 적합성, 희귀성을 강조하는 여러 표현이 섞여 쓰인다.

이 문서는 다음 용도로 쓴다.

- `luxury_score`의 영어권 커뮤니티 표현 매핑
- 좋은 randart 사례의 feature 추출
- frontend copy, 검색 태그, 평가 설명 문구 작성

## English Expressions

| Korean sense | Reddit-style expression | Usage note |
| --- | --- | --- |
| 돌품명품 | `god tier` | 최상급 방어구, 초반 생존을 크게 바꾸는 아이템에 자주 붙음 |
| 돌품명품 | `insane randart` | 극단적으로 높은 강화/저항/Slay 조합을 강조 |
| 돌품명품 | `busted randart` | 밸런스가 깨져 보일 정도로 강한 장신구/방어구/무기 |
| 돌품명품 | `crazy randart` | 많은 좋은 옵션이 한 아이템에 몰린 경우 |
| 돌품명품 | `amazing randart` | 넓게 쓰이는 긍정 표현, `god tier`보다는 약할 수 있음 |
| 돌품명품 | `sick` | 비격식 표현. 강한 무기나 초반 loot brag에 사용 |
| 돌품명품 | `ridiculous` | 좋은 쪽으로도, 말도 안 되는 RNG라는 뜻으로도 쓰임 |
| 명품 | `endgame-worthy` | 최종 무기로 계속 써도 되는가를 판단할 때 유용 |
| 명품 | `will win you the game` | 3-rune 승리에 충분한 수준의 강한 아이템 |
| 명품 | `more than sufficient to win` | 꼭 최상급은 아니어도 승리에는 충분한 아이템 |
| 명품 | `solid` | 안정적으로 좋은 실전템 |
| 명품 | `great` | 범용 긍정. 슬롯/빌드 맥락을 같이 봐야 함 |
| 실전템 | `good enough` | 최적은 아니지만 run을 끝내기에 충분함 |
| 실전템 | `comparable to or better than` | 좋은 일반 +9 branded weapon과 비교할 때 사용 |
| 실전템 | `carry most of a run` | 초중반을 밀어주는 무기/장신구 |
| 잡옵/돌품 | `trash` | 평균 randart나 안 맞는 옵션을 낮게 평가 |
| 돌품 | `trap` | 좋아 보이지만 페널티/anti-synergy 때문에 위험한 아이템 |
| 돌품 | `unusable` | 종족/빌드/슬롯 때문에 못 쓰는 고성능 아이템 |

## High-Performance Patterns

### 1. Strong base plus high enchantment

좋은 무기/방어구 base에 높은 enchantment가 붙으면 Reddit에서도 바로 높은 평가를
받는다. 특히 `crystal plate armour`, `gold dragon scales`, `broad axe`,
`eveningstar`, `demon blade`, `hand cannon`, `quick blade` 같은 base는 옵션이
조금 부족해도 평가 기준점이 높다.

Scoring implication:

- `base_fit`은 영어권 평가에서도 매우 중요하다.
- 낮은 base의 artefact는 좋은 속성이 붙어도 +9 top-tier branded weapon보다
  낮게 평가될 수 있다.

### 2. Armour with extreme AC

Reddit에서 가장 명확하게 `god tier` 또는 `insane` 평가가 나오는 유형은 높은
강화 수치의 heavy armour다.

| Source | Item data | Community judgement |
| --- | --- | --- |
| [YAVP: FoFi Firestarter, insane randart CPA](https://www.reddit.com/r/dcss/comments/c9avq3) | `+19 Crystal Plate Armor {rF+++ MR- Slay+4}` | 작성자가 "best randart armor"와 "most amazing armor"로 표현. 착용 후 AC가 크게 상승했다고 설명 |
| [Good armour early acquirement option on a pure caster?](https://www.reddit.com/r/dcss/comments/14t8dro) | 높은 강화의 dragon scales/GDS 논의 | 댓글에서 `god tier`의 핵심을 추가 저항보다 `+16` AC로 봄 |
| [Are unrandarts the best items in the game](https://www.reddit.com/r/dcss/comments/qfbeno) | `+18 randart CPA` 논의 | 매우 희귀한 career-level roll로 취급 |

Scoring implication:

- `AC+n`과 armour enchantment는 방어구 평가에서 큰 weight를 가져야 한다.
- `rF+++`, `rC+++` 같은 저항은 강하지만, heavy armour에서는 AC 고점이 먼저
  언급되는 경우가 많다.

### 3. Weapon that can replace a fully enchanted normal weapon

무기는 randart라는 이유만으로 고평가되지 않는다. 좋은 일반 무기
`+9 broad axe of freezing`, `+9 demon blade`, `+9 eveningstar`와 비교해서
이겨야 한다는 관점이 강하다.

| Source | Item data | Community judgement |
| --- | --- | --- |
| [Are Artefacts typically preferable weapons?](https://www.reddit.com/r/dcss/comments/1r3yf01/are_artefacts_typically_preferable_weapons/) | 일반론 | 좋은 base type, brand, enchantment level이 없으면 artefact가 반드시 우월하지 않다고 설명 |
| [Randart broad axe vs Consecrated labrys](https://www.reddit.com/r/dcss/comments/1tbst3d/for_a_3_rune_run_should_i_switch_to_the/) | randart broad axe, vamp brand, melee build | `will win you the game`, `amazing weapon`, `more than sufficient to win a three rune game`로 평가 |
| [Never made it this far before](https://www.reddit.com/r/dcss/comments/198atds) | `+9 heavy eveningstar`, later `+11 artifact eveningstar` | `endgame worthy`, `amazing`으로 평가 |
| [Found on D:4 on MiBe](https://www.reddit.com/r/dcss/comments/1lyena4) | early broad axe | `endgame-worthy`, `Free S-runes with careful play`로 평가 |

Scoring implication:

- 무기 점수는 `base type + enchantment + brand + build fit`이 핵심이다.
- 저항이 많은 약한 base weapon보다, 강한 base와 좋은 brand가 더 중요할 수 있다.
- `vamp`, `heavy`, `freezing`, `elec`, `speed` 등은 맥락에 따라 높은 공격 점수를
  준다.

### 4. Jewellery with multiple combat stats or resistances

장신구는 여러 ring/amulet 효과를 한 slot에 압축하면 높은 평가를 받는다.

| Source | Item data | Community judgement |
| --- | --- | --- |
| [Totally insane start](https://www.reddit.com/r/dcss/comments/1aptdnn) | good randart amulet/rings with multiple resistances, preferably `+Blink` or `+Inv` | D1 최고의 단일 아이템 후보로 언급 |
| [Not bad for a D7 HOFi. Amazing acquirement](https://www.reddit.com/r/dcss/comments/142zoov) | ring with four positive combat stats vs gloves | "4 rings on one finger"라는 식으로 고평가 |
| [Has anybody ever seen this amulet?](https://www.reddit.com/r/dcss/comments/1k4iby1) | randart amulet of Faith with `Str+3`, `Dex-4` 등 | `pretty good overall`; 작은 stat penalty는 감수 가능하다는 평가 |
| [YAVP: MDFw of Dith](https://www.reddit.com/r/dcss/comments/1i9yfu9) | crazy randart rings and amulets | 하이브리드 캐릭터의 강한 loot package로 언급 |

Scoring implication:

- `Slay`, `AC`, `EV`, `SH`, 핵심 저항, `Regen`, `+Blink`, `+Inv`가 한 장신구에
  모이면 high-value로 본다.
- penalty가 작고 빌드에 덜 중요한 stat이면 `purity`에서 약간만 감점한다.
- ring/amulet은 swap 가능성과 slot pressure를 함께 고려한다.

### 5. Auxiliary armour slot with irreplaceable combat value

장갑, 부츠, 망토, 헬멧처럼 보조 방어구 slot에 `Slay`, `AC`, 저항이 붙으면
대체하기 어렵기 때문에 높게 평가된다.

| Source | Item data | Community judgement |
| --- | --- | --- |
| [Not bad for a D7 HOFi. Amazing acquirement](https://www.reddit.com/r/dcss/comments/142zoov) | gauntlets with `AC+3 Slay+5` 논의 | `nearly impossible to find something better for the hand slot`; Slaying은 절대 하찮지 않다고 평가 |
| [Randart broad axe vs Consecrated labrys](https://www.reddit.com/r/dcss/comments/1tbst3d/for_a_3_rune_run_should_i_switch_to_the/) | boots context | `best boots in the game`이라는 slot-specific 평가가 붙음 |

Scoring implication:

- 보조 방어구의 `Slay+n`, `AC+n`, `Regen`, 핵심 저항은 slot scarcity 보너스를
  받아야 한다.
- 장갑의 `Slay+5`는 후반에도 대체가 어려운 공격력으로 본다.

### 6. Early timing changes the judgement

같은 아이템이라도 D:1-D:4 같은 초반에 나오면 `busted start`, `insane start`,
`carry most of a run` 같은 표현을 받는다.

| Source | Item data | Community judgement |
| --- | --- | --- |
| [Totally insane start](https://www.reddit.com/r/dcss/comments/1aptdnn) | D1-D9에 high-tier unrands/randarts 연속 출현 | `busted start`, `insane`으로 표현 |
| [how rare is this sword for level 2 dungeon?](https://www.reddit.com/r/dcss/comments/1h8ylsw) | early `+9` sword with useful resists | `+9 is AMAZING when you're near 0 training`; 초중반 저항이 크게 평가됨 |
| [Love finding unusable endgame artifacts on D2](https://www.reddit.com/r/dcss/comments/13ah2eq) | early endgame armour but unusable species/build context | `god tier armor`라도 착용 불가하면 brag/irony가 됨 |

Scoring implication:

- `timing`은 독립 축으로 유지한다.
- 초반 `+9`, `rPois`, `rF+`, `rElec`, `Regen`, `AC+`는 후반보다 더 큰 체감 가치를
  가진다.
- 종족이 못 입는 armour처럼 `unusable`한 고성능 아이템은 성능 점수와 실사용
  점수를 분리해야 한다.

## Phrase-To-Grade Mapping

| Reddit phrase | Suggested Korean grade | Score hint |
| --- | --- | ---: |
| `god tier`, `busted`, `insane`, `ridiculous` | `돌품명품` | `90..100` |
| `will win you the game`, `one of the best`, `endgame-worthy` | `명품` 또는 `돌품명품` | `80..95` |
| `amazing`, `crazy`, `sick`, `awesome` | `명품` | `80..90` |
| `solid`, `great`, `good overall` | `실전템` 또는 `명품` | `65..85` |
| `good enough`, `more than sufficient` | `실전템` | `65..80` |
| `trap`, `unusable`, `trash`, `crap` | `돌품` 또는 특수 사례 | `0..50` |

## Practical Scoring Notes

- Reddit 평가는 "아이템 자체의 절대 수치"보다 "이 캐릭터가 이 시점에 쓰면
  게임을 바꾸는가"를 자주 본다.
- 무기는 artefact 여부보다 좋은 base, 좋은 brand, 높은 enchantment가 먼저다.
- 방어구는 높은 AC/enchantment가 매우 큰 신호다.
- 장신구와 보조 방어구는 slot scarcity 때문에 복합 옵션의 가치가 크다.
- `Slay`는 공격력뿐 아니라 accuracy에도 기여한다고 평가되며, 특히 보조 방어구와
  장신구에서 premium stat으로 취급된다.
- `Will-`, `*Corrode`, `*Fragile`, `-Tele`, `Inacc`, `Harm` 같은 페널티는 빌드와
  swap 가능성에 따라 감점 폭이 크게 달라진다.

## Source Index

- <https://www.reddit.com/r/dcss/comments/c9avq3>
- <https://www.reddit.com/r/dcss/comments/14t8dro>
- <https://www.reddit.com/r/dcss/comments/qfbeno>
- <https://www.reddit.com/r/dcss/comments/1r3yf01/are_artefacts_typically_preferable_weapons/>
- <https://www.reddit.com/r/dcss/comments/1tbst3d/for_a_3_rune_run_should_i_switch_to_the/>
- <https://www.reddit.com/r/dcss/comments/198atds>
- <https://www.reddit.com/r/dcss/comments/1lyena4>
- <https://www.reddit.com/r/dcss/comments/1aptdnn>
- <https://www.reddit.com/r/dcss/comments/142zoov>
- <https://www.reddit.com/r/dcss/comments/1k4iby1>
- <https://www.reddit.com/r/dcss/comments/1i9yfu9>
- <https://www.reddit.com/r/dcss/comments/1h8ylsw>
- <https://www.reddit.com/r/dcss/comments/13ah2eq>
