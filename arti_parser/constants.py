"""DCSS item and artifact data constants."""

from __future__ import annotations

import re

from .dcss_data import (
    DCSS_ARMOUR_ATTRIBUTES,
    DCSS_ARMOUR_SLOTS,
    DCSS_UNRANDART_NAMES,
)

ARTIFACT_DESCRIPTION_RE = re.compile(
    r"^\s+(?P<label>[-+*^A-Za-z][^:]*):\s+(?P<text>.*)$"
)

ARTIFACT_PROPERTY_BLOCK_RE = re.compile(r"\{(?P<properties>[^{}]+)\}\s*$")

ARTIFACT_ENCHANTMENT_RE = re.compile(r"^(?:cursed\s+)?(?P<value>[+-]\d+)\s+")

SIGNED_PROPERTY_RE = re.compile(r"^(?P<key>[A-Za-z][A-Za-z0-9]*)(?P<value>[+-]\d+)$")

INTERNAL_PROPERTY_TOKENS = {
    "Self",
    "Melee",
    "Range",
    "vamp",
    "Dev",
    "Cun",
    "Bglg",
    "Elem",
    "Fort",
    "Comp",
    "Sorc",
}

INTERNAL_PROPERTY_TOKEN_KEYS = {token.casefold() for token in INTERNAL_PROPERTY_TOKENS}

MULTI_WORD_PROPERTY_TOKENS = {
    "holy wrath",
    "sonic wave",
    "manifold assault",
    "coup de grace",
    "freezing cloud",
}

ENCHANTMENT_PREFIX_RE = re.compile(r"^(?:cursed\s+)?[+-]\d+\s+")

RAW_ARTIFACT_TITLE_RE = re.compile(
    r"^(?P<prefix>\s*(?:[A-Za-z] - )?)(?P<title>the .*\{[^{}]+\})(?P<suffix>.*)$"
)

LST_LOCATION_RE = re.compile(r"^\(-?\d+, -?\d+, [^)]+\)$")

PRICE_SUFFIX_RE = re.compile(r"\s+\(\d+ gold\)\s*$")

WORN_SUFFIX_RE = re.compile(r"\s+\([^)]*\)(?=\s*\{)")

INVENTORY_ITEM_RE = re.compile(r"^\s*[A-Za-z] - ")

RAW_ARTIFACT_DESCRIPTION_RE = re.compile(
    r"^\s+(?P<label>[-+*^A-Za-z][^:]*):\s+(?P<text>.*)$"
)

RAW_BRACKET_SUBTYPE_RE = re.compile(r"^\s+\[(?P<subtype>[^]]+)\]\s*$")

RANGED_WEAPONS = {
    "sling",
    "shortbow",
    "longbow",
    "arbalest",
    "hand cannon",
    "triple crossbow",
}

WEAPON_BRANDS = {
    "flaming",
    "flame",
    "freezing",
    "freeze",
    "venom",
    "draining",
    "drain",
    "heavy",
    "speed",
    "antimagic",
    "holy",
    "holy wrath",
    "electrocution",
    "elec",
    "pain",
    "vampirism",
    "protection",
    "protect",
    "spectral",
    "reaping",
    "distortion",
    "chaos",
    "penetration",
    "sunder",
    "shock",
    "anguish",
    "deathbane",
}

SHIELD_ITEMS = {"buckler", "kite shield", "tower shield", "shield"}

HELMET_ITEMS = {"helmet", "hat"}

BOOTS_ITEMS = {"boots", "pair of boots", "barding"}

GLOVES_ITEMS = {"gloves", "pair of gloves"}

CLOAK_ITEMS = {"cloak", "scarf"}

BODY_ARMOUR_MARKERS = (
    "robe",
    "animal skin",
    "leather armour",
    "ring mail",
    "scale mail",
    "chain mail",
    "plate armour",
    "crystal plate armour",
    "troll leather armour",
    "steam dragon scales",
    "acid dragon scales",
    "swamp dragon scales",
    "fire dragon scales",
    "ice dragon scales",
    "pearl dragon scales",
    "storm dragon scales",
    "gold dragon scales",
    "shadow dragon scales",
    "quicksilver dragon scales",
    "hide armour",
    "skin",
)

BASE_SUBTYPE_ATTRIBUTES = {
    "ring of protection": {"AC"},
    "ring of evasion": {"EV"},
    "ring of strength": {"Str"},
    "ring of intelligence": {"Int"},
    "ring of dexterity": {"Dex"},
    "ring of magical power": {"MP"},
    "ring of willpower": {"Will"},
    "ring of protection from fire": {"rF"},
    "ring of protection from cold": {"rC"},
    "ring of poison resistance": {"rPois"},
    "ring of resist corrosion": {"rCorr"},
    "ring of see invisible": {"SInv"},
    "ring of wizardry": {"Wiz"},
    "amulet of reflection": {"Reflect", "SH"},
    "amulet of regeneration": {"Regen"},
    "amulet of magic regeneration": {"RegenMP"},
    "amulet of guardian spirit": {"Spirit"},
    "amulet of the acrobat": {"Acrobat"},
    "amulet of faith": {"Faith"},
    "amulet of dissipation": {"Dissipate"},
    "staff of alchemy": {"Alch", "rPois"},
    "staff of air": {"Air", "rElec"},
    "staff of cold": {"Ice", "rC"},
    "staff of conjuration": {"Conj"},
    "staff of death": {"Necro", "rN"},
    "staff of earth": {"Earth"},
    "staff of fire": {"Fire", "rF"},
    "staff of poison": {"Alch", "rPois"},
}

BASE_ITEM_ATTRIBUTES = {
    **DCSS_ARMOUR_ATTRIBUTES,
    "troll leather armour": ["Regen+"],
    "troll skin": ["Regen+"],
}

UNRANDART_NAMES = {
    "Singing Sword",
    "Wrath of Trog",
    "mace of Variability",
    "partisan of Prune",
    "sword of Power",
    "staff of Olgreb",
    "crystal ball of Wucad Mu",
    "Vampire's Tooth",
    "scythe of Curses",
    "sceptre of Torment",
    "sword of Zonguldrok",
    "sword of Cerebov",
    "orb of Dispater",
    "sceptre of Asmodeus",
    "faerie dragon scales",
    'demon blade "Bloodbane"',
    "scimitar of Flaming Death",
    'eveningstar "Brilliance"',
    'demon blade "Leech"',
    "dagger of Chilly Death",
    'dagger "Morg"',
    'scythe "Finisher"',
    'greatsling "Punk"',
    'longbow "Zephyr"',
    'giant club "Skullcrusher"',
    "glaive of the Guard",
    "zealot's sword",
    'arbalest "Damnation"',
    "sword of the Dread Knight",
    'morningstar "Eos"',
    "spear of the Botono",
    "trident of the Octopus King",
    'mithril axe "Arga"',
    "Elemental Staff",
    'heavy crossbow "Sniper"',
    'longbow "Piercer"',
    "blowgun of the Assassin",
    'lance "Wyrmbane"',
    "Spriggan's Knife",
    "plutonium sword",
    'great mace "Undeadhunter"',
    'whip "Snakebite"',
    "knife of Accuracy",
    "Lehudib's crystal spear",
    "captain's cutlass",
    "storm bow",
    "tower shield of Ignorance",
    "robe of Augmentation",
    "cloak of the Thief",
    'tower shield "Bullseye"',
    "crown of Dyrovepreva",
    "hat of the Bear Spirit",
    "robe of Misfortune",
    "cloak of Flash",
    "hood of the Assassin",
    "Lear's hauberk",
    "skin of Zhor",
    "salamander hide armour",
    "gauntlets of War",
    "shield of Resistance",
    "robe of Folly",
    "Maxwell's patent armour",
    "mask of the Dragon",
    "robe of Night",
    "scales of the Dragon King",
    "hat of the Alchemist",
    "fencer's gloves",
    "cloak of Starlight",
    "ratskin cloak",
    "shield of the Gong",
    "amulet of the Air",
    "ring of Shadows",
    "amulet of Cekugob",
    "amulet of Tranquility",
    "necklace of Bloodlust",
    "ring of the Hare",
    "ring of the Tortoise",
    "ring of the Mage",
    "brooch of Shielding",
    "robe of Clouds",
    "hat of Pondering",
    "obsidian axe",
    "lightning scales",
    "Black Knight's barding",
    "amulet of Vitality",
    "autumn katana",
    'shillelagh "Devastator"',
    "dragonskin cloak",
    "ring of the Octopus King",
    "Axe of Woe",
    "moon troll leather armour",
    "macabre finger necklace",
    "boots of the spider",
    "dark maul",
    "hat of the High Council",
    "arc blade",
    'demon whip "Spellbinder"',
    "lajatang of Order",
    'great mace "Firestarter"',
    "orange crystal plate armour",
    "Majin-Bo",
    'pair of quick blades "Gyre" and "Gimble"',
    "Maxwell's etheric cage",
    "crown of Eternal Torment",
    "robe of Vines",
    "Kryia's mail coat",
    'frozen axe "Frostbite"',
    "armour of Talos",
    "warlock's mirror",
    "amulet of invisibility",
    "Maxwell's thermic engine",
    'demon trident "Rift"',
    "sphere of Battle",
    "Cigotuvi's embrace",
    "seven-league boots",
    "Mad Mage's Maulers",
    "dreamshard necklace",
    "Delatra's gloves",
    "woodcutter's axe",
    "Throatcutter",
    "staff of the Meek",
    'trishula "Condemnation"',
    "amulet of Elemental Vulnerability",
    "mountain boots",
    "Lochaber axe",
    "Hermit's Pendant",
    "slick slippers",
    "Force Lance",
    "consecrated labrys",
    'toga "Victory"',
    "Storm Queen's Shield",
    "dreamdust necklace",
    'hand cannon "Mule"',
    "gloves of the gadgeteer",
    "Charlatan's Orb",
    "justicar's regalia",
    "skull of Zonguldrok",
    "fungal fisticloak",
    "crown of vainglory",
    "scarf of invisibility",
    "swamp witch's dragon scales",
    'athame "Fimbulwinter"',
    "fire dragon occultist's scales",
    "ice dragon arcanist's scales",
}

UNRANDART_NAMES = UNRANDART_NAMES | DCSS_UNRANDART_NAMES
UNRANDART_NAME_KEYS = {
    " ".join(name.casefold().split()) for name in UNRANDART_NAMES
}

SHIELD_ITEMS = SHIELD_ITEMS | {
    name for name, slot in DCSS_ARMOUR_SLOTS.items() if slot == "offhand" and name != "orb"
}
HELMET_ITEMS = HELMET_ITEMS | {
    name for name, slot in DCSS_ARMOUR_SLOTS.items() if slot == "helmet"
}
BOOTS_ITEMS = BOOTS_ITEMS | {
    name for name, slot in DCSS_ARMOUR_SLOTS.items() if slot in {"boots", "barding"}
}
GLOVES_ITEMS = GLOVES_ITEMS | {
    name for name, slot in DCSS_ARMOUR_SLOTS.items() if slot == "gloves"
}
CLOAK_ITEMS = CLOAK_ITEMS | {
    name for name, slot in DCSS_ARMOUR_SLOTS.items() if slot == "cloak"
}
BODY_ARMOUR_MARKERS = tuple(
    sorted(
        set(BODY_ARMOUR_MARKERS)
        | {name for name, slot in DCSS_ARMOUR_SLOTS.items() if slot == "body_armour"}
    )
)

TOP_BASE_ITEMS = {
    "broad axe",
    "eveningstar",
    "demon whip",
    "triple sword",
    "hand cannon",
    "gold dragon scales",
    "crystal plate armour",
}

GOOD_BASE_ITEMS = {
    "cloak",
    "boots",
    "pair of boots",
    "gloves",
    "pair of gloves",
    "helmet",
    "hat",
    "kite shield",
    "tower shield",
    "fire dragon scales",
    "ice dragon scales",
    "pearl dragon scales",
    "storm dragon scales",
    "quicksilver dragon scales",
    "ring",
    "amulet",
}

GOOD_BRANDS = {
    "speed": 10,
    "heavy": 8,
    "electrocution": 8,
    "elec": 8,
    "freezing": 7,
    "freeze": 7,
    "flaming": 7,
    "flame": 7,
    "holy wrath": 8,
    "holy": 8,
    "antimagic": 6,
    "venom": 4,
    "vampirism": 7,
    "spectral": 7,
    "chaos": 4,
}

UTILITY_SCORES = {
    "SInv": 3,
    "Fly": 2,
    "Regen": 5,
    "RegenMP": 5,
    "Rampage": 5,
    "Reflect": 6,
    "Wiz": 5,
    "+Blink": 4,
    "+Inv": 3,
    "Archmagi": 5,
    "Clar": 3,
}

PENALTY_SCORES = {
    "*Slow": 8,
    "^Drain": 7,
    "Fragile": 10,
    "^Fragile": 10,
    "-Tele": 6,
    "-Cast": 8,
    "*Noise": 3,
    "*Rage": 4,
    "^Contam": 4,
    "*Corrode": 5,
    "*Silence": 8,
    "Bane": 4,
    "Harm": 3,
}

SPELL_SCHOOL_KEYS = {
    "Conj",
    "Hexes",
    "Summ",
    "Necro",
    "Tloc",
    "Fire",
    "Ice",
    "Air",
    "Earth",
    "Alch",
    "Forge",
}
