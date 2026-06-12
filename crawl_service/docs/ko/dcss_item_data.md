# DCSS 아이템 데이터

# DCSS item 상수는 수기로 작성된 기본값에, 공식 Dungeon Crawl: Stone Soup 소스 트리에서 생성한 데이터로 보강합니다.

## Source

- 저장소: <https://github.com/crawl/crawl>
- 현재 생성 버전: `0.34.1`
- 소스 파일:
  - `crawl-ref/source/dat/descript/items.txt`
  - `crawl-ref/source/art-data.txt`
  - `crawl-ref/source/item-prop.cc`

공식 Crawl README에는 최신 아이템 설명이 게임 내 `?/`와 `dat/descript/`(게임 외부)에서 확인된다고 나옵니다.

## 생성 모듈

Run:

```sh
python3 scripts/update_dcss_item_data.py --version 0.34.1
```

실행 시 `crawl_service/domain/constants/generated_dcss_data.py`가 다음 항목으로 갱신됩니다.

- `DCSS_ITEM_FLAVOUR_TEXT`: 정규화된 아이템명 기준의 아이템 설명 텍스트.
- `DCSS_UNRANDART_NAMES`: `art-data.txt`에서 파싱한 unrandart 이름.
- `DCSS_EQUIPMENT_NAMES`: 대분류 기준 장비명 목록.
- `DCSS_ARMOUR_SLOTS`: Crawl 슬롯명으로 매핑한 방어구 아이템명.

`crawl_service/domain/constants/` package가 이 생성 모듈을 import해 로컬 호환 별칭과 점수용 상수와 병합합니다.
