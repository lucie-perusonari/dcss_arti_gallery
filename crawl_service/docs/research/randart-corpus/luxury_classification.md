# Randart Luxury Classification

이 문서는 `crawl_service/docs/research/randart-corpus/corpus.json`의 실제 morgue randart 표본을
커뮤니티식 `명품` 관점으로 다시 분류한 메모다.

기존 `evaluation.total`은 실전성 정렬에 가깝다. 여기서는 Reddit의 `best
randart`, 한국 DCSS 커뮤니티의 `돌품명품` 감각에 맞춰 "그 슬롯에서 정상적인
기대치를 얼마나 벗어났는가"를 더 크게 본다.

## Classification Rule

| Grade | Meaning |
| --- | --- |
| `돌품명품 후보` | 자랑감은 강하지만 페널티, base, 빌드 의존성 때문에 논쟁이 생길 물건 |
| `명품` | 대부분의 관련 빌드가 진지하게 채용할 강한 물건 |

## Corpus Result Summary

이 표본에서 `명품` 수준으로 남길 만한 물건은 장신구의 Slay 압축, 방어구 슬롯의
Slay, 특수한 caster/melee 혼합 옵션에 몰려 있다.

## 돌품명품 후보

| Item | Properties | Note |
| --- | --- | --- |
| `the +4 robe of the Other Side {-Tele Str+6 Slay+6 Archmagi}` | `-Tele`, `Str+6`, `Slay+6`, `Archmagi` | `Slay+6 Archmagi`가 강한 brag 신호다. `-Tele`와 robe base 때문에 실사용은 빌드 의존적이다. |
| `the +2 leather armour of the Hippo {rF+ rCorr Str-3 Slay+6}` | `rF+`, `rCorr`, `Str-3`, `Slay+6` | `Slay+6`은 확실한 출품감이다. 낮은 armour base와 `Str-3` 때문에 명품 판정은 갈린다. |
| `the amulet "Coicka" {^Contam Rampage +Blink +Inv RegenMP+ Slay+2}` | `^Contam`, `Rampage`, `+Blink`, `+Inv`, `RegenMP+`, `Slay+2` | 옵션 압축은 화려하다. 페널티와 빌드 의존성이 있어 실전 명품보다는 재미있는 후보에 가깝다. |

## 명품

| Item | Properties | Note |
| --- | --- | --- |
| `the amulet "Qolow" {Dissipate Str+5 Slay+4}` | `Str+5`, `Slay+4` | 장신구 슬롯에 melee damage가 깔끔하게 압축됐다. 단순하지만 강하다. |
| `the +5 plate armour of the Skies Above {Will+ Slay+4 SInv}` | `Will+`, `Slay+4`, `SInv` | 중갑 melee 기준으로 공격과 방어 결핍을 동시에 메운다. |
| `the amulet of Vuplidd {Dissipate rF+ Will+ Slay+3}` | `rF+`, `Will+`, `Slay+3` | amulet 한 슬롯에서 저항, Will, Slay를 동시에 준다. |
| `the ring of Ladice {rF+ Will+ Int+6 Slay+3}` | `rF+`, `Will+`, `Int+6`, `Slay+3` | caster/hybrid에게 높은 압축 가치가 있다. |
| `the amulet of the Moon {Acrobat rC+ Dex+3 Slay+2 SInv}` | `rC+`, `Dex+3`, `Slay+2`, `SInv` | 전투 스탯과 유틸이 amulet 슬롯에 잘 모였다. |
