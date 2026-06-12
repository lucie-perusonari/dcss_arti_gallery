# DCSS Item Data

DCSS item constants combine hand-maintained local defaults with generated armour-slot and fixed-artifact data from the official Dungeon Crawl: Stone Soup source tree.

## Source

- Repository: <https://github.com/crawl/crawl>
- Current generated version: `0.34.1`
- Source files:
  - `crawl-ref/source/art-data.txt`
  - `crawl-ref/source/item-prop.cc`

`crawl_service` does not store or expose in-game item description text.

## Generated Module

Run:

```sh
python3 scripts/update_dcss_item_data.py --version 0.34.1
```

The command regenerates `crawl_service/artifacts/generated_dcss_data.py` with:

- `DCSS_UNRANDART_NAMES`: unrandart names parsed from `art-data.txt`.
- `DCSS_ARMOUR_SLOTS`: armour item names mapped to Crawl slot names.

`crawl_service/artifacts/constants.py` imports the generated module and merges it with local compatibility aliases
and scoring constants.
