# DCSS 타일 출처

아래 PNG 파일은 공식 Dungeon Crawl Stone Soup 저장소에서 가져온 것입니다.

- 저장소: <https://github.com/crawl/crawl>
- 소스 디렉터리: `crawl-ref/source/rltiles/item`
- 로컬 파일명은 API에서 쓰기 편한 kebab-case로 정규화했습니다.
- 타일 선택 로직 출처: `crawl-ref/source/tilepick.cc`

갤러리는 아이템 타입/세부 타입별 아티팩트 이미지에 공식 DCSS 타일을 사용합니다.

- 무기: 기본 타일은 `<base>.png` 형태로 두고, randart 변형은 `randart/weapon/<base>-N.png`에 둡니다.
- 방어구: 기본 타일은 `<base>.png` 형태로 두고, boots/gloves/helmet/orb/robe randart 변형은
  `randart/armour/<slot>-N.png`에 둡니다.
- 장신구: 대표 타일은 `ring-randart.png`, `amulet-randart.png`로 두고, randart 변형은
  `randart/ring/ring-N.png`, `randart/amulet/amulet-N.png`에 둡니다.
- Staff: 대표 타일은 `staff-randart.png`로 두고, randart 변형은 `randart/staff/staff-N.png`에 둡니다.
- Talisman: subtype별 타일을 `talisman-<subtype>.png` 형태로 둡니다.

기본적으로 Crawl은 `item.rnd`로 randart 타일 변형을 고릅니다. 그러나 morgue artifact 문서에는 이 값이
보존되지 않기 때문에, Gallery API는 artifact id/name 해시로 결정적 randart 변형을 선택합니다.
이렇게 하면 같은 아티팩트는 렌더링마다 동일하게 유지되면서도, 동일 base randart 간에는 서로 다른 공식 DCSS
타일이 보일 수 있습니다.

주요 정규화 파일명 예시:

- `executioner's axe`: `weapon/executioner_axe1.png` -> `executioners-axe.png`
- `great mace`: `weapon/mace_large1.png` -> `great-mace.png`
- `double sword`: `weapon/double_sword.png` -> `double-sword.png`
- `athame`: `weapon/athame1.png` -> `athame.png`
- `gold dragon scales`: `armour/golden_dragon_armour_art.png` -> `gold-dragon-scales.png`
- `golden dragon scales`: `armour/golden_dragon_armour_art.png` -> `golden-dragon-scales.png`
- `shadow dragon scales`: `armour/shadow_dragon_armour_art.png` -> `shadow-dragon-scales.png`
- `sanguine talisman`: `talisman/vampire.png` -> `talisman-sanguine.png` alias
- `dragon-coil talisman`: `talisman/dragon.png` -> `talisman-dragon-coil.png` alias
- `granite talisman`: `talisman/statue.png` -> `talisman-granite.png` alias
- `riddle talisman`: `talisman/protean.png` -> `talisman-riddle.png` alias
