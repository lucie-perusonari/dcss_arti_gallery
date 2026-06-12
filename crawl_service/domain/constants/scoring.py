"""Artifact scoring constants."""

from __future__ import annotations

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

STAT_KEYS = {"Str", "Int", "Dex", "AC", "EV", "SH", "Slay", "MP"}

RESISTANCE_KEYS = {"rF", "rC", "rN", "Will", "rElec", "rPois", "rCorr"}

PENALTY_KEYS = {
    "*Noise",
    "-Tele",
    "*Rage",
    "^Contam",
    "*Corrode",
    "^Drain",
    "*Slow",
    "^Fragile",
    "*Silence",
    "Bane",
    "Harm",
}

BRAND_TOKENS = {
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
}
