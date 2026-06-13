# evaluator.py

`evaluator.py`는 `random_attributes`와 item metadata를 점수와 등급으로 평가합니다. base item의
intrinsic 속성이 아니라 실제 랜덤 속성을 기준으로 평가하는 것이 핵심 계약입니다.

## 주요 함수

- `evaluate_artifact_data`: 평가 공개 함수입니다.
- `_offense_score`: slay, 능력치, 좋은 brand, spell school 보너스를 계산합니다.
- `_defense_score`: AC, EV, SH, Will, 저항 계열 보너스를 계산합니다.
- `_utility_score`: MP, stealth, SInv, Regen, Rampage 같은 유틸리티를 계산합니다.
- `_penalty_points`: negative token과 penalty token을 감점 포인트로 계산합니다.
- `_base_fit_score`: slot 가치, base item 가치, enchantment, brand 적합도를 계산합니다.
- `_rarity_score`: 고강화, 높은 slay, 복수 저항, penalty 여부 같은 희귀 신호를 계산합니다.

## 출력

- `total`: 0에서 100 사이 practical score입니다.
- `practical_score`: 현재 `total`과 같은 값입니다.
- `rarity_score`: 희귀성 점수입니다.
- `offense`, `defense`, `utility`, `penalty`, `base_fit`: 세부 점수입니다.
- `grade`, `luxury_grade`: 한국어 등급 label입니다.

## 변경 시 주의점

- 평가 입력은 반드시 `classification.random_attributes`여야 합니다.
- scoring formula 변경은 기존 저장 문서 재평가가 필요하므로 `CURRENT_SCORING_VERSION` 갱신을
  검토합니다.
- 등급 label은 frontend 표시와 맞물릴 수 있습니다.
