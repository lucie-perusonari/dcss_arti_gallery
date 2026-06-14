# DCSS 타일 출처

아래 PNG 파일은 공식 Dungeon Crawl Stone Soup 저장소에서 가져온 것입니다.

- 저장소: <https://github.com/crawl/crawl>
- 소스 디렉터리: `crawl-ref/source/rltiles/item`
- 타일 선택 로직 출처: `crawl-ref/source/tilepick.cc`

갤러리는 아이템 타입/세부 타입별 아티팩트 이미지에 공식 DCSS 타일을 사용합니다.

- 전체 장비 아이콘 mirror는 `equipment/{normal,ego,artifact}` 아래에 원본 `item` 하위 경로를 보존해 둡니다.
- API의 `tile` 선택은 장비 mirror 경로(`/tiles/equipment/...`)를 사용합니다.
- gallery에 노출되는 item은 모두 randart로 간주하므로 API는 `equipment/artifact` 후보만 반환합니다.
- 무기, 방어구, 장신구, staff, talisman은 모두 `equipment/artifact` 아래의 mirror 파일만 사용합니다.

기본적으로 Crawl은 `item.rnd`로 randart 타일 변형을 고릅니다. 그러나 morgue artifact 문서에는 이 값이
보존되지 않기 때문에, Gallery API는 artifact id/name 해시로 결정적 randart 변형을 선택합니다.
이렇게 하면 같은 아티팩트는 렌더링마다 동일하게 유지되면서도, 동일 base randart 간에는 서로 다른 공식 DCSS
타일이 보일 수 있습니다.
무기와 방어구는 `dc-item.txt`에서 `randart` variation으로 지정된 타일만 API 선택 후보로 사용하며,
일반/마법/ego variation 타일은 randart 후보에 섞지 않습니다.
