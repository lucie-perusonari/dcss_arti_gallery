"""Raw randart extraction helpers for DCSS morgue txt and lst text."""

from __future__ import annotations

from collections.abc import Iterable, Iterator
from dataclasses import dataclass, replace

from crawl_service.domain.artifacts.types import ArtifactRawInfo, ArtifactRawTextInput
from crawl_service.domain.constants import (
    ARTIFACT_DESCRIPTION_RE,
    BRACKET_SUBTYPE_RE,
    INVENTORY_ITEM_RE,
    LST_LOCATION_RE,
    PRICE_SUFFIX_RE,
    RAW_ARTIFACT_TITLE_RE,
    WORN_SUFFIX_RE,
)


@dataclass
class _RawBlock:
    line_no: int
    title: str
    lines: list[str]
    item_location: str | None = None
    item_source: str | None = None


@dataclass(frozen=True)
class _LstContext:
    level: str | None = None
    location: str | None = None
    shop: str | None = None

    def update(self, line: str) -> "_LstContext":
        stripped = line.strip()
        if line.startswith("Level "):
            return _LstContext(level=stripped, location=stripped, shop=None)
        if line.startswith("[Shop]"):
            location = f"{self.level} {stripped}" if self.level else stripped
            return _LstContext(level=self.level, location=location, shop=stripped)
        if LST_LOCATION_RE.match(line):
            return _LstContext(level=self.level, location=stripped, shop=None)
        return self


def get_artifact_raw_info(raw: ArtifactRawTextInput) -> list[ArtifactRawInfo]:
    """Convert one parser-ready raw text object into artifact raw info objects."""

    extension = raw.extension.lower()
    if extension == "txt":
        artifacts = get_txt_artifact_raw_info(raw.text)
    elif extension == "lst":
        artifacts = get_lst_artifact_raw_info(raw.text)
    else:
        raise ValueError(f"unsupported morgue raw extension: {raw.extension!r}")

    return [
        replace(artifact, source_name=raw.name, source_url=raw.url)
        for artifact in artifacts
    ]


def get_txt_artifact_raw_info(text: str) -> list[ArtifactRawInfo]:
    """Extract randart raw blocks from a morgue txt character dump."""

    return [_raw_info_from_block(block) for block in _txt_blocks(text.splitlines())]


def get_lst_artifact_raw_info(text: str) -> list[ArtifactRawInfo]:
    """Extract randart raw blocks from a DCSS lst file."""

    return [_raw_info_from_block(block) for block in _lst_blocks(text.splitlines())]


def _txt_blocks(lines: list[str]) -> Iterator[_RawBlock]:
    for line_no, block_lines in _txt_inventory_item_blocks(lines):
        title = _candidate_title(block_lines[0])
        if title is None:
            continue
        yield _RawBlock(
            line_no=line_no,
            title=title,
            lines=block_lines,
            item_source=_extract_txt_item_source(block_lines),
        )


def _lst_blocks(lines: list[str]) -> Iterator[_RawBlock]:
    context = _LstContext()
    current: _RawBlock | None = None

    for line_no, line in enumerate(lines, start=1):
        if _is_lst_context_line(line):
            if current is not None:
                yield current
                current = None
            context = context.update(line)
            continue

        title = _candidate_title(line)
        if title is not None:
            if current is not None:
                yield current
            current = _RawBlock(
                line_no=line_no,
                title=title,
                lines=[line],
                item_location=context.location,
                item_source=context.shop,
            )
            continue

        if current is not None:
            if _is_lst_block_boundary(line):
                yield current
                current = None
                continue
            current.lines.append(line)

    if current is not None:
        yield current


def _candidate_title(line: str) -> str | None:
    match = RAW_ARTIFACT_TITLE_RE.match(line)
    if not match:
        return None
    title = match.group("title").strip()
    title = WORN_SUFFIX_RE.sub("", title)
    return PRICE_SUFFIX_RE.sub("", title).strip()


def _is_lst_block_boundary(line: str) -> bool:
    if _is_lst_context_line(line):
        return True
    if line.startswith("[") and line.endswith("]"):
        return True
    if line.startswith("  ") and not line.startswith("    "):
        return True
    return False


def _is_lst_context_line(line: str) -> bool:
    return (
        line.startswith("Level ")
        or line.startswith("[Shop]")
        or bool(LST_LOCATION_RE.match(line))
    )


def _raw_info_from_block(block: _RawBlock) -> ArtifactRawInfo:
    descriptions, labels, subtype = _description_lines(block.lines[1:])
    return ArtifactRawInfo(
        source_name=None,
        source_url=None,
        line_no=block.line_no,
        raw_text_block="\n".join(block.lines),
        artifact_name=block.title,
        item_location=block.item_location,
        item_source=block.item_source,
        visible_item_description=descriptions,
        visible_description_labels=labels,
        bracket_subtype=subtype,
    )


def _txt_inventory_item_blocks(lines: list[str]) -> list[tuple[int, list[str]]]:
    inventory = _txt_inventory_lines(lines)
    blocks: list[tuple[int, list[str]]] = []
    current_line_no: int | None = None
    current_block: list[str] = []

    for line_no, line in inventory:
        if INVENTORY_ITEM_RE.match(line):
            if current_line_no is not None:
                blocks.append((current_line_no, current_block))
            current_line_no = line_no
            current_block = [line]
            continue

        if current_line_no is not None:
            current_block.append(line)

    if current_line_no is not None:
        blocks.append((current_line_no, current_block))

    return blocks


def _txt_inventory_lines(lines: list[str]) -> list[tuple[int, str]]:
    try:
        inventory_start = lines.index("Inventory:") + 1
    except ValueError:
        return []

    inventory_lines: list[tuple[int, str]] = []
    for index, line in enumerate(lines[inventory_start:], start=inventory_start + 1):
        if line.startswith("   Skills:"):
            break
        inventory_lines.append((index, line))

    return inventory_lines


def _extract_txt_item_source(block_lines: list[str]) -> str | None:
    for line in block_lines[1:]:
        stripped = line.strip()
        if stripped.startswith("(") and stripped.endswith(")"):
            return stripped[1:-1].strip()
    return None


def _description_lines(
    block_lines: Iterable[str],
) -> tuple[list[str], list[str], str | None]:
    descriptions: list[str] = []
    labels: list[str] = []
    subtype: str | None = None
    current_description = False

    for line in block_lines:
        subtype_match = BRACKET_SUBTYPE_RE.match(line)
        if subtype_match:
            subtype = subtype_match.group("subtype")
            current_description = False
            continue

        description_match = ARTIFACT_DESCRIPTION_RE.match(line)
        if description_match:
            labels.append(description_match.group("label").strip())
            descriptions.append(line.rstrip())
            current_description = True
            continue

        if current_description and line.startswith(" ") and line.strip():
            descriptions.append(line.rstrip())
            continue

        current_description = False

    return descriptions, labels, subtype
