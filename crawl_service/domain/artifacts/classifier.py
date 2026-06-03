"""Build document-friendly random artifact objects from parsed artifacts."""

from __future__ import annotations

from crawl_service.domain.artifacts.types import ArtifactInfo, RandomArtifact
from crawl_service.domain.constants import (
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


def build_random_artifact(artifact_info: ArtifactInfo) -> RandomArtifact:
    """Build a document-friendly random artifact from parsed artifact info."""

    all_attributes = _dedupe([attribute.token for attribute in artifact_info.attributes])
    brand = _brand(artifact_info, all_attributes)
    if brand and brand not in all_attributes:
        all_attributes.append(brand)

    base_attributes = _base_attributes(artifact_info)
    all_attributes = _dedupe([*all_attributes, *base_attributes])
    random_attributes = [
        token for token in all_attributes if token not in set(base_attributes)
    ]

    item_class = _item_class(artifact_info)
    weapon_subtype = None
    if item_class == "weapon":
        weapon_subtype = (
            "ranged" if artifact_info.base_item.lower() in RANGED_WEAPONS else "melee"
        )
    armour_slot = _armour_slot(artifact_info) if item_class == "armour" else None
    jewellery_slot = _jewellery_slot(artifact_info) if item_class == "jewellery" else None
    item_subtype = _item_subtype(artifact_info, item_class)

    return RandomArtifact(
        artifact_info=artifact_info,
        name=artifact_info.raw_info.artifact_name,
        base_item=artifact_info.base_item,
        enchantment=artifact_info.enchantment,
        brand=brand,
        base_subtype=artifact_info.base_subtype,
        item_class=item_class,
        item_subtype=item_subtype,
        weapon_subtype=weapon_subtype,
        armour_slot=armour_slot,
        jewellery_slot=jewellery_slot,
        all_attributes=all_attributes,
        base_attributes=base_attributes,
        random_attributes=random_attributes,
        all_attribute_text=_attribute_text(all_attributes),
        base_attribute_text=_attribute_text(base_attributes),
        random_attribute_text=_attribute_text(random_attributes),
    )


def _base_attributes(artifact_info: ArtifactInfo) -> list[str]:
    base_keys = (
        set(BASE_SUBTYPE_ATTRIBUTES.get(artifact_info.base_subtype.lower(), set()))
        if artifact_info.base_subtype
        else set()
    )
    visible_base_attributes = [
        attribute.token
        for attribute in artifact_info.attributes
        if attribute.key in base_keys
    ]
    base_item_attributes = BASE_ITEM_ATTRIBUTES.get(artifact_info.base_item.lower(), [])
    return _dedupe([*visible_base_attributes, *base_item_attributes])


def _brand(artifact_info: ArtifactInfo, tokens: list[str]) -> str | None:
    for token in tokens:
        if token in WEAPON_BRANDS:
            return token

    display_name = artifact_info.display_name.lower()
    marker = " of "
    if marker not in display_name:
        return None
    candidate = display_name.rsplit(marker, 1)[-1].split('"', 1)[0].strip()
    return candidate if candidate in WEAPON_BRANDS else None


def _item_class(artifact_info: ArtifactInfo) -> str:
    base_subtype = (artifact_info.base_subtype or "").lower()
    base_item = artifact_info.base_item.lower()
    name = artifact_info.display_name.lower()

    if base_subtype.startswith(("ring of ", "amulet of ")) or base_item in {"ring", "amulet"}:
        return "jewellery"
    if "talisman" in base_subtype or "talisman" in base_item:
        return "talisman"
    if " staff" in base_subtype or base_subtype.startswith("staff of ") or base_item.endswith(" staff"):
        return "staff"
    if base_item in {"skull", "crystal ball", "charlatan's orb"}:
        return "misc"
    if _armour_slot(artifact_info) is not None:
        return "armour"
    if name.startswith("+") or artifact_info.enchantment is not None:
        return "weapon"
    return "unknown"


def _item_subtype(artifact_info: ArtifactInfo, item_class: str) -> str:
    if artifact_info.base_subtype and item_class in {"jewellery", "staff", "talisman"}:
        return artifact_info.base_subtype
    if item_class == "armour":
        return _armour_slot(artifact_info) or artifact_info.base_item
    return artifact_info.base_item


def _armour_slot(artifact_info: ArtifactInfo) -> str | None:
    base_item = artifact_info.base_item.lower()
    name = artifact_info.display_name.lower()
    if base_item in SHIELD_ITEMS:
        return "shield"
    if base_item in HELMET_ITEMS:
        return "helmet"
    if base_item in BOOTS_ITEMS or "pair of boots" in name:
        return "boots"
    if base_item in GLOVES_ITEMS or "pair of gloves" in name or "fisticloak" in base_item:
        return "gloves"
    if base_item in CLOAK_ITEMS:
        return "cloak"
    if base_item == "orb":
        return "orb"
    if any(marker in base_item for marker in BODY_ARMOUR_MARKERS):
        return "body armour"
    return None


def _jewellery_slot(artifact_info: ArtifactInfo) -> str | None:
    base_item = artifact_info.base_item.lower()
    if base_item in {"ring", "amulet"}:
        return base_item
    base_subtype = (artifact_info.base_subtype or "").lower()
    if base_subtype.startswith("ring of "):
        return "ring"
    if base_subtype.startswith("amulet of "):
        return "amulet"
    return None


def _attribute_text(attributes: list[str]) -> str:
    return ", ".join(attributes)


def _dedupe(values: list[str]) -> list[str]:
    seen: set[str] = set()
    deduped: list[str] = []
    for value in values:
        if value in seen:
            continue
        seen.add(value)
        deduped.append(value)
    return deduped
