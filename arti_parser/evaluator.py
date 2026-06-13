"""Evaluate random artifact quality from random attribute tokens."""

from __future__ import annotations

from dataclasses import dataclass

from arti_parser.parser import parse_property_token
from arti_parser.constants import (
    GOOD_BASE_ITEMS,
    GOOD_BRANDS,
    PENALTY_SCORES,
    SPELL_SCHOOL_KEYS,
    TOP_BASE_ITEMS,
    UTILITY_SCORES,
)
from arti_parser.models import ArtifactDocumentEvaluation


@dataclass(frozen=True)
class _EvaluatedAttribute:
    token: str
    key: str
    value: int | bool | None

    @property
    def int_value(self) -> int | None:
        return self.value if isinstance(self.value, int) and not isinstance(self.value, bool) else None

    @property
    def is_negative(self) -> bool:
        if self.key in PENALTY_SCORES:
            return True
        return self.int_value is not None and self.int_value < 0


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
    offense = _offense_score(attributes)
    defense = _defense_score(attributes)
    utility = _utility_score(attributes)
    penalty_points = _penalty_points(attributes)
    base_fit = _base_fit_score(
        base_item=base_item,
        enchantment=enchantment,
        item_class=item_class,
        armour_slot=armour_slot,
        jewellery_slot=jewellery_slot,
        attributes=attributes,
    )
    power = min(30, offense + defense + utility)
    synergy = _synergy_score(attributes)
    purity = _clamp(15 - penalty_points - _junk_points(attributes), 0, 15)
    flex = _flex_score(attributes, power, penalty_points)
    timing = 2
    untyped_total = round(base_fit + power + synergy + purity + flex + timing)
    total = _clamp(
        round(untyped_total * _type_multiplier(item_class, armour_slot)),
        0,
        100,
    )
    rarity = _rarity_score(
        enchantment=enchantment,
        item_class=item_class,
        armour_slot=armour_slot,
        attributes=attributes,
        penalty_points=penalty_points,
    )

    return ArtifactDocumentEvaluation(
        total=total,
        practical_score=total,
        rarity_score=rarity,
        offense=offense,
        defense=defense,
        utility=utility,
        penalty=-penalty_points,
        base_fit=base_fit,
        grade=_grade(total),
        luxury_grade=_luxury_grade(total, rarity),
    )


def _base_fit_score(
    *,
    base_item: str,
    enchantment: int | None,
    item_class: str,
    armour_slot: str | None,
    jewellery_slot: str | None,
    attributes: list[_EvaluatedAttribute],
) -> int:
    slot_value = _slot_value(item_class, armour_slot, jewellery_slot)
    normalized_base_item = base_item.lower()
    if normalized_base_item in TOP_BASE_ITEMS:
        base_item_value = 6
    elif normalized_base_item in GOOD_BASE_ITEMS or item_class == "jewellery":
        base_item_value = 4
    elif item_class == "unknown":
        base_item_value = 0
    else:
        base_item_value = 2

    enchant_value = 0 if enchantment is None else min(5, max(0, enchantment))
    brand_value = _brand_value(attributes)
    return _clamp(slot_value + base_item_value + enchant_value + brand_value, 0, 20)


def _slot_value(
    item_class: str,
    armour_slot: str | None,
    jewellery_slot: str | None,
) -> int:
    if item_class == "jewellery":
        return 7 if jewellery_slot == "amulet" else 6
    if item_class == "armour":
        if armour_slot in {"cloak", "boots", "gloves", "helmet"}:
            return 6
        return 5
    if item_class == "weapon":
        return 5
    if item_class in {"staff", "talisman"}:
        return 4
    return 0


def _brand_value(attributes: list[_EvaluatedAttribute]) -> int:
    return min(
        4,
        max((GOOD_BRANDS.get(attribute.token, 0) for attribute in attributes), default=0),
    )


def _offense_score(attributes: list[_EvaluatedAttribute]) -> int:
    score = 0
    for attribute in attributes:
        value = attribute.int_value
        if attribute.key == "Slay" and value and value > 0:
            score += min(16, 4 * value)
        elif attribute.key in {"Str", "Dex", "Int"} and value and value > 0:
            score += min(9, round(1.5 * value))
        elif attribute.token in GOOD_BRANDS:
            score += GOOD_BRANDS.get(attribute.token, 4)
        elif attribute.key in SPELL_SCHOOL_KEYS:
            score += 3
    return score


def _defense_score(attributes: list[_EvaluatedAttribute]) -> int:
    score = 0
    for attribute in attributes:
        value = attribute.int_value
        if attribute.key == "AC" and value and value > 0:
            score += min(12, 2 * value)
        elif attribute.key == "EV" and value and value > 0:
            score += min(12, 2 * value)
        elif attribute.key == "SH" and value and value > 0:
            score += min(9, round(1.5 * value))
        elif attribute.key == "Will" and value and value > 0:
            score += 9 if value >= 2 else 5
        elif attribute.key in {"rF", "rC"} and value and value > 0:
            score += 7 if value >= 2 else 4
        elif attribute.key == "rN" and value and value > 0:
            score += {1: 2, 2: 4}.get(value, 6)
        elif attribute.key == "rElec" and attribute.value is True:
            score += 6
        elif attribute.key == "rPois" and attribute.value is True:
            score += 4
        elif attribute.key == "rCorr" and attribute.value is True:
            score += 3
    return score


def _utility_score(attributes: list[_EvaluatedAttribute]) -> int:
    score = 0
    for attribute in attributes:
        value = attribute.int_value
        if attribute.key == "MP" and value and value > 0:
            score += min(8, value)
        elif attribute.key == "Stlth" and value and value > 0:
            score += 4 if value >= 2 else 2
        elif attribute.value is True:
            score += UTILITY_SCORES.get(attribute.key, 0)
    return score


def _penalty_points(attributes: list[_EvaluatedAttribute]) -> int:
    points = 0
    for attribute in attributes:
        value = attribute.int_value
        if attribute.key in PENALTY_SCORES:
            points += PENALTY_SCORES[attribute.key]
        elif attribute.token in PENALTY_SCORES:
            points += PENALTY_SCORES[attribute.token]
        elif attribute.key == "Will" and value and value < 0:
            points += 6
        elif attribute.key in {"rF", "rC"} and value and value < 0:
            points += 6
        elif attribute.key in {"rPois", "rElec"} and attribute.is_negative:
            points += 5
        elif attribute.key in {"Str", "Dex", "Int"} and value and value < 0:
            points += min(8, abs(value))
        elif attribute.key == "Stlth" and value and value < 0:
            points += 2
    return points


def _junk_points(attributes: list[_EvaluatedAttribute]) -> int:
    spell_school_count = sum(1 for attribute in attributes if attribute.key in SPELL_SCHOOL_KEYS)
    junk = max(0, spell_school_count - 1)
    junk += sum(1 for attribute in attributes if attribute.key in {"Dissipate", "Command", "Wildshape"})
    return min(5, junk)


def _synergy_score(attributes: list[_EvaluatedAttribute]) -> int:
    score = 8
    keys = [attribute.key for attribute in attributes]
    offensive = any(key in {"Slay", "Str", "Dex", "Int"} for key in keys)
    defensive = any(key in {"AC", "EV", "SH", "Will", "rF", "rC", "rElec"} for key in keys)
    utility = any(key in {"Reflect", "Rampage", "Regen", "RegenMP", "Wiz"} for key in keys)
    if offensive and defensive:
        score += 3
    if defensive and utility:
        score += 2
    if offensive and utility:
        score += 2
    if not any(attribute.is_negative for attribute in attributes):
        score += 2
    return _clamp(score, 0, 20)


def _flex_score(
    attributes: list[_EvaluatedAttribute],
    power: int,
    penalty_points: int,
) -> int:
    score = 0
    for attribute in attributes:
        value = attribute.int_value
        if attribute.key == "Slay" and value and value >= 6:
            score += 5
        elif attribute.key in {"Int", "Dex"} and value and value >= 9:
            score += 5
        elif attribute.key == "AC" and value and value >= 8:
            score += 5
        elif attribute.key in {"Str", "EV", "SH", "MP"} and value and value >= 8:
            score += 3
    if power >= 25:
        score += 2
    if penalty_points:
        score += min(3, penalty_points // 4)
    if power < 15:
        score = min(score, 4)
    return _clamp(score, 0, 10)


def _rarity_score(
    *,
    enchantment: int | None,
    item_class: str,
    armour_slot: str | None,
    attributes: list[_EvaluatedAttribute],
    penalty_points: int,
) -> int:
    """Score rare luxury signals, excluding intrinsic base item properties."""

    score = _enchantment_rarity_score(enchantment, item_class, armour_slot)
    parsed_values = {attribute.key: attribute.value for attribute in attributes}

    slay = _int_value(parsed_values.get("Slay"))
    if slay >= 6:
        score += 45
    elif slay >= 4:
        score += 25
    elif slay >= 3 and _high_value_slot(item_class, armour_slot):
        score += 15

    resist_count = _positive_resist_count(parsed_values)
    if resist_count >= 4:
        score += 30
    elif resist_count >= 3:
        score += 20

    if slay >= 3 and _high_value_slot(item_class, armour_slot):
        score += 15

    if item_class == "jewellery" and slay > 0:
        has_stat = any(_int_value(parsed_values.get(key)) > 0 for key in {"Str", "Int", "Dex"})
        has_defense = resist_count > 0 or _int_value(parsed_values.get("Will")) > 0
        if has_stat and has_defense:
            score += 15

    if penalty_points == 0 and score > 0:
        score += 5
    elif penalty_points >= 10:
        score -= 25
    elif penalty_points >= 6:
        score -= 15
    elif penalty_points > 0:
        score -= 10

    return _clamp(score, 0, 100)


def _enchantment_rarity_score(
    enchantment: int | None,
    item_class: str,
    armour_slot: str | None,
) -> int:
    if enchantment is None or enchantment <= 0:
        return 0

    if item_class == "weapon":
        if enchantment >= 9:
            return 30
        if enchantment >= 7:
            return 20
        if enchantment >= 5:
            return 10
        return 0

    if item_class != "armour":
        return 0

    if armour_slot in {"cloak", "boots", "gloves", "helmet"}:
        if enchantment >= 4:
            return 25
        if enchantment >= 2:
            return 10
        return 0

    if enchantment >= 15:
        return 45
    if enchantment >= 10:
        return 35
    if enchantment >= 7:
        return 25
    if enchantment >= 5:
        return 10
    return 0


def _high_value_slot(item_class: str, armour_slot: str | None) -> bool:
    if item_class == "jewellery":
        return True
    return item_class == "armour" and armour_slot in {
        "cloak",
        "boots",
        "gloves",
        "helmet",
    }


def _positive_resist_count(parsed_values: dict[str, int | bool | None]) -> int:
    count = 0
    for key in ("rF", "rC", "rN", "Will"):
        if _int_value(parsed_values.get(key)) > 0:
            count += 1
    for key in ("rElec", "rPois", "rCorr"):
        if parsed_values.get(key) is True:
            count += 1
    return count


def _int_value(value: int | bool | None) -> int:
    return value if isinstance(value, int) and not isinstance(value, bool) else 0


def _type_multiplier(item_class: str, armour_slot: str | None) -> float:
    if item_class == "jewellery":
        return 1.05
    if item_class == "armour":
        if armour_slot in {"cloak", "boots", "gloves", "helmet"}:
            return 1.05
        return 0.98
    if item_class in {"staff", "talisman"}:
        return 0.95
    return 1.0


def _grade(total: int) -> str:
    if total >= 90:
        return "돌품명품"
    if total >= 80:
        return "명품"
    if total >= 65:
        return "실전템"
    if total >= 45:
        return "애매템"
    return "돌품"


def _luxury_grade(practical_score: int, rarity_score: int) -> str:
    if practical_score >= 80 and rarity_score >= 60:
        return "전설급"
    if rarity_score >= 45 and practical_score >= 55:
        return "돌품명품 후보"
    if practical_score >= 65 and rarity_score >= 30:
        return "명품"
    if practical_score >= 65:
        return "실전템"
    if rarity_score >= 30:
        return "희귀 잡템"
    if practical_score >= 45:
        return "애매템"
    return "돌품"


def _evaluated_attributes(tokens: list[str]) -> list[_EvaluatedAttribute]:
    return [_evaluated_attribute(token) for token in tokens]


def _evaluated_attribute(token: str) -> _EvaluatedAttribute:
    key, value = parse_property_token(token)
    return _EvaluatedAttribute(token=token, key=key, value=value)


def _clamp(value: int, minimum: int, maximum: int) -> int:
    return max(minimum, min(maximum, value))
