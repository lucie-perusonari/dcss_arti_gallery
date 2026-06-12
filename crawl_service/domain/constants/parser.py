"""Parser and document constants for crawl service artifact text."""

from __future__ import annotations

import re

RAW_ARTIFACT_TITLE_RE = re.compile(
    r"^(?P<prefix>\s*(?:[A-Za-z] - )?)(?P<title>the .*\{[^{}]+\})(?P<suffix>.*)$"
)

LST_LOCATION_RE = re.compile(r"^\(-?\d+, -?\d+, [^)]+\)$")

PRICE_SUFFIX_RE = re.compile(r"\s+\(\d+ gold\)\s*$")

WORN_SUFFIX_RE = re.compile(r"\s+\([^)]*\)(?=\s*\{)")

INVENTORY_ITEM_RE = re.compile(r"^\s*[A-Za-z] - ")

ARTIFACT_DESCRIPTION_RE = re.compile(r"^\s+(?P<label>[+*^A-Za-z][^:]*):\s+(?P<text>.*)$")

BRACKET_SUBTYPE_RE = re.compile(r"^\s+\[(?P<subtype>[^]]+)\]\s*$")

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

ARTIFACT_ID_SLUG_RE = re.compile(r"[^a-z0-9]+")

PLAYER_RE = re.compile(r"morgue-(?P<player>.+?)-\d{8}-\d{6}\.(?:txt|lst)$")

DOCUMENT_DESCRIPTION_LINE_RE = re.compile(r"^\s*(?P<label>[-+*^A-Za-z][^:]*):\s*(?P<text>.*)$")

DISPLAY_PROPERTY_BLOCK_RE = re.compile(r"\s*\{[^{}]*\}\s*$")
