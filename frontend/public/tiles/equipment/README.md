# DCSS equipment icons

이 디렉터리는 공식 Dungeon Crawl Stone Soup 저장소의 `crawl-ref/source/rltiles/item`에서 장비 계열 PNG를 가져와
사용 목적별로 정리한 asset mirror입니다.

- upstream: <https://github.com/crawl/crawl/tree/master/crawl-ref/source/rltiles/item>
- 기준 파일: `crawl-ref/source/rltiles/dc-item.txt`
- 다운로드 기준 branch: `master`
- 로컬 갱신일: 2026-06-15

## 분류

- `normal`: `dc-item.txt`에서 enchant variation 없이 선언된 기본 장비 타일
- `ego`: `shiny`, `runed`, `glowing` enchant variation에 연결된 장비 타일
- `artifact`: `randart` enchant variation에 연결되었거나 파일명/경로가 artefact, artifact, unrand, `_art` 계열인 장비 타일

같은 PNG가 여러 variation에 함께 쓰이면 각 분류에 모두 복사합니다. 예를 들어 일부 기본 타일은 ego 또는 randart
variation에서도 같은 이미지로 쓰일 수 있습니다.

## 범위

장비 계열로 식별한 upstream 하위 디렉터리는 다음과 같습니다.

- `weapon`
- `armour`
- `ring`
- `amulet`
- `staff`
- `talisman`

## 파일 수

분류 디렉터리 기준 파일 수:

- `normal`: 402
- `ego`: 84
- `artifact`: 294

원본 PNG 기준 고유 파일 수는 711개입니다. 여러 분류에 중복 복사된 원본 PNG는 69개입니다.
API가 모든 gallery item을 randart로 표시하기 위해 ring/amulet/staff randart 후보와 talisman 타일은
`artifact` 아래에도 복사해 둡니다.

분류별 장비 계열 파일 수:

| 분류 | amulet | armour | ring | staff | talisman | weapon |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| `normal` | 50 | 118 | 67 | 30 | 22 | 115 |
| `ego` | 0 | 23 | 0 | 0 | 0 | 61 |
| `artifact` | 20 | 92 | 20 | 7 | 22 | 133 |
