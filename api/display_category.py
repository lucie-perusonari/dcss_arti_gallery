"""Display category fallback rules for artifact filtering."""

from __future__ import annotations

from typing import Any


WEAPON_CATEGORY_ORDER = [
    "short blades",
    "long blades",
    "axes",
    "maces & flails",
    "polearms",
    "staves",
    "ranged",
    "other weapons",
]

WEAPON_CATEGORIES: dict[str, str] = {
    "arbalest": "ranged",
    "athame": "short blades",
    "bardiche": "polearms",
    "battleaxe": "axes",
    "broad axe": "axes",
    "club": "maces & flails",
    "dagger": "short blades",
    "demon blade": "long blades",
    "demon trident": "polearms",
    "demon whip": "maces & flails",
    "dire flail": "maces & flails",
    "double sword": "long blades",
    "eudemon blade": "long blades",
    "eveningstar": "maces & flails",
    "executioner's axe": "axes",
    "falchion": "long blades",
    "flail": "maces & flails",
    "giant club": "maces & flails",
    "giant spiked club": "maces & flails",
    "glaive": "polearms",
    "great mace": "maces & flails",
    "great sword": "long blades",
    "halberd": "polearms",
    "hammer": "maces & flails",
    "hand axe": "axes",
    "hand cannon": "ranged",
    "lajatang": "staves",
    "long sword": "long blades",
    "longbow": "ranged",
    "mace": "maces & flails",
    "morningstar": "maces & flails",
    "orcbow": "ranged",
    "partisan": "polearms",
    "quarterstaff": "staves",
    "quick blade": "short blades",
    "rapier": "short blades",
    "sacred scourge": "maces & flails",
    "scimitar": "long blades",
    "short sword": "short blades",
    "shortbow": "ranged",
    "sling": "ranged",
    "spear": "polearms",
    "staff": "staves",
    "trident": "polearms",
    "triple crossbow": "ranged",
    "triple sword": "long blades",
    "trishula": "polearms",
    "war axe": "axes",
    "whip": "maces & flails",
}

KNOWN_WEAPON_ITEMS = sorted(WEAPON_CATEGORIES)


def display_category_for_document(document: dict[str, Any]) -> str:
    """Return the current frontend-facing category for an artifact document."""

    stored = str(document.get("display_category") or "").strip()
    if stored:
        return stored

    item_class = str(document.get("item_class") or "").strip().lower()
    item_subtype = str(document.get("item_subtype") or "").strip().lower()
    base_item = str(document.get("base_item") or "").strip().lower()

    if item_class == "weapon":
        return (
            WEAPON_CATEGORIES.get(item_subtype)
            or WEAPON_CATEGORIES.get(base_item)
            or ("ranged" if document.get("weapon_subtype") == "ranged" else "other weapons")
        )
    if item_class == "armour":
        return str(document.get("armour_slot") or item_subtype or base_item).strip()
    if item_class == "jewellery":
        jewellery_slot = str(document.get("jewellery_slot") or "").strip().lower()
        if jewellery_slot in {"ring", "amulet"}:
            return jewellery_slot
        if base_item == "amulet" or item_subtype.startswith("amulet of "):
            return "amulet"
        return "ring"
    return item_subtype or base_item


def display_category_filter(display_category: str) -> dict[str, Any]:
    """Build a Mongo filter for the fallback display category."""

    category = display_category.strip().lower()
    if not category:
        return {}

    filters = [
        {"display_category": category},
        _weapon_category_filter(category),
        _armour_category_filter(category),
        _jewellery_category_filter(category),
        _subtype_category_filter(category),
    ]
    return {"$or": [condition for condition in filters if condition]}


def display_category_sort_key(item_class: str, category: str) -> tuple[int, str]:
    if item_class == "weapon":
        try:
            return (WEAPON_CATEGORY_ORDER.index(category), category)
        except ValueError:
            return (len(WEAPON_CATEGORY_ORDER), category)
    return (0, category)


def _weapon_category_filter(category: str) -> dict[str, Any]:
    if category == "ranged":
        return {"item_class": "weapon", "$or": [{"weapon_subtype": "ranged"}, *_weapon_item_filters(category)]}
    if category == "other weapons":
        return {
            "item_class": "weapon",
            "weapon_subtype": {"$ne": "ranged"},
            "item_subtype": {"$nin": KNOWN_WEAPON_ITEMS},
            "base_item": {"$nin": KNOWN_WEAPON_ITEMS},
        }
    item_filters = _weapon_item_filters(category)
    return {"item_class": "weapon", "$or": item_filters} if item_filters else {}


def _weapon_item_filters(category: str) -> list[dict[str, Any]]:
    item_names = [name for name, item_category in WEAPON_CATEGORIES.items() if item_category == category]
    return [
        {"item_subtype": {"$in": item_names}},
        {"base_item": {"$in": item_names}},
    ]


def _armour_category_filter(category: str) -> dict[str, Any]:
    return {
        "item_class": "armour",
        "$or": [
            {"armour_slot": category},
            {"item_subtype": category},
            {"base_item": category},
        ],
    }


def _jewellery_category_filter(category: str) -> dict[str, Any]:
    if category == "amulet":
        return {
            "item_class": "jewellery",
            "$or": [
                {"jewellery_slot": "amulet"},
                {"base_item": "amulet"},
                {"item_subtype": {"$regex": "^amulet of ", "$options": "i"}},
            ],
        }
    if category == "ring":
        return {
            "item_class": "jewellery",
            "$or": [
                {"jewellery_slot": "ring"},
                {"base_item": "ring"},
                {"item_subtype": {"$regex": "^ring of ", "$options": "i"}},
            ],
        }
    return {"item_class": "jewellery", "jewellery_slot": category}


def _subtype_category_filter(category: str) -> dict[str, Any]:
    return {
        "item_class": {"$in": ["staff", "talisman", "misc"]},
        "$or": [
            {"item_subtype": category},
            {"base_item": category},
        ],
    }
