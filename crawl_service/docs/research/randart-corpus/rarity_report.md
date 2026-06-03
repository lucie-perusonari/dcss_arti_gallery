# Randart 희소도 및 명품 보고서

이 문서는 DCSS randart 속성 생성 메커니즘을 단순 Monte Carlo로 재현해,
현재 repo의 실전성/희소도/명품 판정 사이의 관계를 정리한다.

## 범위

- Source baseline: Crawl `0.34.1` `artefact.cc` randart property generation.
- Source URL: <https://github.com/crawl/crawl/blob/0.34.1/crawl-ref/source/artefact.cc>
- Samples: `200,000` per profile, `1,400,000` total.
- Seed: `20260602`.
- This is conditional on an item already becoming a randart; it does not model whole-game item placement, shop generation, acquirement, or exact base-item frequency.
- Weapon brand generation and item-specific artprop eligibility are approximated from `artefact.cc`; fixed props, god gifts, unrand replacement, and full ego/base generation are out of scope.
- High enchantment is included as a luxury signal for fixed representative profiles and real corpus items. Whole-game probability for those enchantment/base outcomes still requires the full item generator.

## 메커니즘 희소도

Before item class or scoring is considered, the source quality roll is already strongly low-biased.
`quality = 1 + Binomial(6, 1/21)`, and bad props are `Binomial(2, 1/21)`.

### Quality Roll

| Value | Probability |
| --- | ---: |
| `1` | 74.62% |
| `2` | 22.39% |
| `3` | 2.80% |
| `4` | 0.187% |
| `5` | 0.0070% |
| `6` | 0.0001% |
| `7` | <0.0001% |

### Good Property/Enhancement Opportunities

| Value | Probability |
| --- | ---: |
| `>= 1` | 100.00% |
| `>= 2` | 32.32% |
| `>= 3` | 5.24% |
| `>= 4` | 0.505% |
| `>= 5` | 0.031% |
| `>= 6` | 0.0012% |
| `>= 7` | <0.0001% |

## 집계 시뮬레이션

| Metric | Value |
| --- | ---: |
| Average score | 45.96 |
| Max score observed | 79 |

### Practical Grade Rarity

| Value | Count | Rate |
| --- | ---: | ---: |
| `돌품` | 781,914 | 55.85% |
| `애매템` | 611,277 | 43.66% |
| `실전템` | 6,809 | 0.486% |

### Luxury Grade Rarity

| Value | Count | Rate |
| --- | ---: | ---: |
| `돌품` | 781,914 | 55.85% |
| `돌품명품 후보` | 2,657 | 0.190% |
| `명품` | 5,791 | 0.414% |
| `실전템` | 607 | 0.043% |
| `애매템` | 421,379 | 30.10% |
| `희귀 잡템` | 187,652 | 13.40% |

### Luxury Signals

| Value | Count | Rate |
| --- | ---: | ---: |
| `Slay+4 이상` | 4,039 | 0.288% |
| `Slay+6 이상` | 1,047 | 0.075% |
| `무기 +9 이상` | 200,000 | 14.29% |
| `무페널티` | 1,269,495 | 90.68% |
| `저항 3종 이상` | 3,975 | 0.284% |

## 아이템 프로필별

| Profile | Avg | Max | practical 실전템+ | luxury 명품+ | 돌품명품 후보+ | Slay+4+ | Slay+6+ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| amulet | 44.55 | 78 | 0.061% | 0.335% | 0.321% | 0.373% | 0.093% |
| ring | 43.74 | 76 | 0.033% | 0.394% | 0.383% | 0.471% | 0.123% |
| +0 gloves | 43.54 | 79 | 0.035% | 0.307% | 0.291% | 0.397% | 0.101% |
| +4 robe | 41.60 | 73 | 0.011% | 0.068% | 0.066% | 0.370% | 0.097% |
| +5 plate armour | 42.55 | 73 | 0.022% | 0.092% | 0.090% | 0.408% | 0.108% |
| +9 eveningstar | 55.87 | 78 | 3.13% | 3.02% | 0.178% | 0% | 0% |
| +3 scimitar | 49.86 | 72 | 0.110% | 0.0035% | 0% | 0% | 0% |

## 실제 Morgue 코퍼스 비교

기존 `crawl_service/docs/research/randart-corpus/corpus.json` 150개 표본은 생성 확률 표본이 아니라
실제 morgue에서 관측된 아이템 표본이다. 그래도 시뮬레이션 결과의 고점 희소성과
현실 관측의 온도를 비교하는 참고값으로 쓸 수 있다.

| Metric | Value |
| --- | ---: |
| Corpus artifacts | 150 |
| Average score | 48.31 |
| Max score | 74 |
| Average rarity score | 6.93 |
| Max rarity score | 45 |

### Corpus Practical Grades

| Value | Count | Rate |
| --- | ---: | ---: |
| `돌품` | 55 | 36.67% |
| `애매템` | 89 | 59.33% |
| `실전템` | 6 | 4.00% |

### Corpus Luxury Grades

| Value | Count | Rate |
| --- | ---: | ---: |
| `돌품` | 54 | 36.00% |
| `돌품명품 후보` | 1 | 0.667% |
| `명품` | 3 | 2.00% |
| `실전템` | 2 | 1.33% |
| `애매템` | 82 | 54.67% |
| `희귀 잡템` | 8 | 5.33% |

### Corpus Luxury Signals

| Value | Count | Rate |
| --- | ---: | ---: |
| `Slay+4 이상` | 4 | 2.67% |
| `Slay+6 이상` | 2 | 1.33% |
| `무기 +9 이상` | 9 | 6.00% |
| `무페널티` | 94 | 62.67% |
| `저항 3종 이상` | 5 | 3.33% |
| `중갑/방패 +10 이상` | 2 | 1.33% |

## 해석

- `grade`는 실전성 등급이고, `luxury_grade`는 실전성에 `rarity_score`를 결합한 커뮤니티식 명품 판정이다.
- 명품 등급은 단순히 좋은 속성이 하나 붙는 사건이 아니다. 품질값이 3 이상으로 올라갈 확률부터 약 5%대이고, 4회 이상 좋은 속성/강화 기회는 약 0.5%대다.
- `Slay+4` 이상은 source 로직상 같은 `Slay` prop을 여러 번 강화해야 하는 쪽에 가까워, 장신구와 방어구에서 강한 희소도 신호가 된다.
- 강화수치는 명품성의 핵심 신호라 `rarity_score`에 반영한다. 다만 이 시뮬레이션은 대표 프로필의 고정 강화수치를 쓰므로, 게임 전체에서 해당 강화수치와 base가 함께 나올 확률은 별도 item generator 분석이 필요하다.
- 무기는 `Slay`가 randart property로 붙지 않기 때문에 명품 판정이 base, enchantment, brand, 저항 압축에 더 의존한다. 같은 점수라도 장신구/보조 방어구의 `Slay` spike와 성격이 다르다.
- 이 결과는 randart 하나당 조건부 확률이다. 한 게임에서 체감되는 희소도는 randart 생성 기회 수, branch/shop/acquirement, base item 분포까지 곱해져 더 낮아진다.

## 재현

```sh
python3 scripts/simulate_randart_rarity.py --samples 200000 --seed 20260602
```

Raw simulation output: `crawl_service/docs/research/randart-corpus/rarity_simulation.json`.
