# parser.py

`parser.py`는 artifact 이름과 property token을 문법적으로 파싱합니다. 이 모듈은 item class나
점수를 판단하지 않고, 문자열에서 안정적인 구조화 값만 뽑는 역할에 집중합니다.

## 주요 함수

- `artifact_display_name`: trailing property block과 선행 `the `를 제거합니다.
- `normalized_artifact_name`: `cursed`/`chaotic` 같은 item status prefix를 제거한 출력용 이름을 만듭니다.
- `artifact_enchantment_and_base_text`: `+6 broad axe` 같은 강화 수치와 base text를 분리합니다.
- `artifact_base_item`: bracket subtype과 display name에서 base item을 추론합니다.
- `artifact_attributes`: property block을 token 목록으로 쪼개고 visible description을 연결합니다.
- `is_random_artifact`: unrandart와 plain magic item을 제외합니다.
- `parse_property_token`: `Slay+3`, `rF++`, `Regen+` 같은 token을 `(key, value)`로 정규화합니다.

## token 해석

- signed token은 정수 값으로 변환합니다. 예: `Slay+3` -> `("Slay", 3)`.
- resistance step token은 `+`, `-` 개수로 단계 값을 만듭니다. 예: `rF++` -> `("rF", 2)`.
- boolean plus token은 `True`로 변환합니다. 예: `Regen+` -> `("Regen", True)`.
- 그 외 token은 boolean attribute로 취급합니다.

## 변경 시 주의점

- `INTERNAL_PROPERTY_TOKEN_KEYS`에 속한 token은 저장 attribute에서 제외됩니다.
- multi-word property는 `MULTI_WORD_PROPERTY_TOKENS`에 등록해야 단일 token으로 유지됩니다.
- `cursed`와 `chaotic` prefix는 randart 정체성이 아니라 item status flag로 취급합니다.
  원문은 extractor의 `raw_text_block`에 남기고, randart 판정과 출력 이름에는 prefix를 제거한
  normalized name을 사용합니다.
- randart 제외 규칙은 `UNRANDART_NAME_KEYS`, `EXCLUDED_RANDOM_ARTIFACT_NAME_KEYS`,
  plain magic item 판정과 연결됩니다.
