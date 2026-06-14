"""Convert canonical Mongo artifact documents into Gallery API responses."""

from __future__ import annotations

import hashlib
import re
from typing import Any

from api.models import ArtifactDocument


BRAND_TOKENS = {
    "chaos",
    "distortion",
    "draining",
    "electrocution",
    "flaming",
    "freezing",
    "heavy",
    "holy wrath",
    "pain",
    "protection",
    "speed",
    "venom",
    "vampirism",
    "vorpal",
}
def _equipment_paths(category: str, *paths: str) -> tuple[str, ...]:
    return tuple(f"/tiles/equipment/{category}/{path}.png" for path in paths)


RANDART_WEAPON_TILES = {
    "arbalest": _equipment_paths("artifact", "weapon/ranged/arbalest3"),
    "athame": _equipment_paths("artifact", "weapon/athame3"),
    "bardiche": _equipment_paths("artifact", "weapon/bardiche3"),
    "battleaxe": _equipment_paths("artifact", "weapon/battle_axe3"),
    "broad axe": _equipment_paths("artifact", "weapon/broad_axe3"),
    "club": _equipment_paths("artifact", "weapon/club2"),
    "dagger": _equipment_paths("artifact", "weapon/dagger3"),
    "demon blade": _equipment_paths("artifact", "weapon/demon_blade3"),
    "demon trident": _equipment_paths("artifact", "weapon/demon_trident3"),
    "demon whip": _equipment_paths("artifact", "weapon/demon_whip3"),
    "dire flail": _equipment_paths("artifact", "weapon/dire_flail3"),
    "double sword": _equipment_paths("artifact", "weapon/double_sword3"),
    "eveningstar": _equipment_paths("artifact", "weapon/eveningstar3"),
    "eudemon blade": _equipment_paths("artifact", "weapon/demon_blade3"),
    "executioner's axe": _equipment_paths("artifact", "weapon/executioner_axe3"),
    "falchion": _equipment_paths("artifact", "weapon/falchion3"),
    "flail": _equipment_paths("artifact", "weapon/flail3"),
    "giant club": _equipment_paths("artifact", "weapon/giant_club3"),
    "giant spiked club": _equipment_paths("artifact", "weapon/giant_spiked_club3"),
    "glaive": _equipment_paths("artifact", "weapon/glaive3"),
    "great mace": _equipment_paths("artifact", "weapon/mace_large3"),
    "great sword": _equipment_paths("artifact", "weapon/greatsword3"),
    "halberd": _equipment_paths("artifact", "weapon/halberd3"),
    "hammer": _equipment_paths("artifact", "weapon/hammer3"),
    "hand axe": _equipment_paths("artifact", "weapon/hand_axe3"),
    "hand cannon": _equipment_paths("artifact", "weapon/ranged/hand_cannon3"),
    "lajatang": _equipment_paths("artifact", "weapon/lajatang3"),
    "long sword": _equipment_paths("artifact", "weapon/long_sword3"),
    "longbow": _equipment_paths("artifact", "weapon/ranged/longbow3"),
    "mace": _equipment_paths("artifact", "weapon/mace3"),
    "morningstar": _equipment_paths("artifact", "weapon/morningstar3"),
    "orcbow": _equipment_paths("artifact", "weapon/ranged/orcbow3"),
    "partisan": _equipment_paths("artifact", "weapon/partisan3"),
    "quarterstaff": _equipment_paths("artifact", "weapon/quarterstaff3"),
    "quick blade": _equipment_paths("artifact", "weapon/quickblade3"),
    "rapier": _equipment_paths("artifact", "weapon/rapier3"),
    "sacred scourge": _equipment_paths("artifact", "weapon/demon_whip3"),
    "scimitar": _equipment_paths("artifact", "weapon/scimitar3"),
    "short sword": _equipment_paths("artifact", "weapon/short_sword3"),
    "shortbow": _equipment_paths("artifact", "weapon/ranged/shortbow3"),
    "sling": _equipment_paths("artifact", "weapon/ranged/sling3"),
    "spear": _equipment_paths("artifact", "weapon/spear3"),
    "staff": _equipment_paths("artifact", "weapon/quarterstaff3"),
    "trident": _equipment_paths("artifact", "weapon/trident3"),
    "trishula": _equipment_paths("artifact", "weapon/demon_trident3"),
    "triple crossbow": _equipment_paths("artifact", "weapon/ranged/triple_crossbow2"),
    "triple sword": _equipment_paths("artifact", "weapon/triple_sword3"),
    "war axe": _equipment_paths("artifact", "weapon/war_axe3"),
    "whip": _equipment_paths("artifact", "weapon/bullwhip3"),
}
RANDART_ARMOUR_TILES = {
    "acid dragon scales": _equipment_paths("artifact", "armour/acid_dragon_armour_art"),
    "animal skin": _equipment_paths("artifact", "armour/animal_skin3"),
    "barding": _equipment_paths("artifact", "armour/barding3"),
    "boots": _equipment_paths("artifact", "armour/boots_art1"),
    "pair of boots": _equipment_paths("artifact", "armour/boots_art1"),
    "buckler": _equipment_paths("artifact", "armour/shields/buckler3"),
    "cap": _equipment_paths("artifact", "armour/headgear/hat3"),
    "centaur barding": _equipment_paths("artifact", "armour/barding3"),
    "chain mail": _equipment_paths("artifact", "armour/chain_mail3"),
    "cloak": _equipment_paths("artifact", "armour/cloak4"),
    "crystal plate armour": _equipment_paths("artifact", "armour/crystal_plate3"),
    "fire dragon scales": _equipment_paths("artifact", "armour/fire_dragon_armour_art"),
    "gold dragon scales": _equipment_paths("artifact", "armour/golden_dragon_armour_art"),
    "golden dragon scales": _equipment_paths("artifact", "armour/golden_dragon_armour_art"),
    "gloves": _equipment_paths("artifact", "armour/glove5"),
    "hat": _equipment_paths("artifact", "armour/headgear/hat3"),
    "pair of gloves": _equipment_paths("artifact", "armour/glove5"),
    "helmet": _equipment_paths("artifact", "armour/headgear/helmet_art1"),
    "ice dragon scales": _equipment_paths("artifact", "armour/ice_dragon_armour_art"),
    "kite shield": _equipment_paths("artifact", "armour/shields/kite_shield3"),
    "leather armour": _equipment_paths("artifact", "armour/leather_armour3"),
    "orb": _equipment_paths("artifact", "armour/shields/orb_randart1"),
    "pearl dragon scales": _equipment_paths("artifact", "armour/pearl_dragon_armour_art"),
    "plate armour": _equipment_paths("artifact", "armour/plate3"),
    "quicksilver dragon scales": _equipment_paths("artifact", "armour/quicksilver_dragon_armour_art"),
    "ring mail": _equipment_paths("artifact", "armour/ring_mail3"),
    "robe": _equipment_paths("artifact", "armour/robe_art1"),
    "scale mail": _equipment_paths("artifact", "armour/scale_mail3"),
    "scarf": _equipment_paths("artifact", "armour/scarf3"),
    "shadow dragon scales": _equipment_paths("artifact", "armour/shadow_dragon_armour_art"),
    "shield": _equipment_paths("artifact", "armour/shields/kite_shield3"),
    "steam dragon scales": _equipment_paths("artifact", "armour/steam_dragon_armour_art"),
    "storm dragon scales": _equipment_paths("artifact", "armour/storm_dragon_armour_art"),
    "swamp dragon scales": _equipment_paths("artifact", "armour/swamp_dragon_armour_art"),
    "tower shield": _equipment_paths("artifact", "armour/shields/tower_shield3"),
    "troll leather armour": _equipment_paths("artifact", "armour/troll_leather_armour_art"),
    "troll skin": _equipment_paths("artifact", "armour/troll_leather_armour_art"),
}
RANDART_RING_TILES = _equipment_paths(
    "artifact",
    "ring/randarts/anvil",
    "ring/randarts/blood",
    "ring/randarts/bronze-flower",
    "ring/randarts/dark",
    "ring/randarts/double",
    "ring/randarts/eye",
    "ring/randarts/fire",
    "ring/randarts/flower",
    "ring/randarts/four-colour",
    "ring/randarts/green",
    "ring/randarts/ice",
    "ring/randarts/pink",
    "ring/randarts/red-blue",
    "ring/randarts/snake",
    "ring/randarts/zircon",
)
RANDART_AMULET_TILES = _equipment_paths(
    "artifact",
    "amulet/randarts/azure",
    "amulet/randarts/cluster",
    "amulet/randarts/drop",
    "amulet/randarts/knot",
    "amulet/randarts/scarab",
    "amulet/randarts/skull",
    "amulet/randarts/spider",
    "amulet/randarts/sun",
)
RANDART_STAFF_TILES = _equipment_paths(
    "artifact",
    "staff/staff-artefact1",
    "staff/staff-artefact2",
    "staff/staff-artefact3",
    "staff/staff-artefact4",
    "staff/staff-artefact5",
    "staff/staff-artefact6",
    "staff/staff-artefact7",
)
FALLBACK_RANDART_WEAPON_TILES = _equipment_paths(
    "artifact",
    "weapon/dagger3",
    "weapon/mace3",
    "weapon/long_sword3",
    "weapon/hand_axe3",
    "weapon/spear3",
    "weapon/ranged/shortbow3",
)
FALLBACK_RANDART_ARMOUR_TILES = _equipment_paths(
    "artifact",
    "armour/robe_art1",
    "armour/leather_armour3",
    "armour/plate3",
    "armour/cloak4",
    "armour/glove5",
    "armour/shields/kite_shield3",
)
TALISMAN_TILES = {
    "blade talisman": "/tiles/equipment/artifact/talisman/blade.png",
    "dragon-coil talisman": "/tiles/equipment/artifact/talisman/dragon.png",
    "dragon-blood talisman": "/tiles/equipment/artifact/talisman/dragon.png",
    "eel talisman": "/tiles/equipment/artifact/talisman/eel.png",
    "fortress talisman": "/tiles/equipment/artifact/talisman/fortress.png",
    "granite talisman": "/tiles/equipment/artifact/talisman/statue.png",
    "hive talisman": "/tiles/equipment/artifact/talisman/hive.png",
    "inkwell talisman": "/tiles/equipment/artifact/talisman/inkwell.png",
    "lupine talisman": "/tiles/equipment/artifact/talisman/lupine.png",
    "maw talisman": "/tiles/equipment/artifact/talisman/maw.png",
    "medusa talisman": "/tiles/equipment/artifact/talisman/medusa.png",
    "protean talisman": "/tiles/equipment/artifact/talisman/protean.png",
    "quill talisman": "/tiles/equipment/artifact/talisman/quill.png",
    "riddle talisman": "/tiles/equipment/artifact/talisman/protean.png",
    "rimehorn talisman": "/tiles/equipment/artifact/talisman/rimehorn.png",
    "sanguine talisman": "/tiles/equipment/artifact/talisman/vampire.png",
    "scarab talisman": "/tiles/equipment/artifact/talisman/scarab.png",
    "serpent talisman": "/tiles/equipment/artifact/talisman/snake.png",
    "sphinx talisman": "/tiles/equipment/artifact/talisman/sphinx.png",
    "spider talisman": "/tiles/equipment/artifact/talisman/spider.png",
    "spore talisman": "/tiles/equipment/artifact/talisman/spore.png",
    "statue talisman": "/tiles/equipment/artifact/talisman/statue.png",
    "storm talisman": "/tiles/equipment/artifact/talisman/storm.png",
    "talisman of death": "/tiles/equipment/artifact/talisman/death.png",
    "vampire talisman": "/tiles/equipment/artifact/talisman/vampire.png",
    "wellspring talisman": "/tiles/equipment/artifact/talisman/water.png",
}
MISC_TILES = {
    "charlatan's orb": "/tiles/equipment/artifact/armour/artefact/urand_charlatan.png",
    "crystal ball": "/tiles/equipment/artifact/armour/artefact/urand_wucad_mu.png",
    "skull": "/tiles/equipment/artifact/armour/artefact/urand_skull_of_zonguldrok.png",
}

SIGNED_PROPERTY_RE = re.compile(r"^(?P<key>[A-Za-z][A-Za-z0-9]*)(?P<value>[+-]\d+)$")
DOCUMENT_DESCRIPTION_LINE_RE = re.compile(
    r"^\s*(?P<label>[+*^A-Za-z][^:]*):\s+(?P<text>.*)$"
)


def present_artifact_document(document: dict[str, Any]) -> ArtifactDocument:
    """Build the frontend-facing API read model from one canonical Mongo document."""

    data = dict(document)
    data.pop("_id", None)
    evaluation = data["evaluation"]
    attributes = _display_attributes(data)
    description = _display_description(data, attributes)
    response = {
        "id": data["id"],
        "name": data["name"],
        "baseItem": data["base_item"],
        "type": data["item_class"],
        "subtype": data["item_subtype"],
        "weaponSubtype": data.get("weapon_subtype"),
        "armourSubtype": _armour_subtype(data),
        "armourSlot": data.get("armour_slot"),
        "jewellerySlot": data.get("jewellery_slot"),
        "tile": _tile_for(data),
        "source": {
            "player": data["source"].get("player", ""),
            "url": data["source"].get("url"),
        },
        "allAttributes": data.get("all_attributes", []),
        "baseAttributes": data.get("base_attributes", []),
        "randomAttributes": data.get("random_attributes", []),
        "discovery": _discovery(data),
        "score": evaluation,
        "dcssDescription": description,
    }
    return ArtifactDocument.model_validate(response)


def _display_attributes(document: dict[str, Any]) -> list[dict[str, str | bool]]:
    by_token = {attribute["token"]: attribute for attribute in document.get("attributes", [])}
    description_lines = document.get("visible_item_description", [])
    base_attributes = set(document.get("base_attributes", []))
    display_attributes: list[dict[str, str | bool]] = []
    for token in document.get("all_attributes", []):
        stored = by_token.get(token)
        key, value = _key_value(token)
        if stored:
            key = stored.get("key", key)
            value = stored.get("value", value)
        elif token in base_attributes and _has_visible_attribute_with_key(by_token, key):
            continue
        display_attributes.append(
            {
                "token": token,
                "isBrand": token in BRAND_TOKENS,
                "description": _description_for_token(token, key, value, description_lines),
            }
        )
    return display_attributes


def _armour_subtype(document: dict[str, Any]) -> str | None:
    if document.get("item_class") != "armour":
        return None
    name = str(document.get("name") or "").lower()
    if _looks_like_boots(name):
        return "pair of boots"
    if _looks_like_gloves(name):
        return "pair of gloves"
    return document.get("armour_subtype") or document.get("base_item")


def _has_visible_attribute_with_key(
    by_token: dict[str, dict[str, Any]],
    key: str,
) -> bool:
    for visible_token, attribute in by_token.items():
        visible_key = attribute.get("key")
        if visible_key is None:
            visible_key, _ = _key_value(visible_token)
        if visible_key == key:
            return True
    return False


def _display_description(
    document: dict[str, Any],
    attributes: list[dict[str, str | bool]],
) -> str:
    lines: list[str] = []
    base_subtype = str(document.get("base_subtype") or "").strip()
    if document.get("item_class") == "jewellery" and base_subtype:
        lines.append(f"[{base_subtype}]")
    for attribute in attributes:
        if attribute["isBrand"]:
            continue
        description = str(attribute["description"]).strip()
        if description:
            lines.append(f"{attribute['token']}: {description}")
        else:
            lines.append(attribute["token"])
    return "\n".join(lines)


def _discovery(document: dict[str, Any]) -> dict[str, str | None]:
    first_source = document.get("first_source")
    if not isinstance(first_source, dict):
        first_source = {}
    return {
        "version": first_source.get("version") or document.get("source_version"),
        "datetime": first_source.get("game_ended_at"),
    }


def _key_value(token: str) -> tuple[str, int | bool | None]:
    signed_match = SIGNED_PROPERTY_RE.match(token)
    if signed_match:
        return signed_match.group("key"), int(signed_match.group("value"))

    for key in ("rF", "rC", "rN", "Will"):
        if token.startswith(key) and set(token[len(key) :]) <= {"+", "-"}:
            suffix = token[len(key) :]
            if suffix:
                sign = -1 if suffix[0] == "-" else 1
                return key, sign * len(suffix)

    for key in ("RegenMP", "Regen"):
        if token == f"{key}+":
            return key, True

    return token, True


def _description_for_token(
    token: str,
    key: str,
    value: int | bool | None,
    description_lines: list[str],
) -> str:
    for index, line in enumerate(description_lines):
        match = DOCUMENT_DESCRIPTION_LINE_RE.match(line)
        if not match:
            continue
        label = match.group("label").strip()
        label_key, label_value = _key_value(label)
        if label != token and (label_key != key or label_value != value):
            continue

        parts = [match.group("text").strip()]
        for following in description_lines[index + 1 :]:
            if DOCUMENT_DESCRIPTION_LINE_RE.match(following):
                break
            stripped = following.strip()
            if stripped:
                parts.append(stripped)
        return " ".join(parts).strip()
    return ""


def _tile_for(document: dict[str, Any]) -> str:
    item_class = document["item_class"]
    base_item = document["base_item"].lower()
    subtype = document["item_subtype"].lower()
    name = document["name"].lower()

    if _looks_like_boots(name):
        return _pick_variant(RANDART_ARMOUR_TILES["boots"], document)
    if _looks_like_gloves(name):
        return _pick_variant(RANDART_ARMOUR_TILES["gloves"], document)

    if item_class == "weapon":
        if base_item in RANDART_WEAPON_TILES:
            return _pick_variant(RANDART_WEAPON_TILES[base_item], document)
        return _pick_variant(FALLBACK_RANDART_WEAPON_TILES, document)
    if item_class == "jewellery":
        if document.get("jewellery_slot") == "amulet" or subtype.startswith("amulet of "):
            return _pick_variant(RANDART_AMULET_TILES, document)
        return _pick_variant(RANDART_RING_TILES, document)
    if item_class == "talisman":
        talisman = subtype or base_item
        if talisman in TALISMAN_TILES:
            return TALISMAN_TILES[talisman]
        return "/tiles/equipment/artifact/talisman/statue.png"
    if item_class == "staff":
        return _pick_variant(RANDART_STAFF_TILES, document)
    if item_class == "armour":
        armour_subtype = str(document.get("armour_subtype") or "").lower()
        if base_item == "pair":
            if "pair of boots" in name:
                return _pick_variant(RANDART_ARMOUR_TILES["boots"], document)
            if "pair of gloves" in name:
                return _pick_variant(RANDART_ARMOUR_TILES["gloves"], document)
        variant_key = (
            armour_subtype
            if armour_subtype in RANDART_ARMOUR_TILES
            else base_item if base_item in RANDART_ARMOUR_TILES else subtype
        )
        if variant_key in RANDART_ARMOUR_TILES:
            return _pick_variant(RANDART_ARMOUR_TILES[variant_key], document)
        return _pick_variant(FALLBACK_RANDART_ARMOUR_TILES, document)
    if item_class == "misc":
        if "charlatan" in name:
            return MISC_TILES["charlatan's orb"]
        if "wucad mu" in name:
            return MISC_TILES["crystal ball"]
        if base_item in MISC_TILES:
            return MISC_TILES[base_item]
        return _pick_variant(RANDART_RING_TILES, document)
    return _pick_variant(RANDART_RING_TILES, document)


def _pick_variant(paths: tuple[str, ...], document: dict[str, Any]) -> str:
    seed = document.get("id") or document.get("name") or document.get("raw_text_block") or ""
    digest = hashlib.sha256(str(seed).encode("utf-8")).digest()
    index = int.from_bytes(digest[:4], "big") % len(paths)
    return paths[index]


def _looks_like_boots(name: str) -> bool:
    return "pair of " in name and any(word in name for word in ("boots", "slippers"))


def _looks_like_gloves(name: str) -> bool:
    return "pair of " in name and any(word in name for word in ("gloves", "gauntlets"))
