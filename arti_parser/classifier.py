 """Artifact classification helpers for ArtifactDocument construction."""

from __future__ import annotations

from dataclasses import dataclass

from arti_parser.models import ArtifactDocumentAttribute
from arti_parser.constants import (
    BASE_ITEM_ATTRIBUTES,
    BASE_SUBTYPE_ATTRIBUTES,
    BODY_ARMOUR_MARKERS,
    BOOTS_ITEMS,
    CLOAK_ITEMS,
    GLOVES_ITEMS,
    HELMET_ITEMS,
    RANGED_WEAPONS,
    SHIELD_ITEMS,
    WEAPON_BRANDS,
)


@dataclass(frozen=True)
class ArtifactClassification:
    item_class: str
    item_subtype: str
    weapon_subtype: str | None
    armour_slot: str | None
    jewellery_slot: str | None
    brand: str | None
    all_attributes: list[str]
    base_attributes: list[str]
    random_attributes: list[str]


def classify_artifact(
    *,
    attributes: list[ArtifactDocumentAttribute],
    display_name: str,
    base_item: str,
    base_subtype: str | None,
    enchantment: int | None,
) -> ArtifactClassification:
    """Return all classification fields needed for document construction."""

    armour_slot = _armour_slot_from_fields(display_name, base_item)
    item_class = _item_class_from_fields(
        display_name=display_name,
        base_item=base_item,
        base_subtype=base_subtype,
        enchantment=enchantment,
        armour_slot=armour_slot,
    )
    if item_class != "armour":
        armour_slot = None

    visible_attributes = _dedupe([attribute.token for attribute in attributes])
    brand = _brand(display_name, visible_attributes)
    base_attributes = _base_attributes(attributes, base_subtype, base_item)
    all_attributes = _dedupe(
        [
            *visible_attributes,
            *([] if brand is None or brand in visible_attributes else [brand]),
            *base_attributes,
        ]
    )
    return ArtifactClassification(
        item_class=item_class,
        item_subtype=_item_subtype_from_fields(
            item_class=item_class,
            base_item=base_item,
            base_subtype=base_subtype,
            armour_slot=armour_slot,
        ),
        weapon_subtype=_weapon_subtype(base_item, item_class),
        armour_slot=armour_slot,
        jewellery_slot=_jewellery_slot_from_fields(item_class, base_item, base_subtype),
        brand=brand,
        all_attributes=all_attributes,
        base_attributes=base_attributes,
        random_attributes=_random_attributes(all_attributes, base_attributes),
    )


def _base_attributes(
    attributes: list[ArtifactDocumentAttribute],
    base_subtype: str | None,
    base_item: str,
) -> list[str]:
    base_keys = (
        set(BASE_SUBTYPE_ATTRIBUTES.get(base_subtype.lower(), set()))
        if base_subtype
        else set()
    )
    visible_base_attributes = [
        attribute.token for attribute in attributes if attribute.key in base_keys
    ]
    base_item_attributes = BASE_ITEM_ATTRIBUTES.get(base_item.lower(), [])
    return _dedupe([*visible_base_attributes, *base_item_attributes])


def _random_attributes(
    all_attributes: list[str],
    base_attributes: list[str],
) -> list[str]:
    base_attribute_set = set(base_attributes)
    return [token for token in all_attributes if token not in base_attribute_set]


def _brand(display_name: str, tokens: list[str]) -> str | None:
    for token in tokens:
        if token in WEAPON_BRANDS:
            return token

    normalized_display_name = display_name.lower()
    marker = " of "
    if marker not in normalized_display_name:
        return None
    candidate = normalized_display_name.rsplit(marker, 1)[-1].split('"', 1)[0].strip()
    return candidate if candidate in WEAPON_BRANDS else None


def _item_class_from_fields(
    *,
    display_name: str,
    base_item: str,
    base_subtype: str | None,
    enchantment: int | None,
    armour_slot: str | None,
) -> str:
    normalized_base_subtype = (base_subtype or "").lower()
    normalized_base_item = base_item.lower()
    normalized_display_name = display_name.lower()

    if (
        normalized_base_subtype.startswith(("ring of ", "amulet of "))
        or normalized_base_item in {"ring", "amulet"}
    ):
        return "jewellery"
    if "talisman" in normalized_base_subtype or "talisman" in normalized_base_item:
        return "talisman"
    if (
        " staff" in normalized_base_subtype
        or normalized_base_subtype.startswith("staff of ")
        or normalized_base_item.endswith(" staff")
    ):
        return "staff"
    if normalized_base_item in {"skull", "crystal ball", "charlatan's orb"}:
        return "misc"
    if armour_slot is not None:
        return "armour"
    if normalized_display_name.startswith("+") or enchantment is not None:
        return "weapon"
    return "unknown"


def _item_subtype_from_fields(
    *,
    item_class: str,
    base_item: str,
    base_subtype: str | None,
    armour_slot: str | None,
) -> str:
    if base_subtype and item_class in {"jewellery", "staff", "talisman"}:
        return base_subtype
    if item_class == "armour":
        return armour_slot or base_item
    return base_item


def _weapon_subtype(base_item: str, item_class: str) -> str | None:
    if item_class != "weapon":
        return None
    return "ranged" if base_item.lower() in RANGED_WEAPONS else "melee"


def _jewellery_slot_from_fields(
    item_class: str,
    base_item: str,
    base_subtype: str | None,
) -> str | None:
    if item_class != "jewellery":
        return None
    normalized_base_item = base_item.lower()
    if normalized_base_item in {"ring", "amulet"}:
        return normalized_base_item
    normalized_base_subtype = (base_subtype or "").lower()
    if normalized_base_subtype.startswith("ring of "):
        return "ring"
    if normalized_base_subtype.startswith("amulet of "):
        return "amulet"
    return None


def _armour_slot_from_fields(display_name: str, base_item: str) -> str | None:
    normalized_base_item = base_item.lower()
    normalized_display_name = display_name.lower()
    if normalized_base_item in SHIELD_ITEMS:
        return "shield"
    if normalized_base_item in HELMET_ITEMS:
        return "helmet"
    if normalized_base_item in BOOTS_ITEMS or "pair of boots" in normalized_display_name:
        return "boots"
    if normalized_base_item in GLOVES_ITEMS or "pair of gloves" in normalized_display_name or "fisticloak" in normalized_base_item:
        return "gloves"
    if normalized_base_item in CLOAK_ITEMS:
        return "cloak"
    if normalized_base_item == "orb":
        return "orb"
    if any(marker in normalized_base_item for marker in BODY_ARMOUR_MARKERS):
        return "body armour"
    return None


def _dedupe(values: list[str]) -> list[str]:
    seen: set[str] = set()
    deduped: list[str] = []
    for value in values:
        if value in seen:
            continue
        seen.add(value)
        deduped.append(value)
    return deduped
