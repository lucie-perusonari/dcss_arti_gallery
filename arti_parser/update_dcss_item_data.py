#!/usr/bin/env python3
"""Generate DCSS item data constants from the official Crawl source tree."""

from __future__ import annotations

import argparse
import re
import subprocess
from pathlib import Path
from pprint import pformat


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_VERSION = "0.34.1"
SOURCE_BASE = "https://raw.githubusercontent.com/crawl/crawl/{version}/crawl-ref/source"
OUTPUT_PATH = ROOT / "arti_parser" / "dcss_data.py"


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--version", default=DEFAULT_VERSION)
    parser.add_argument("--output", type=Path, default=OUTPUT_PATH)
    args = parser.parse_args()

    source = SOURCE_BASE.format(version=args.version)
    art_data = _fetch(f"{source}/art-data.txt")
    item_prop = _fetch(f"{source}/item-prop.cc")

    unrand_names = _parse_unrand_names(art_data)
    armour_slots = _parse_armour_slots(item_prop)

    output = _render_module(
        version=args.version,
        unrand_names=unrand_names,
        armour_slots=armour_slots,
    )
    args.output.write_text(output, encoding="utf-8")


def _fetch(url: str) -> str:
    return subprocess.check_output(["curl", "-L", "--fail", "--silent", url], text=True)


def _parse_unrand_names(text: str) -> set[str]:
    names: set[str] = set()
    for match in re.finditer(r"^NAME:\s*(.+?)\s*$", text, re.MULTILINE):
        name = match.group(1).strip()
        if name.startswith("DUMMY UNRANDART"):
            continue
        names.add(name)
    return names


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


def _render_module(
    *,
    version: str,
    unrand_names: set[str],
    armour_slots: dict[str, str],
) -> str:
    return (
        '"""Generated DCSS item data from the official Crawl source tree."""\n\n'
        "from __future__ import annotations\n\n"
        f"DCSS_UNRANDART_NAMES = {pformat(set(sorted(unrand_names)), width=100)}\n\n"
        "DCSS_ARMOUR_SLOTS = "
        f"{pformat(armour_slots, width=100, sort_dicts=True)}\n"
    )


if __name__ == "__main__":
    main()
