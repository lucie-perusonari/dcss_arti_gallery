# DCSS Item Data

This project supplements hand-written artifact constants with generated data
from the official Dungeon Crawl: Stone Soup source tree.

## Source

- Repository: <https://github.com/crawl/crawl>
- Current generated version: `0.34.1`
- Source files:
  - `crawl-ref/source/dat/descript/items.txt`
  - `crawl-ref/source/art-data.txt`
  - `crawl-ref/source/item-prop.cc`

The official Crawl README notes that current item descriptions are available
in-game through `?/` and out-of-game under `dat/descript/`.

## Generated Module

Run:

```sh
python3 scripts/update_dcss_item_data.py --version 0.34.1
```

This updates `crawl_service/domain/generated_dcss_data.py` with:

- `DCSS_ITEM_FLAVOUR_TEXT`: item description text keyed by normalized item name.
- `DCSS_UNRANDART_NAMES`: unrandart names parsed from `art-data.txt`.
- `DCSS_EQUIPMENT_NAMES`: equipment names grouped by broad item class.
- `DCSS_ARMOUR_SLOTS`: armour item names mapped to Crawl slot names.

`crawl_service/domain/constants.py` imports this generated module and merges it
with local compatibility aliases and scoring-specific constants.
