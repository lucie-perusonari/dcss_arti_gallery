# constants.py

`constants.py`는 파싱과 분류에서 사용하는 정규식, lookup table, 공식 DCSS source tree에서
온 item/unrandart 정적 상수를 모읍니다. 파서, classifier, evaluator가 쓰는 관련 상수의
소유 위치는 이 모듈입니다.

참고 원본:

- `item-prop.cc`: <https://raw.githubusercontent.com/crawl/crawl/master/crawl-ref/source/item-prop.cc>
- `art-data.txt`: <https://raw.githubusercontent.com/crawl/crawl/master/crawl-ref/source/art-data.txt>

## 주요 데이터

- artifact title, property block, enchantment, description 파싱 정규식.
- 내부 property token과 multi-word property token 목록.
- `DCSS_UNRANDART_NAMES`, `DCSS_ARMOUR_STATS`, `DCSS_ARMOUR_ATTRIBUTES`,
  `DCSS_ARMOUR_SLOTS`, `DCSS_WEAPON_STATS`, `DCSS_STAFF_STATS`, `DCSS_MISSILE_STATS`.
- weapon brand 목록.
- `DCSS_WEAPON_STATS`에서 파생한 ranged weapon 목록.
- `DCSS_ARMOUR_SLOTS`에서 파생한 armour slot item 목록과 구버전 morgue 호환 alias.
- base subtype/base item intrinsic attribute 목록.
- `DCSS_UNRANDART_NAMES`에서 파생한 normalized unrandart key 목록.

## 다른 모듈과의 연결

- `parser.py`는 정규식, internal token, multi-word token, unrandart key를 사용합니다.
- `classifier.py`는 item 목록, brand, intrinsic attribute table을 사용합니다.
- `evaluator.py`는 평가용 table을 자체 소유하며, 공식 item stats는 이 모듈에서 직접 읽습니다.

## 변경 시 주의점

- `UNRANDART_NAMES`, ranged weapon, armour slot item 목록, base armour intrinsic 속성은
  이 파일의 `DCSS_*` 정적 데이터에서 파생합니다.
- `shield`, `pair of boots`, `pair of gloves`, `gold dragon scales`, `troll skin`처럼
  DCSS 현재 명칭과 다르지만 과거 morgue에서 보일 수 있는 값은 호환 alias로만 추가합니다.
- 새 property token을 추가할 때 parser와 evaluator가 그 token을 어떻게 해석하는지도 확인합니다.
- 정규식 변경은 `.txt`, `.lst` 양쪽 추출에 영향을 줄 수 있습니다.
