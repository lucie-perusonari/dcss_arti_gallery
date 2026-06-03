# DCSS Tile Sources

These PNG files are copied from the official Dungeon Crawl Stone Soup repository:

- Repository: <https://github.com/crawl/crawl>
- Source directory: `crawl-ref/source/rltiles/item`
- Local names normalize DCSS tile filenames to API-friendly kebab-case names.
- Tile selection logic source: `crawl-ref/source/tilepick.cc`

The gallery uses these official DCSS tiles for item-type and subtype-specific artifact images:

- `weapon/` and `weapon/ranged/`: melee and ranged weapon base item tile families. Randart weapon variants are copied to `randart/weapon/<base>-*.png`.
- `armour/`, `armour/headgear/`, and `armour/shields/`: body armour, cloaks, boots, gloves, helmets, hats, shields, and orbs. Boots, gloves, helmets, robes, and orbs with official artefact/enchant variants are copied to `randart/armour/<slot>-*.png`.
- `ring/randarts/` and `amulet/randarts/`: jewellery randart tile sets copied to `randart/ring/ring-*.png` and `randart/amulet/amulet-*.png`.
- `staff/`: staff randart variants copied from `staff-artefact*.png` to `randart/staff/staff-*.png`.
- `talisman/`: talisman subtype tiles.

Crawl normally chooses randart tile variants with `item.rnd`. Morgue artifact documents do not preserve that field, so the API and frontend mock data choose a deterministic variant from the artifact id/name hash. This keeps the same artifact stable across renders while allowing same-base randarts to display different official DCSS tiles.

Notable normalized filenames:

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
