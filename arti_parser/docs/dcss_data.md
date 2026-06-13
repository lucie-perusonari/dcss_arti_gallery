# dcss_data.py

`dcss_data.py`는 공식 DCSS source tree를 참고해 정리한 정적 lookup 데이터입니다. 사람이 직접
운영 로직을 넣는 모듈이 아니라, `constants.py`와 평가 로직이 참조하는 데이터 모듈로 취급합니다.

저장소 정책상 생성용 스크립트는 기본적으로 만들지 않습니다. 이 모듈에도 생성기를 두지 않고,
필요한 경우 공식 DCSS 원본과 현재 상수의 차이를 사람이 검토해 반영합니다.

참고 원본:

- `item-prop.cc`: <https://raw.githubusercontent.com/crawl/crawl/master/crawl-ref/source/item-prop.cc>
- `art-data.txt`: <https://raw.githubusercontent.com/crawl/crawl/master/crawl-ref/source/art-data.txt>

## 주요 데이터

- `DCSS_UNRANDART_NAMES`: unrandart 이름 목록입니다.
- `DCSS_ARMOUR_SLOTS`: armour base item과 slot mapping입니다.
- `DCSS_ARMOUR_STATS`: armour base item의 AC, EV penalty, 가격, slot, 착용 size 정보입니다.
- `DCSS_ARMOUR_ATTRIBUTES`: armour base item의 intrinsic resistance/attribute token 목록입니다. `item-prop.cc`의 armour `flags` 값을 기준으로 정리합니다.
- `DCSS_WEAPON_STATS`: weapon base item의 damage, hit, speed, skill, size, damage type, 생성 가중치, 가격 정보입니다.
- `DCSS_STAFF_STATS`: magical staff의 school, damage multiplier, AC check, damage type 정보입니다.
- `DCSS_MISSILE_STATS`: missile의 damage, mulch rate, 가격 정보입니다.

## 사용 위치

- `constants.py`가 `UNRANDART_NAMES`에 DCSS unrandart 목록을 합칩니다.
- `constants.py`가 armour slot별 item set을 만들 때 `DCSS_ARMOUR_SLOTS`를 합칩니다.
- `constants.py`가 `BASE_ITEM_ATTRIBUTES`에 `DCSS_ARMOUR_ATTRIBUTES`를 합쳐 armour intrinsic 속성을 random attribute에서 제외합니다.
- `evaluator.py`가 armour/weapon base score 계산에 `DCSS_ARMOUR_STATS`와 `DCSS_WEAPON_STATS`를 우선 사용합니다.

## 변경 시 주의점

- 수동 편집보다 공식 DCSS 원본과 산출물의 차이를 먼저 확인합니다.
- 생성 스크립트는 추가하지 않습니다. 참고 원본 위치는 이 문서에 남기고, 상수 변경은 diff를 검토할 수 있게 작게 유지합니다.
- 생성기가 필요하다는 판단이 들면 먼저 저장소 공통 스크립트 정책을 확인하고, 테스트 fixture/mock 생성인지 운영 필수 생성인지 분류합니다. 테스트용 생성기는 `tests/` 아래에만 둘 수 있습니다.
