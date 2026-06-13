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
def _variant_paths(category: str, slug: str, count: int) -> tuple[str, ...]:
    return tuple(f"/tiles/randart/{category}/{slug}-{index}.png" for index in range(1, count + 1))


WEAPON_TILES = {
    "arbalest": "/tiles/arbalest.png",
    "athame": "/tiles/athame.png",
    "battleaxe": "/tiles/battleaxe.png",
    "broad axe": "/tiles/broad-axe.png",
    "dagger": "/tiles/dagger.png",
    "dire flail": "/tiles/dire-flail.png",
    "double sword": "/tiles/double-sword.png",
    "eveningstar": "/tiles/eveningstar.png",
    "executioner's axe": "/tiles/executioners-axe.png",
    "falchion": "/tiles/falchion.png",
    "flail": "/tiles/flail.png",
    "glaive": "/tiles/glaive.png",
    "great mace": "/tiles/great-mace.png",
    "great sword": "/tiles/great-sword.png",
    "halberd": "/tiles/halberd.png",
    "hand axe": "/tiles/hand-axe.png",
    "hand cannon": "/tiles/hand-cannon.png",
    "lajatang": "/tiles/lajatang.png",
    "long sword": "/tiles/long-sword.png",
    "longbow": "/tiles/longbow.png",
    "mace": "/tiles/mace.png",
    "morningstar": "/tiles/morningstar.png",
    "orcbow": "/tiles/orcbow.png",
    "quarterstaff": "/tiles/quarterstaff.png",
    "rapier": "/tiles/rapier.png",
    "scimitar": "/tiles/scimitar.png",
    "short sword": "/tiles/short-sword.png",
    "shortbow": "/tiles/shortbow.png",
    "sling": "/tiles/sling.png",
    "spear": "/tiles/spear.png",
    "trident": "/tiles/trident.png",
    "triple crossbow": "/tiles/triple-crossbow.png",
    "triple sword": "/tiles/triple-sword.png",
    "war axe": "/tiles/war-axe.png",
    "whip": "/tiles/whip.png",
}
RANDART_WEAPON_TILES = {
    "arbalest": _variant_paths("weapon", "arbalest", 3),
    "athame": _variant_paths("weapon", "athame", 3),
    "battleaxe": _variant_paths("weapon", "battleaxe", 3),
    "broad axe": _variant_paths("weapon", "broad-axe", 3),
    "dagger": _variant_paths("weapon", "dagger", 3),
    "dire flail": _variant_paths("weapon", "dire-flail", 3),
    "double sword": _variant_paths("weapon", "double-sword", 3),
    "eveningstar": _variant_paths("weapon", "eveningstar", 3),
    "executioner's axe": _variant_paths("weapon", "executioners-axe", 3),
    "falchion": _variant_paths("weapon", "falchion", 3),
    "flail": _variant_paths("weapon", "flail", 3),
    "glaive": _variant_paths("weapon", "glaive", 3),
    "great mace": _variant_paths("weapon", "great-mace", 3),
    "great sword": _variant_paths("weapon", "great-sword", 3),
    "halberd": _variant_paths("weapon", "halberd", 3),
    "hand axe": _variant_paths("weapon", "hand-axe", 3),
    "hand cannon": _variant_paths("weapon", "hand-cannon", 3),
    "lajatang": _variant_paths("weapon", "lajatang", 3),
    "long sword": _variant_paths("weapon", "long-sword", 3),
    "longbow": _variant_paths("weapon", "longbow", 3),
    "mace": _variant_paths("weapon", "mace", 3),
    "morningstar": _variant_paths("weapon", "morningstar", 3),
    "orcbow": _variant_paths("weapon", "orcbow", 3),
    "quarterstaff": _variant_paths("weapon", "quarterstaff", 3),
    "rapier": _variant_paths("weapon", "rapier", 3),
    "scimitar": _variant_paths("weapon", "scimitar", 3),
    "short sword": _variant_paths("weapon", "short-sword", 3),
    "shortbow": _variant_paths("weapon", "shortbow", 3),
    "sling": _variant_paths("weapon", "sling", 3),
    "spear": _variant_paths("weapon", "spear", 3),
    "trident": _variant_paths("weapon", "trident", 3),
    "triple crossbow": _variant_paths("weapon", "triple-crossbow", 2),
    "triple sword": _variant_paths("weapon", "triple-sword", 3),
    "war axe": _variant_paths("weapon", "war-axe", 3),
}
ARMOUR_TILES = {
    "acid dragon scales": "/tiles/acid-dragon-scales.png",
    "animal skin": "/tiles/robe.png",
    "boots": "/tiles/boots.png",
    "buckler": "/tiles/buckler.png",
    "chain mail": "/tiles/chain-mail.png",
    "cloak": "/tiles/cloak.png",
    "crystal plate armour": "/tiles/crystal-plate-armour.png",
    "fire dragon scales": "/tiles/fire-dragon-scales.png",
    "gold dragon scales": "/tiles/gold-dragon-scales.png",
    "golden dragon scales": "/tiles/golden-dragon-scales.png",
    "gloves": "/tiles/gloves.png",
    "hat": "/tiles/hat.png",
    "helmet": "/tiles/helmet.png",
    "ice dragon scales": "/tiles/ice-dragon-scales.png",
    "kite shield": "/tiles/kite-shield.png",
    "leather armour": "/tiles/leather-armour.png",
    "orb": "/tiles/orb.png",
    "pair of boots": "/tiles/boots.png",
    "pair of gloves": "/tiles/gloves.png",
    "pearl dragon scales": "/tiles/pearl-dragon-scales.png",
    "plate armour": "/tiles/plate-armour.png",
    "quicksilver dragon scales": "/tiles/quicksilver-dragon-scales.png",
    "ring mail": "/tiles/ring-mail.png",
    "robe": "/tiles/robe-randart.png",
    "scale mail": "/tiles/scale-mail.png",
    "scarf": "/tiles/scarf.png",
    "shadow dragon scales": "/tiles/shadow-dragon-scales.png",
    "shield": "/tiles/kite-shield.png",
    "steam dragon scales": "/tiles/steam-dragon-scales.png",
    "storm dragon scales": "/tiles/storm-dragon-scales.png",
    "swamp dragon scales": "/tiles/swamp-dragon-scales.png",
    "tower shield": "/tiles/tower-shield.png",
    "troll leather armour": "/tiles/troll-leather-armour.png",
    "troll skin": "/tiles/troll-leather-armour.png",
}
RANDART_ARMOUR_TILES = {
    "boots": _variant_paths("armour", "boots", 2),
    "pair of boots": _variant_paths("armour", "boots", 2),
    "gloves": _variant_paths("armour", "gloves", 5),
    "pair of gloves": _variant_paths("armour", "gloves", 5),
    "helmet": _variant_paths("armour", "helmet", 3),
    "orb": _variant_paths("armour", "orb", 4),
    "robe": _variant_paths("armour", "robe", 2),
}
RANDART_RING_TILES = _variant_paths("ring", "ring", 15)
RANDART_AMULET_TILES = _variant_paths("amulet", "amulet", 8)
RANDART_STAFF_TILES = _variant_paths("staff", "staff", 7)
TALISMAN_TILES = {
    "blade talisman": "/tiles/talisman-blade.png",
    "dragon-coil talisman": "/tiles/talisman-dragon-coil.png",
    "dragon-blood talisman": "/tiles/talisman-dragon.png",
    "eel talisman": "/tiles/talisman-eel.png",
    "fortress talisman": "/tiles/talisman-fortress.png",
    "granite talisman": "/tiles/talisman-granite.png",
    "hive talisman": "/tiles/talisman-hive.png",
    "inkwell talisman": "/tiles/talisman-inkwell.png",
    "lupine talisman": "/tiles/talisman-lupine.png",
    "maw talisman": "/tiles/talisman-maw.png",
    "medusa talisman": "/tiles/talisman-medusa.png",
    "protean talisman": "/tiles/talisman-protean.png",
    "quill talisman": "/tiles/talisman-quill.png",
    "riddle talisman": "/tiles/talisman-riddle.png",
    "rimehorn talisman": "/tiles/talisman-rimehorn.png",
    "sanguine talisman": "/tiles/talisman-sanguine.png",
    "scarab talisman": "/tiles/talisman-scarab.png",
    "serpent talisman": "/tiles/talisman-serpent.png",
    "sphinx talisman": "/tiles/talisman-sphinx.png",
    "spider talisman": "/tiles/talisman-spider.png",
    "spore talisman": "/tiles/talisman-spore.png",
    "statue talisman": "/tiles/talisman-statue.png",
    "storm talisman": "/tiles/talisman-storm.png",
    "talisman of death": "/tiles/talisman-death.png",
    "vampire talisman": "/tiles/talisman-vampire.png",
    "wellspring talisman": "/tiles/talisman-water.png",
}
MISC_TILES = {
    "charlatan's orb": "/tiles/charlatans-orb.png",
    "crystal ball": "/tiles/crystal-ball-wucad-mu.png",
    "skull": "/tiles/skull-of-zonguldrok.png",
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
    description = _display_description(attributes)
    response = {
        "id": data["id"],
        "name": data["name"],
        "baseItem": data["base_item"],
        "type": data["item_class"],
        "subtype": data["item_subtype"],
        "tile": _tile_for(data),
        "source": {"player": data["source"].get("player", "")},
        "randomAttributes": data.get("random_attributes", []),
        "score": evaluation,
        "dcssDescription": description,
    }
    return ArtifactDocument.model_validate(response)


def _display_attributes(document: dict[str, Any]) -> list[dict[str, str | bool]]:
    by_token = {attribute["token"]: attribute for attribute in document.get("attributes", [])}
    description_lines = document.get("visible_item_description", [])
    display_attributes: list[dict[str, str | bool]] = []
    for token in document.get("all_attributes", []):
        stored = by_token.get(token)
        key, _ = _key_value(token)
        if stored:
            key = stored.get("key", key)
        display_attributes.append(
            {
                "token": token,
                "isBrand": token in BRAND_TOKENS,
                "description": _description_for_token(token, key, description_lines),
            }
        )
    return display_attributes


def _display_description(attributes: list[dict[str, str | bool]]) -> str:
    lines: list[str] = []
    for attribute in attributes:
        if attribute["isBrand"]:
            continue
        description = str(attribute["description"]).strip()
        if description:
            lines.append(f"{attribute['token']}: {description}")
        else:
            lines.append(attribute["token"])
    return "\n".join(lines)


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
    description_lines: list[str],
) -> str:
    for index, line in enumerate(description_lines):
        match = DOCUMENT_DESCRIPTION_LINE_RE.match(line)
        if not match:
            continue
        label = match.group("label").strip()
        label_key, _ = _key_value(label)
        if label != token and label_key != key:
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
        return WEAPON_TILES.get(base_item, _tile_path(base_item))
    if item_class == "jewellery":
        if document.get("jewellery_slot") == "amulet" or subtype.startswith("amulet of "):
            return _pick_variant(RANDART_AMULET_TILES, document)
        return _pick_variant(RANDART_RING_TILES, document)
    if item_class == "talisman":
        talisman = subtype or base_item
        if talisman in TALISMAN_TILES:
            return TALISMAN_TILES[talisman]
        prefix = talisman.removesuffix(" talisman").strip()
        return f"/tiles/talisman-{prefix.replace(' ', '-')}.png" if prefix else "/tiles/talisman-statue.png"
    if item_class == "staff":
        return _pick_variant(RANDART_STAFF_TILES, document)
    if item_class == "armour":
        if base_item == "pair":
            if "pair of boots" in name:
                return _pick_variant(RANDART_ARMOUR_TILES["boots"], document)
            if "pair of gloves" in name:
                return _pick_variant(RANDART_ARMOUR_TILES["gloves"], document)
        variant_key = base_item if base_item in RANDART_ARMOUR_TILES else subtype
        if variant_key in RANDART_ARMOUR_TILES:
            return _pick_variant(RANDART_ARMOUR_TILES[variant_key], document)
        return ARMOUR_TILES.get(base_item) or ARMOUR_TILES.get(subtype) or _tile_path(base_item or subtype or "robe")
    if item_class == "misc":
        if "charlatan" in name:
            return "/tiles/charlatans-orb.png"
        if "wucad mu" in name:
            return "/tiles/crystal-ball-wucad-mu.png"
        if base_item in MISC_TILES:
            return MISC_TILES[base_item]
        return _tile_path(base_item)
    return _pick_variant(RANDART_RING_TILES, document)


def _pick_variant(paths: tuple[str, ...], document: dict[str, Any]) -> str:
    seed = document.get("id") or document.get("name") or document.get("raw_text_block") or ""
    digest = hashlib.sha256(str(seed).encode("utf-8")).digest()
    index = int.from_bytes(digest[:4], "big") % len(paths)
    return paths[index]


def _tile_path(item_name: str) -> str:
    safe_name = item_name.replace("'", "").replace(" ", "-")
    return f"/tiles/{safe_name}.png"


def _looks_like_boots(name: str) -> bool:
    return "pair of " in name and any(word in name for word in ("boots", "slippers"))


def _looks_like_gloves(name: str) -> bool:
    return "pair of " in name and any(word in name for word in ("gloves", "gauntlets"))
