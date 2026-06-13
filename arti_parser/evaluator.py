"""Evaluate random artifact value from item metadata and random attributes."""

from __future__ import annotations

from dataclasses import dataclass
from itertools import combinations

from arti_parser.dcss_data import DCSS_ARMOUR_STATS, DCSS_WEAPON_STATS
from arti_parser.models import ArtifactDocumentEvaluation
from arti_parser.parser import parse_property_token


@dataclass(frozen=True)
class _EvaluatedAttribute:
    token: str
    key: str
    value: int | bool | None

    @property
    def int_value(self) -> int | None:
        return self.value if isinstance(self.value, int) and not isinstance(self.value, bool) else None


@dataclass(frozen=True)
class _ScoreParts:
    base: int = 0
    offense: float = 0
    defense: float = 0
    utility: float = 0
    penalty: float = 0

    @property
    def positive_total(self) -> float:
        return self.base + self.offense + self.defense + self.utility

    @property
    def total(self) -> int:
        return max(0, round(self.positive_total - self.penalty))


WEAPON_BASE_SCORES = {
    "club": 2,
    "dagger": 5,
    "whip": 7,
    "mace": 9,
    "falchion": 9,
    "short sword": 10,
    "hand axe": 10,
    "spear": 11,
    "trident": 12,
    "flail": 12,
    "rapier": 12,
    "sling": 12,
    "quarterstaff": 14,
    "long sword": 15,
    "war axe": 16,
    "scimitar": 17,
    "morningstar": 18,
    "halberd": 18,
    "battleaxe": 20,
    "great sword": 20,
    "great mace": 21,
    "orcbow": 21,
    "lajatang": 22,
    "arbalest": 24,
    "longbow": 24,
    "broad axe": 25,
    "eveningstar": 26,
    "demon whip": 28,
    "demon trident": 28,
    "double sword": 28,
    "hand cannon": 30,
    "executioner's axe": 32,
    "triple sword": 33,
    "triple crossbow": 34,
}

ARMOUR_BASE_AC = {
    "robe": 2,
    "animal skin": 2,
    "leather armour": 3,
    "troll leather armour": 4,
    "troll skin": 4,
    "ring mail": 5,
    "scale mail": 6,
    "chain mail": 8,
    "plate armour": 10,
    "crystal plate armour": 14,
    "steam dragon scales": 5,
    "acid dragon scales": 6,
    "swamp dragon scales": 7,
    "fire dragon scales": 8,
    "ice dragon scales": 9,
    "pearl dragon scales": 10,
    "storm dragon scales": 10,
    "shadow dragon scales": 10,
    "gold dragon scales": 12,
    "golden dragon scales": 12,
    "quicksilver dragon scales": 9,
    "buckler": 3,
    "kite shield": 8,
    "shield": 8,
    "tower shield": 13,
}

SPEED_BRANDS = {"speed"}
NORMAL_ATTACK_BRANDS = {
    "elec",
    "electrocution",
    "heavy",
    "flame",
    "flaming",
    "freeze",
    "freezing",
    "holy",
    "holy wrath",
    "vamp",
    "vampirism",
    "antimagic",
    "spect",
    "spectral",
    "drain",
    "draining",
    "venom",
    "pain",
}
WEAK_ATTACK_BRANDS = {"chaos", "protect", "protection", "distort", "distortion"}

MAJOR_RESIST_KEYS = {"rF", "rC", "Will"}
DIRECT_DAMAGE_SCHOOLS = {"Fire", "Ice", "Earth", "Alch", "Air"}
ELEMENTAL_SCHOOLS = {"Fire", "Ice", "Earth", "Air"}
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
HIGH_UTILITY_KEYS = {"SInv", "Reflect", "Wiz", "RegenMP"}
LOW_UTILITY_KEYS = {
    "Fly",
    "+Blink",
    "+Inv",
    "Rampage",
    "Clar",
    "Wildshape",
    "Chemistry",
    "Acrobat",
    "Spirit",
}

COMMON_BOOLEAN_PENALTIES = {
    "*Slow": 36,
    "-Tele": 36,
    "*Silence": 36,
    "Bane": 24,
    "Harm": 24,
    "-Cast": 20,
    "*Corrode": 18,
    "*Rage": 24,
    "^Fragile": 8,
    "Fragile": 8,
    "^Drain": 8,
    "^Contam": 8,
    "*Noise": 5,
}


def evaluate_artifact_data(
    *,
    base_item: str,
    enchantment: int | None,
    item_class: str,
    armour_slot: str | None,
    jewellery_slot: str | None,
    random_attributes: list[str],
) -> ArtifactDocumentEvaluation:
    """Evaluate artifact fields into the document evaluation shape."""

    attributes = _evaluated_attributes(random_attributes)
    normalized_class = item_class.lower()
    if normalized_class == "weapon":
        parts = _weapon_score(base_item, enchantment, attributes)
    elif normalized_class == "staff":
        parts = _staff_score(attributes)
    elif normalized_class == "armour":
        parts = _armour_score(base_item, enchantment, armour_slot, attributes)
    elif normalized_class == "jewellery":
        parts = _jewellery_score(attributes)
    else:
        parts = _fallback_score(attributes)

    total = parts.total
    return ArtifactDocumentEvaluation(
        total=total,
        practical_score=total,
        rarity_score=0,
        offense=round(parts.offense),
        defense=round(parts.defense),
        utility=round(parts.utility),
        penalty=-round(parts.penalty),
        base_fit=round(parts.base),
        grade="unclassified",
        luxury_grade=None,
    )


def _weapon_score(
    base_item: str,
    enchantment: int | None,
    attributes: list[_EvaluatedAttribute],
) -> _ScoreParts:
    base = _weapon_base_score(base_item)
    offense = _enchantment_score(enchantment)
    defense = 0.0
    utility = 0.0
    penalty = 0.0

    for attribute in attributes:
        key = attribute.key
        value = attribute.int_value
        if attribute.token in SPEED_BRANDS:
            offense += 30
        elif attribute.token in NORMAL_ATTACK_BRANDS:
            offense += 15
        elif attribute.token in WEAK_ATTACK_BRANDS:
            offense += 8
        elif key == "Slay" and value:
            offense += _positive(value) * 9
            penalty += _negative_abs(value) * 9
        elif key in {"Str", "Dex"} and value:
            offense += _positive(value) * 3
            penalty += _negative_abs(value) * 4
        elif key == "Int" and value:
            penalty += _negative_abs(value)
        elif key == "Regen" and attribute.value is True:
            utility += 12
        else:
            common = _common_positive_score(attribute)
            if _common_positive_category(attribute) in {"defense", "utility"}:
                if common:
                    if _common_positive_category(attribute) == "defense":
                        defense += common * 0.5
                    else:
                        utility += common * 0.5
            penalty += _common_penalty_score(attribute)

    return _ScoreParts(base=base, offense=offense, defense=defense, utility=utility, penalty=penalty)


def _staff_score(attributes: list[_EvaluatedAttribute]) -> _ScoreParts:
    offense = 0.0
    defense = 0.0
    utility = 0.0
    penalty = 0.0
    schools: set[str] = set()

    for attribute in attributes:
        key = attribute.key
        value = attribute.int_value
        if key == "Archmagi" and attribute.value is True:
            utility += 30
        elif key == "Wiz" and attribute.value is True:
            utility += 24
        elif key == "RegenMP" and attribute.value is True:
            utility += 20
        elif key == "Int" and value:
            utility += _positive(value) * 3
            penalty += _staff_int_penalty(value)
        elif key == "MP" and value:
            utility += _positive(value)
            penalty += _negative_abs(value)
        elif key in SPELL_SCHOOL_KEYS:
            schools.add(key)
        else:
            category = _common_positive_category(attribute)
            score = _common_positive_score(attribute)
            if category == "defense":
                defense += score
            elif category == "utility":
                utility += score
            penalty += _staff_penalty_score(attribute)

    offense += _staff_school_score(schools)
    return _ScoreParts(offense=offense, defense=defense, utility=utility, penalty=penalty)


def _armour_score(
    base_item: str,
    enchantment: int | None,
    armour_slot: str | None,
    attributes: list[_EvaluatedAttribute],
) -> _ScoreParts:
    base = _armour_base_score(base_item, armour_slot)
    defense = _enchantment_score(enchantment)
    offense = 0.0
    utility = 0.0
    penalty = 0.0
    resist_count = 0

    for attribute in attributes:
        key = attribute.key
        value = attribute.int_value
        if key == "Slay" and value:
            offense += _positive(value) * 9
            penalty += _negative_abs(value) * 9
        elif key in {"AC", "EV", "SH"} and value:
            defense += _positive(value) * 3
            penalty += _negative_abs(value) * 3
        elif key in {"Str", "Dex", "Int"} and value:
            utility += _positive(value)
            penalty += _negative_abs(value) * 2
        else:
            score = _common_positive_score(attribute)
            category = _common_positive_category(attribute)
            if category == "defense":
                defense += score
                if _is_resistance(attribute):
                    resist_count += 1
            elif category == "utility":
                utility += _armour_utility_score(attribute)
            penalty += _common_penalty_score(attribute)

    defense += _resistance_bundle_bonus(resist_count)
    return _ScoreParts(base=base, offense=offense, defense=defense, utility=utility, penalty=penalty)


def _jewellery_score(attributes: list[_EvaluatedAttribute]) -> _ScoreParts:
    offense = 0.0
    defense = 0.0
    utility = 0.0
    penalty = 0.0

    for attribute in attributes:
        key = attribute.key
        value = attribute.int_value
        if key == "Slay" and value:
            offense += _positive(value) * 3
            penalty += _negative_abs(value) * 3
        elif key in {"AC", "EV", "SH"} and value:
            defense += _positive(value) * 3
            penalty += _negative_abs(value) * 3
        elif key in {"Str", "Dex", "Int"} and value:
            utility += _positive(value) * 2
            penalty += _negative_abs(value) * 2
        else:
            category = _common_positive_category(attribute)
            score = _common_positive_score(attribute)
            if category == "defense":
                defense += score
            elif category == "utility":
                utility += score
            penalty += _common_penalty_score(attribute)

    return _ScoreParts(offense=offense, defense=defense, utility=utility, penalty=penalty)


def _fallback_score(attributes: list[_EvaluatedAttribute]) -> _ScoreParts:
    offense = 0.0
    defense = 0.0
    utility = 0.0
    penalty = 0.0
    for attribute in attributes:
        key = attribute.key
        value = attribute.int_value
        if key == "Slay" and value:
            offense += _positive(value) * 3
            penalty += _negative_abs(value) * 3
        elif key in {"AC", "EV", "SH"} and value:
            defense += _positive(value) * 3
            penalty += _negative_abs(value) * 3
        elif key in {"Str", "Dex", "Int"} and value:
            utility += _positive(value) * 2
            penalty += _negative_abs(value) * 2
        else:
            category = _common_positive_category(attribute)
            score = _common_positive_score(attribute)
            if category == "defense":
                defense += score
            elif category == "utility":
                utility += score
            penalty += _common_penalty_score(attribute)
    return _ScoreParts(offense=offense, defense=defense, utility=utility, penalty=penalty)


def _enchantment_score(enchantment: int | None) -> int:
    return 0 if enchantment is None else enchantment * 3


def _armour_base_score(base_item: str, armour_slot: str | None) -> int:
    normalized = _normalize(base_item)
    if normalized in DCSS_ARMOUR_STATS:
        return int(DCSS_ARMOUR_STATS[normalized]["ac"]) * 3
    if normalized in ARMOUR_BASE_AC:
        return ARMOUR_BASE_AC[normalized] * 3
    if armour_slot in {"cloak", "boots", "gloves", "helmet"}:
        return 15
    if armour_slot in {"orb", "cloak"} or normalized == "scarf":
        return 10
    return 10


def _weapon_base_score(base_item: str) -> int:
    normalized = _normalize(base_item)
    stats = DCSS_WEAPON_STATS.get(normalized)
    if not stats:
        return WEAPON_BASE_SCORES.get(normalized, 8)
    damage = int(stats["damage"])
    speed = int(stats["speed"])
    min_delay = max(3, speed // 2)
    speed_adjustment = max(0, 10 - min_delay) * 2
    return max(2, round(damage * 1.4 + speed_adjustment))


def _common_positive_score(attribute: _EvaluatedAttribute) -> int:
    value = attribute.int_value
    key = attribute.key
    if key in MAJOR_RESIST_KEYS and value and value > 0:
        return value * 12
    if key == "rN" and value and value > 0:
        return value * 6
    if key in {"rElec", "rPois", "rCorr"} and attribute.value is True:
        return 12
    if key in {"AC", "EV", "SH"} and value and value > 0:
        return value * 3
    if key == "Regen" and attribute.value is True:
        return 24
    if key in HIGH_UTILITY_KEYS and attribute.value is True:
        return 18
    if key in LOW_UTILITY_KEYS and attribute.value is True:
        return 6
    if key == "MP" and value and value > 0:
        return value
    return 0


def _common_positive_category(attribute: _EvaluatedAttribute) -> str | None:
    key = attribute.key
    if key in {*MAJOR_RESIST_KEYS, "rN", "rElec", "rPois", "rCorr", "AC", "EV", "SH"}:
        return "defense"
    if key in {"Regen", *HIGH_UTILITY_KEYS, *LOW_UTILITY_KEYS, "MP"}:
        return "utility"
    return None


def _armour_utility_score(attribute: _EvaluatedAttribute) -> int:
    key = attribute.key
    if key == "Regen":
        return 16
    if key == "SInv":
        return 6
    if key == "Rampage":
        return 6
    if key in {"+Inv", "+Blink"}:
        return 4
    if key == "MP":
        return _positive(attribute.int_value)
    return 0


def _common_penalty_score(attribute: _EvaluatedAttribute) -> int:
    key = attribute.key
    value = attribute.int_value
    if attribute.token in COMMON_BOOLEAN_PENALTIES:
        return COMMON_BOOLEAN_PENALTIES[attribute.token]
    if key in {"rF", "rC", "Will", "rElec", "rPois", "rCorr"} and value and value < 0:
        return abs(value) * 12
    if key == "rN" and value and value < 0:
        return abs(value) * 6
    if key in {"Str", "Dex", "Int"} and value and value < 0:
        return abs(value) * 2
    if key == "Stlth" and value and value < 0:
        return abs(value) * 2
    return 0


def _staff_penalty_score(attribute: _EvaluatedAttribute) -> int:
    if attribute.token == "*Silence":
        return 40
    if attribute.token == "-Cast":
        return 30
    return _common_penalty_score(attribute)


def _staff_int_penalty(value: int | None) -> int:
    if value is None or value >= 0:
        return 0
    return round(abs(value) * 8 / 3)


def _staff_school_score(schools: set[str]) -> int:
    if not schools:
        return 0
    score = len(schools) * 5
    direct = schools & DIRECT_DAMAGE_SCHOOLS
    if "Conj" in schools and direct:
        score += len(direct) * 18
    elemental = schools & ELEMENTAL_SCHOOLS
    if len(elemental) >= 2:
        score += len(list(combinations(elemental, 2))) * 8

    combo_count = 0
    for school in schools:
        if school == "Conj":
            continue
        if school in direct or school in elemental:
            continue
        combo_count += 1
    if len(schools) > 1:
        score += max(0, len(schools) - 2 + combo_count) * 4
    return score


def _resistance_bundle_bonus(resist_count: int) -> int:
    bonus = 0
    if resist_count >= 2:
        bonus += 8
    if resist_count >= 3:
        bonus += 8
    return bonus


def _is_resistance(attribute: _EvaluatedAttribute) -> bool:
    return attribute.key in {"rF", "rC", "Will", "rN", "rElec", "rPois", "rCorr"}


def _evaluated_attributes(tokens: list[str]) -> list[_EvaluatedAttribute]:
    return [_evaluated_attribute(token) for token in tokens]


def _evaluated_attribute(token: str) -> _EvaluatedAttribute:
    key, value = parse_property_token(token)
    return _EvaluatedAttribute(token=token, key=key, value=value)


def _positive(value: int | None) -> int:
    return value if value is not None and value > 0 else 0


def _negative_abs(value: int | None) -> int:
    return abs(value) if value is not None and value < 0 else 0


def _normalize(value: str) -> str:
    return " ".join(value.casefold().split())
