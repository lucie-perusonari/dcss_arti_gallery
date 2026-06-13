# dcss_data.py

`dcss_data.py`는 공식 DCSS source tree에서 생성된 정적 데이터입니다. 사람이 직접 운영 로직을
넣는 모듈이 아니라, `constants.py`가 참조하는 generated lookup source로 취급합니다.

## 주요 데이터

- `DCSS_UNRANDART_NAMES`: unrandart 이름 목록입니다.
- `DCSS_ARMOUR_SLOTS`: armour base item과 slot mapping입니다.

## 사용 위치

- `constants.py`가 `UNRANDART_NAMES`에 generated unrandart 목록을 합칩니다.
- `constants.py`가 armour slot별 item set을 만들 때 `DCSS_ARMOUR_SLOTS`를 합칩니다.

## 변경 시 주의점

- 파일 상단 주석처럼 generated data로 취급합니다.
- 수동 편집보다 생성 스크립트 경로를 확인하고 갱신하는 편이 안전합니다.
