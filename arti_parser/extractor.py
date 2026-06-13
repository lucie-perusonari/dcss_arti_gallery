"""Extract raw artifact evidence from DCSS morgue txt and lst text."""

from __future__ import annotations

import hashlib
import re
from collections.abc import Iterable, Iterator
from dataclasses import dataclass

from arti_parser.constants import (
    INVENTORY_ITEM_RE,
    LST_LOCATION_RE,
    PRICE_SUFFIX_RE,
    RAW_ARTIFACT_DESCRIPTION_RE,
    RAW_BRACKET_SUBTYPE_RE,
    RAW_ARTIFACT_TITLE_RE,
    WORN_SUFFIX_RE,
)
from arti_parser.classifier import (
    ArtifactClassification,
    classify_artifact,
)
from arti_parser.evaluator import evaluate_artifact_data
from arti_parser.parser import (
    artifact_attributes,
    artifact_base_item,
    artifact_display_name,
    artifact_enchantment_and_base_text,
    is_random_artifact,
)
from arti_parser.models import (
    ArtifactDocument,
    ArtifactDocumentAttribute,
    ArtifactDocumentEvaluation,
    ArtifactDocumentSource,
)
from typing import Protocol


class MorgueRawText(Protocol):
    name: str
    url: str | None
    extension: str
    text: str


ARTIFACT_ID_SLUG_RE = re.compile(r"[^a-z0-9]+")
PLAYER_RE = re.compile(r"morgue-(?P<player>.+?)-\d{8}-\d{6}\.(?:txt|lst)$")


def extract_artifact_documents(raw_text: MorgueRawText) -> list[ArtifactDocument]:
    """Build storage-ready artifact documents from one raw morgue text."""

    documents_by_id: dict[str, ArtifactDocument] = {}
    for raw_artifact in _raw_artifacts(raw_text):
        parsed = _parse_artifact(raw_artifact)
        if not is_random_artifact(
            display_name=parsed.display_name,
            base_subtype=parsed.raw.base_subtype,
        ):
            continue
        classification = classify_artifact(
            attributes=parsed.attributes,
            display_name=parsed.display_name,
            base_item=parsed.base_item,
            base_subtype=parsed.raw.base_subtype,
            enchantment=parsed.enchantment,
        )
        evaluation = evaluate_artifact_data(
            base_item=parsed.base_item,
            enchantment=parsed.enchantment,
            item_class=classification.item_class,
            armour_slot=classification.armour_slot,
            jewellery_slot=classification.jewellery_slot,
            random_attributes=classification.random_attributes,
        )
        document = _artifact_document_from_parts(
            parsed=parsed,
            classification=classification,
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
class _RawArtifact:
    source_name: str | None
    source_url: str | None
    line_no: int
    name: str
    raw_text_block: str
    visible_item_description: list[str]
    visible_description_labels: list[str]
    base_subtype: str | None
    item_location: str | None
    item_source: str | None


@dataclass(frozen=True)
class _ParsedArtifact:
    raw: _RawArtifact
    display_name: str
    enchantment: int | None
    base_item: str
    attributes: list[ArtifactDocumentAttribute]


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


def _raw_artifacts(raw: MorgueRawText) -> Iterator[_RawArtifact]:
    extension = raw.extension.lower()
    if extension == "txt":
        blocks = _txt_blocks(raw.text.splitlines())
    elif extension == "lst":
        blocks = _lst_blocks(raw.text.splitlines())
    else:
        raise ValueError(f"unsupported morgue raw extension: {raw.extension!r}")

    for block in blocks:
        yield _raw_artifact_from_block(
            block,
            source_name=raw.name,
            source_url=raw.url,
        )


def _parse_artifact(raw: _RawArtifact) -> _ParsedArtifact:
    display_name = artifact_display_name(raw.name)
    enchantment, base_text = artifact_enchantment_and_base_text(display_name)
    base_item = artifact_base_item(base_text, raw.base_subtype)
    return _ParsedArtifact(
        raw=raw,
        display_name=display_name,
        enchantment=enchantment,
        base_item=base_item,
        attributes=artifact_attributes(raw.name, raw.visible_item_description),
    )


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


def _raw_artifact_from_block(
    block: _RawBlock,
    *,
    source_name: str | None,
    source_url: str | None,
) -> _RawArtifact:
    descriptions, labels, subtype = _description_lines(block.lines[1:])
    return _RawArtifact(
        source_name=source_name,
        source_url=source_url,
        line_no=block.line_no,
        name=block.title,
        raw_text_block="\n".join(block.lines),
        visible_item_description=descriptions,
        visible_description_labels=labels,
        base_subtype=subtype,
        item_location=block.item_location,
        item_source=block.item_source,
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
    parsed: _ParsedArtifact,
    classification: ArtifactClassification,
    evaluation: ArtifactDocumentEvaluation,
) -> ArtifactDocument:
    source_file = parsed.raw.source_name or ""
    line_no = parsed.raw.line_no
    document_key = "|".join([source_file, str(line_no), parsed.raw.name])
    return ArtifactDocument(
        id=_artifact_id_from_key(parsed.raw.name, document_key),
        name=parsed.raw.name,
        base_item=parsed.base_item,
        base_subtype=parsed.raw.base_subtype,
        item_class=classification.item_class,
        item_subtype=classification.item_subtype,
        weapon_subtype=classification.weapon_subtype,
        armour_slot=classification.armour_slot,
        jewellery_slot=classification.jewellery_slot,
        enchantment=parsed.enchantment,
        brand=classification.brand,
        source=ArtifactDocumentSource(
            player=_player_from_source(source_file),
            file=source_file,
            url=parsed.raw.source_url,
            line=line_no,
        ),
        attributes=parsed.attributes,
        all_attributes=classification.all_attributes,
        base_attributes=classification.base_attributes,
        random_attributes=classification.random_attributes,
        all_attribute_text=", ".join(classification.all_attributes),
        base_attribute_text=", ".join(classification.base_attributes),
        random_attribute_text=", ".join(classification.random_attributes),
        evaluation=evaluation,
        visible_item_description=parsed.raw.visible_item_description,
        visible_description_labels=parsed.raw.visible_description_labels,
        raw_text_block=parsed.raw.raw_text_block,
        item_location=parsed.raw.item_location,
        item_source=parsed.raw.item_source,
    )


def _artifact_id_from_key(name: str, key: str) -> str:
    digest = hashlib.sha1(key.encode("utf-8")).hexdigest()[:10]
    slug = ARTIFACT_ID_SLUG_RE.sub("-", name.lower()).strip("-")
    return f"{slug[:48]}-{digest}" if slug else digest


def _player_from_source(source_file: str) -> str:
    match = PLAYER_RE.search(source_file)
    return match.group("player") if match else ""
