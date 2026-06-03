# DCSS 타일 출처

아래 PNG 파일은 공식 Dungeon Crawl Stone Soup 저장소에서 가져온 것입니다.

- 저장소: <https://github.com/crawl/crawl>
- 소스 디렉터리: `crawl-ref/source/rltiles/item`
- 로컬 파일명은 API에서 쓰기 편한 kebab-case로 정규화했습니다.
- 타일 선택 로직 출처: `crawl-ref/source/tilepick.cc`

갤러리는 아이템 타입/세부 타입별 아티팩트 이미지에 공식 DCSS 타일을 사용합니다.

- `weapon/`, `weapon/ranged/`: 근접/원거리 무기의 기본 타일 모음. randart 무기 변형은 `randart/weapon/<base>-*.png`로 복사.
- `armour/`, `armour/headgear/`, `armour/shields/`: 갑옷, 망토, 부츠, 장갑, 투구, 모자, 방패, 구체(orb) 타일. Boots/gloves/helmets/robes/orbs의 공식 artefact/enchant 변형은 `randart/armour/<slot>-*.png`로 복사.
- `ring/randarts/`, `amulet/randarts/`: 장신구 randart 타일 세트는 각각 `randart/ring/ring-*.png`, `randart/amulet/amulet-*.png`에 복사.
- `staff/`: staff randart 변형은 `staff-artefact*.png`에서 `randart/staff/staff-*.png`로 복사.
- `talisman/`: talisman subtype 타일.

기본적으로 Crawl은 `item.rnd`로 randart 타일 변형을 고릅니다. 그러나 morgue artifact 문서에는 이 값이 보존되지 않기 때문에, API와 프론트엔드 mock 데이터에서는 artifact id/name 해시로 결정적 변형을 선택합니다.
이렇게 하면 같은 아티팩트는 렌더링마다 동일하게 유지되면서도, 동일 base randart 간에는 서로 다른 공식 DCSS 타일이 보일 수 있습니다.

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
