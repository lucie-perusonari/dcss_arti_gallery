# constants.py

`constants.py`는 파싱, 분류, 평가에서 사용하는 정규식과 lookup table을 모읍니다.

## 주요 데이터

- artifact title, property block, enchantment, description 파싱 정규식.
- 내부 property token과 multi-word property token 목록.
- weapon brand, ranged weapon, armour slot item 목록.
- base subtype/base item intrinsic attribute 목록.
- unrandart 이름 목록.
- 평가용 `TOP_BASE_ITEMS`, `GOOD_BASE_ITEMS`, `GOOD_BRANDS`, `UTILITY_SCORES`,
  `PENALTY_SCORES`, `SPELL_SCHOOL_KEYS`.

## 다른 모듈과의 연결

- `parser.py`는 정규식, internal token, multi-word token, unrandart key를 사용합니다.
- `classifier.py`는 item 목록, brand, intrinsic attribute table을 사용합니다.
- `evaluator.py`는 좋은 base item, 좋은 brand, utility, penalty, spell school 점수 table을
  사용합니다.

## 변경 시 주의점

- `UNRANDART_NAMES`와 armour slot item 목록은 `dcss_data.py`의 generated 데이터와 합쳐집니다.
- 새 property token을 추가할 때 parser와 evaluator가 그 token을 어떻게 해석하는지도 확인합니다.
- 정규식 변경은 `.txt`, `.lst` 양쪽 추출에 영향을 줄 수 있습니다.
