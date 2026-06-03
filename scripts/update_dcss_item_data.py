#!/usr/bin/env python3
"""Generate DCSS item data constants from the official Crawl source tree."""

from __future__ import annotations

import argparse
import re
import subprocess
import textwrap
from pathlib import Path
from pprint import pformat


DEFAULT_VERSION = "0.34.1"
SOURCE_BASE = "https://raw.githubusercontent.com/crawl/crawl/{version}/crawl-ref/source"
OUTPUT_PATH = Path("crawl_service/domain/generated_dcss_data.py")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--version", default=DEFAULT_VERSION)
    parser.add_argument("--output", type=Path, default=OUTPUT_PATH)
    args = parser.parse_args()

    source = SOURCE_BASE.format(version=args.version)
    items_text = _fetch(f"{source}/dat/descript/items.txt")
    art_data = _fetch(f"{source}/art-data.txt")
    item_prop = _fetch(f"{source}/item-prop.cc")

    descriptions = _parse_item_descriptions(items_text)
    unrand_names = _parse_unrand_names(art_data)
    equipment, armour_slots = _parse_equipment_names(item_prop, descriptions)

    output = _render_module(
        version=args.version,
        descriptions=descriptions,
        unrand_names=unrand_names,
        equipment=equipment,
        armour_slots=armour_slots,
    )
    args.output.write_text(output, encoding="utf-8")


def _fetch(url: str) -> str:
    return subprocess.check_output(["curl", "-L", "--fail", "--silent", url], text=True)


def _parse_item_descriptions(text: str) -> dict[str, str]:
    entries: dict[str, str] = {}
    for block in text.split("%%%%"):
        lines = [line.rstrip() for line in block.strip().splitlines()]
        lines = [line for line in lines if line.strip()]
        if not lines:
            continue
        key = lines[0].strip().casefold()
        if key.startswith("#"):
            continue
        entries[key] = " ".join(line.strip() for line in lines[1:]).strip()
    return dict(sorted(entries.items()))


def _parse_unrand_names(text: str) -> set[str]:
    names: set[str] = set()
    for match in re.finditer(r"^NAME:\s*(.+?)\s*$", text, re.MULTILINE):
        name = match.group(1).strip()
        if name.startswith("DUMMY UNRANDART"):
            continue
        names.add(name)
    return names


def _parse_equipment_names(
    item_prop: str,
    descriptions: dict[str, str],
) -> tuple[dict[str, tuple[str, ...]], dict[str, str]]:
    armour_slots = _parse_armour_slots(item_prop)
    armour = set(armour_slots)
    weapons = set(_parse_prop_array_names(item_prop, "Weapon_prop"))
    staves = {f"staff of {name}" for name in _parse_prop_array_names(item_prop, "Staff_prop")}
    talismans = {name for name in descriptions if name.endswith(" talisman")}
    jewellery = {
        name
        for name in descriptions
        if name.startswith("ring of ") or name.startswith("amulet of ")
    }
    return {
        "armour": tuple(sorted(_without_removed(armour))),
        "jewellery": tuple(sorted(jewellery)),
        "staff": tuple(sorted(_without_removed(staves))),
        "talisman": tuple(sorted(talismans)),
        "weapon": tuple(sorted(_without_removed(weapons))),
    }, dict(sorted(armour_slots.items()))


def _parse_armour_slots(text: str) -> dict[str, str]:
    start = text.rfind("static const", 0, text.index("Armour_prop"))
    brace_start = text.index("{", start)
    brace_end = _matching_brace(text, brace_start)
    body = text[brace_start + 1 : brace_end]
    slots: dict[str, str] = {}
    for record in _top_level_records(body):
        name_match = re.search(r'\{\s*[A-Z0-9_]+,\s*"([^"]+)"', record)
        slot_match = re.search(r"\b(SLOT_[A-Z_]+)\b", record)
        if name_match and slot_match:
            name = name_match.group(1)
            if not name.startswith(("old ", "removed ")):
                slots[name] = slot_match.group(1).removeprefix("SLOT_").lower()
    return slots


def _top_level_records(body: str) -> list[str]:
    records: list[str] = []
    start: int | None = None
    depth = 0
    for index, char in enumerate(body):
        if char == "{":
            if depth == 0:
                start = index
            depth += 1
        elif char == "}":
            depth -= 1
            if depth == 0 and start is not None:
                records.append(body[start : index + 1])
                start = None
    return records


def _parse_prop_array_names(text: str, array_name: str) -> list[str]:
    array_index = text.index(array_name)
    start = text.rfind("static const", 0, array_index)
    if start == -1:
        raise ValueError(f"could not find declaration for {array_name}")
    brace_start = text.index("{", start)
    brace_end = _matching_brace(text, brace_start)
    body = text[brace_start:brace_end]
    return re.findall(r'\{\s*[A-Z0-9_]+,\s*"([^"]+)"', body)


def _matching_brace(text: str, start: int) -> int:
    depth = 0
    for index in range(start, len(text)):
        if text[index] == "{":
            depth += 1
        elif text[index] == "}":
            depth -= 1
            if depth == 0:
                return index
    raise ValueError("unbalanced C++ initializer braces")


def _without_removed(names: set[str]) -> set[str]:
    return {name for name in names if not name.startswith(("old ", "removed "))}


def _render_module(
    *,
    version: str,
    descriptions: dict[str, str],
    unrand_names: set[str],
    equipment: dict[str, tuple[str, ...]],
    armour_slots: dict[str, str],
) -> str:
    return (
        '"""Generated DCSS item data from the official Crawl source tree."""\n\n'
        "from __future__ import annotations\n\n"
        f'DCSS_DATA_VERSION = "{version}"\n'
        'DCSS_DATA_SOURCE = "https://github.com/crawl/crawl"\n\n'
        f"DCSS_ITEM_FLAVOUR_TEXT = {pformat(descriptions, width=100, sort_dicts=True)}\n\n"
        f"DCSS_UNRANDART_NAMES = {pformat(set(sorted(unrand_names)), width=100)}\n\n"
        "DCSS_EQUIPMENT_NAMES = "
        f"{pformat(equipment, width=100, sort_dicts=True)}\n\n"
        "DCSS_ARMOUR_SLOTS = "
        f"{pformat(armour_slots, width=100, sort_dicts=True)}\n"
    )


if __name__ == "__main__":
    main()
