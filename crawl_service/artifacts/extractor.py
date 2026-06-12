"""Extract raw artifact evidence from DCSS morgue txt and lst text."""

from __future__ import annotations

import hashlib
import re
from collections.abc import Iterable, Iterator
from dataclasses import dataclass

from crawl_service.artifacts.constants import (
    INVENTORY_ITEM_RE,
    LST_LOCATION_RE,
    PRICE_SUFFIX_RE,
    RAW_ARTIFACT_DESCRIPTION_RE,
    RAW_BRACKET_SUBTYPE_RE,
    RAW_ARTIFACT_TITLE_RE,
    WORN_SUFFIX_RE,
)
from crawl_service.artifacts.classifier import (
    artifact_all_attributes,
    artifact_armour_slot,
    artifact_base_attributes,
    artifact_brand,
    artifact_item_class,
    artifact_item_subtype,
    artifact_jewellery_slot,
    artifact_random_attributes,
    artifact_weapon_subtype,
    attribute_text,
)
from crawl_service.artifacts.evaluator import evaluate_artifact_data
from crawl_service.artifacts.filter import is_random_artifact
from crawl_service.artifacts.info_parser import (
    artifact_attributes,
    artifact_base_item,
    artifact_display_name,
    artifact_enchantment_and_base_text,
)
from crawl_service.artifacts.models import (
    ArtifactDocument,
    ArtifactDocumentAttribute,
    ArtifactDocumentEvaluation,
    ArtifactDocumentSource,
)
from crawl_service.morgue.types import MorgueRawText


ARTIFACT_ID_SLUG_RE = re.compile(r"[^a-z0-9]+")
PLAYER_RE = re.compile(r"morgue-(?P<player>.+?)-\d{8}-\d{6}\.(?:txt|lst)$")


def extract_artifact_documents(raw_text: MorgueRawText) -> list[ArtifactDocument]:
    """Build storage-ready artifact documents from one raw morgue text."""

    documents_by_id: dict[str, ArtifactDocument] = {}
    for raw_info in get_artifact_raw_info(raw_text):
        display_name = artifact_display_name(raw_info["artifact_name"])
        enchantment, base_text = artifact_enchantment_and_base_text(display_name)
        base_subtype = raw_info.get("bracket_subtype")
        base_item = artifact_base_item(base_text, base_subtype)
        attributes = artifact_attributes(
            raw_info["artifact_name"],
            raw_info["visible_item_description"],
        )
        if not is_random_artifact(
            display_name=display_name,
            base_subtype=base_subtype,
        ):
            continue
        all_attributes = artifact_all_attributes(
            attributes,
            display_name,
            base_subtype,
            base_item,
        )
        base_attributes = artifact_base_attributes(
            attributes,
            base_subtype,
            base_item,
        )
        random_attributes = artifact_random_attributes(
            all_attributes,
            base_attributes,
        )
        item_class = artifact_item_class(
            display_name,
            base_item,
            base_subtype,
            enchantment,
        )
        armour_slot = artifact_armour_slot(item_class, display_name, base_item)
        jewellery_slot = artifact_jewellery_slot(
            item_class,
            base_item,
            base_subtype,
        )
        evaluation = evaluate_artifact_data(
            base_item=base_item,
            enchantment=enchantment,
            item_class=item_class,
            armour_slot=armour_slot,
            jewellery_slot=jewellery_slot,
            random_attributes=random_attributes,
        )
        document = _artifact_document_from_parts(
            raw_info=raw_info,
            attributes=attributes,
            name=raw_info["artifact_name"],
            base_item=base_item,
            base_subtype=base_subtype,
            item_class=item_class,
            item_subtype=artifact_item_subtype(
                item_class,
                base_item,
                base_subtype,
                display_name,
            ),
            weapon_subtype=artifact_weapon_subtype(base_item, item_class),
            armour_slot=armour_slot,
            jewellery_slot=jewellery_slot,
            enchantment=enchantment,
            brand=artifact_brand(display_name, all_attributes),
            all_attributes=all_attributes,
            base_attributes=base_attributes,
            random_attributes=random_attributes,
            all_attribute_text=attribute_text(all_attributes),
            base_attribute_text=attribute_text(base_attributes),
            random_attribute_text=attribute_text(random_attributes),
            evaluation=evaluation,
        )
        documents_by_id[document.id] = document
    return sorted(
        documents_by_id.values(),
        key=lambda document: document.evaluation.total,
        reverse=True,
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


def get_artifact_raw_info(raw: MorgueRawText) -> list[dict]:
    """Convert one fetched morgue text into artifact raw info objects."""

    extension = raw.extension.lower()
    if extension == "txt":
        artifacts = get_txt_artifact_raw_info(raw.text)
    elif extension == "lst":
        artifacts = get_lst_artifact_raw_info(raw.text)
    else:
        raise ValueError(f"unsupported morgue raw extension: {raw.extension!r}")

    return [_with_source(artifact, raw) for artifact in artifacts]


def get_txt_artifact_raw_info(text: str) -> list[dict]:
    """Extract randart raw blocks from a morgue txt character dump."""

    return [_raw_info_from_block(block) for block in _txt_blocks(text.splitlines())]


def get_lst_artifact_raw_info(text: str) -> list[dict]:
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


def _with_source(raw_info: dict, raw: MorgueRawText) -> dict:
    return {
        **raw_info,
        "source_name": raw.name,
        "source_url": raw.url,
    }


def _raw_info_from_block(block: _RawBlock) -> dict:
    descriptions, labels, subtype = _description_lines(block.lines[1:])
    return {
        "source_name": None,
        "source_url": None,
        "line_no": block.line_no,
        "raw_text_block": "\n".join(block.lines),
        "artifact_name": block.title,
        "item_location": block.item_location,
        "item_source": block.item_source,
        "visible_item_description": descriptions,
        "visible_description_labels": labels,
        "bracket_subtype": subtype,
    }


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
        subtype_match = RAW_BRACKET_SUBTYPE_RE.match(line)
        if subtype_match:
            subtype = subtype_match.group("subtype")
            current_description = False
            continue

        description_match = RAW_ARTIFACT_DESCRIPTION_RE.match(line)
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


def _artifact_document_from_parts(
    *,
    raw_info: dict,
    attributes: list[ArtifactDocumentAttribute],
    name: str,
    base_item: str,
    base_subtype: str | None,
    item_class: str,
    item_subtype: str,
    weapon_subtype: str | None,
    armour_slot: str | None,
    jewellery_slot: str | None,
    enchantment: int | None,
    brand: str | None,
    all_attributes: list[str],
    base_attributes: list[str],
    random_attributes: list[str],
    all_attribute_text: str,
    base_attribute_text: str,
    random_attribute_text: str,
    evaluation: ArtifactDocumentEvaluation,
) -> ArtifactDocument:
    source_file = raw_info.get("source_name") or ""
    line_no = raw_info["line_no"]
    document_key = "|".join([source_file, str(line_no), name])
    return ArtifactDocument(
        id=_artifact_id_from_key(name, document_key),
        name=name,
        base_item=base_item,
        base_subtype=base_subtype,
        item_class=item_class,
        item_subtype=item_subtype,
        weapon_subtype=weapon_subtype,
        armour_slot=armour_slot,
        jewellery_slot=jewellery_slot,
        enchantment=enchantment,
        brand=brand,
        source=ArtifactDocumentSource(
            player=_player_from_source(source_file),
            file=source_file,
            url=raw_info.get("source_url"),
            line=line_no,
        ),
        attributes=attributes,
        all_attributes=all_attributes,
        base_attributes=base_attributes,
        random_attributes=random_attributes,
        all_attribute_text=all_attribute_text,
        base_attribute_text=base_attribute_text,
        random_attribute_text=random_attribute_text,
        evaluation=evaluation,
        visible_item_description=raw_info["visible_item_description"],
        visible_description_labels=raw_info["visible_description_labels"],
        raw_text_block=raw_info["raw_text_block"],
        item_location=raw_info.get("item_location"),
        item_source=raw_info.get("item_source"),
    )


def _artifact_id_from_key(name: str, key: str) -> str:
    digest = hashlib.sha1(key.encode("utf-8")).hexdigest()[:10]
    slug = ARTIFACT_ID_SLUG_RE.sub("-", name.lower()).strip("-")
    return f"{slug[:48]}-{digest}" if slug else digest


def _player_from_source(source_file: str) -> str:
    match = PLAYER_RE.search(source_file)
    return match.group("player") if match else ""
