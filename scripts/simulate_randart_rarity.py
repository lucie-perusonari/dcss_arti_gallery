#!/usr/bin/env python3
"""Simulate DCSS randart rarity signals against the local luxury evaluator."""

from __future__ import annotations

import argparse
import json
import random
import sys
from collections import Counter
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from statistics import mean
from types import SimpleNamespace
from typing import Callable, TypeVar

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from crawl_service.domain.evaluation.evaluator import evaluate_artifact


REPORT_PATH = Path("crawl_service/docs/research/randart-corpus/rarity_report.md")
RESULTS_PATH = Path("crawl_service/docs/research/randart-corpus/rarity_simulation.json")
SOURCE_VERSION = "0.34.1"
SOURCE_URL = (
    "https://github.com/crawl/crawl/blob/0.34.1/"
    "crawl-ref/source/artefact.cc"
)


@dataclass(frozen=True)
class PropData:
    name: str
    weight: int
    good: Callable[[random.Random], int] | None
    bad: Callable[[random.Random], int] | None
    max_dup: int = 0
    odds_inc: int = 0


@dataclass(frozen=True)
class ItemProfile:
    key: str
    label: str
    item_class: str
    base_item: str
    enchantment: int | None
    armour_slot: str | None = None
    jewellery_slot: str | None = None
    weapon_subtype: str | None = None
    robe: bool = False
    aux_type: str | None = None
    staff: bool = False


def _good_stat(rng: random.Random) -> int:
    return 1 + rng.randrange(2) + (1 if rng.randrange(4) == 0 else 0)


def _bad_stat(rng: random.Random) -> int:
    return -2 - rng.randrange(4)


def _good_res(_rng: random.Random) -> int:
    return 1


def _bad_res(_rng: random.Random) -> int:
    return -1


def _good_hpmp(rng: random.Random) -> int:
    value = rng.randint(4, 9)
    if rng.randrange(3) == 0:
        value += rng.randint(1, 3)
    return value


def _bad_hpmp(rng: random.Random) -> int:
    return -_good_hpmp(rng)


PROPS: dict[str, PropData] = {
    "Str": PropData("Str", 100, _good_stat, _bad_stat, 7, 1),
    "Int": PropData("Int", 100, _good_stat, _bad_stat, 7, 1),
    "Dex": PropData("Dex", 100, _good_stat, _bad_stat, 7, 1),
    "rF": PropData("rF", 60, _good_res, _bad_res, 2, 4),
    "rC": PropData("rC", 60, _good_res, _bad_res, 2, 4),
    "rElec": PropData("rElec", 55, lambda _rng: 1, None),
    "rPois": PropData("rPois", 55, lambda _rng: 1, None),
    "rN": PropData("rN", 55, _good_res, None, 2, 4),
    "Will": PropData("Will", 50, _good_res, _bad_res, 2, 4),
    "SInv": PropData("SInv", 30, lambda _rng: 1, None),
    "+Inv": PropData("+Inv", 15, lambda _rng: 1, None),
    "Fly": PropData("Fly", 15, lambda _rng: 1, None),
    "+Blink": PropData("+Blink", 15, lambda _rng: 1, None),
    "*Noise": PropData("*Noise", 30, None, lambda _rng: 2),
    "-Tele": PropData("-Tele", 25, None, lambda _rng: 1),
    "*Rage": PropData("*Rage", 30, None, lambda _rng: 20),
    "^Contam": PropData("^Contam", 20, None, lambda _rng: 1),
    "Slay": PropData("Slay", 30, lambda rng: 2 + rng.randrange(2), lambda rng: -(2 + rng.randrange(5)), 3, 2),
    "Stlth": PropData("Stlth", 40, _good_res, _bad_res),
    "MP": PropData("MP", 15, _good_hpmp, _bad_hpmp),
    "Regen": PropData("Regen", 35, lambda _rng: 1, None),
    "rCorr": PropData("rCorr", 40, lambda _rng: 1, None),
    "*Corrode": PropData("*Corrode", 25, None, lambda _rng: 1),
    "^Drain": PropData("^Drain", 25, None, lambda _rng: 1),
    "*Slow": PropData("*Slow", 25, None, lambda _rng: 1),
    "^Fragile": PropData("^Fragile", 30, None, lambda _rng: 1),
    "Harm": PropData("Harm", 25, lambda _rng: 1, None),
    "Rampage": PropData("Rampage", 25, lambda _rng: 1, None),
    "Archmagi": PropData("Archmagi", 40, lambda _rng: 1, None),
    "Conj": PropData("Conj", 20, lambda _rng: 1, None),
    "Hexes": PropData("Hexes", 20, lambda _rng: 1, None),
    "Summ": PropData("Summ", 20, lambda _rng: 1, None),
    "Necro": PropData("Necro", 20, lambda _rng: 1, None),
    "Tloc": PropData("Tloc", 20, lambda _rng: 1, None),
    "Fire": PropData("Fire", 20, lambda _rng: 1, None),
    "Ice": PropData("Ice", 20, lambda _rng: 1, None),
    "Air": PropData("Air", 20, lambda _rng: 1, None),
    "Earth": PropData("Earth", 20, lambda _rng: 1, None),
    "Alch": PropData("Alch", 20, lambda _rng: 1, None),
}

MELEE_BRANDS: tuple[tuple[str, int], ...] = (
    ("flame", 47),
    ("freeze", 47),
    ("heavy", 26),
    ("venom", 26),
    ("drain", 26),
    ("holy", 13),
    ("elec", 13),
    ("speed", 13),
    ("vampirism", 13),
    ("pain", 13),
    ("antimagic", 13),
    ("protection", 13),
    ("spectral", 13),
    ("reaping", 6),
    ("distortion", 3),
    ("chaos", 3),
)

PROFILES: tuple[ItemProfile, ...] = (
    ItemProfile("amulet", "amulet", "jewellery", "amulet", None, jewellery_slot="amulet"),
    ItemProfile("ring", "ring", "jewellery", "ring", None, jewellery_slot="ring"),
    ItemProfile("gloves", "+0 gloves", "armour", "gloves", 0, armour_slot="gloves", aux_type="gloves"),
    ItemProfile("robe", "+4 robe", "armour", "robe", 4, armour_slot="body", robe=True),
    ItemProfile("plate", "+5 plate armour", "armour", "plate armour", 5, armour_slot="body"),
    ItemProfile("top_weapon", "+9 eveningstar", "weapon", "eveningstar", 9, weapon_subtype="melee"),
    ItemProfile("common_weapon", "+3 scimitar", "weapon", "scimitar", 3, weapon_subtype="melee"),
)

GRADE_ORDER = ("돌품", "애매템", "실전템", "명품", "돌품명품")
T = TypeVar("T")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--samples", type=int, default=200_000)
    parser.add_argument("--seed", type=int, default=20260602)
    parser.add_argument("--report", type=Path, default=REPORT_PATH)
    parser.add_argument("--json", type=Path, default=RESULTS_PATH)
    args = parser.parse_args()

    rng = random.Random(args.seed)
    profile_results = [
        _simulate_profile(profile, args.samples, rng)
        for profile in PROFILES
    ]
    aggregate = _aggregate(profile_results)
    corpus = _load_corpus_summary()

    results = {
        "metadata": {
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "source_version": SOURCE_VERSION,
            "source_url": SOURCE_URL,
            "samples_per_profile": args.samples,
            "seed": args.seed,
            "profiles": [profile.key for profile in PROFILES],
        },
        "aggregate": aggregate,
        "profiles": profile_results,
        "corpus": corpus,
    }

    args.json.write_text(json.dumps(results, ensure_ascii=False, indent=2), encoding="utf-8")
    args.report.write_text(_render_report(results), encoding="utf-8")
    print(f"Wrote {args.report} and {args.json}")


def _simulate_profile(profile: ItemProfile, samples: int, rng: random.Random) -> dict:
    grades: Counter[str] = Counter()
    luxury_grades: Counter[str] = Counter()
    score_buckets: Counter[str] = Counter()
    luxury_signals: Counter[str] = Counter()
    scores: list[int] = []
    examples: dict[str, dict] = {}

    for _ in range(samples):
        attributes, quality, bad_count = _generate_randart_attributes(profile, rng)
        artifact = _artifact(profile, attributes)
        evaluation = evaluate_artifact(artifact)
        scores.append(evaluation.total)
        grades[evaluation.grade] += 1
        luxury_grades[evaluation.luxury_grade] += 1
        score_buckets[_score_bucket(evaluation.total)] += 1
        for signal in _luxury_signals(profile, attributes, evaluation.total):
            luxury_signals[signal] += 1
        if evaluation.total >= 80:
            _record_example(examples, evaluation.grade, profile, attributes, evaluation.total, quality, bad_count)

    return {
        "profile": profile.key,
        "label": profile.label,
        "samples": samples,
        "average_score": round(mean(scores), 2),
        "max_score": max(scores),
        "grades": _rates(grades, samples),
        "luxury_grades": _rates(luxury_grades, samples),
        "score_buckets": _rates(score_buckets, samples),
        "luxury_signals": _rates(luxury_signals, samples),
        "examples": examples,
    }


def _generate_randart_attributes(profile: ItemProfile, rng: random.Random) -> tuple[list[str], int, int]:
    props: dict[str, int] = {}
    if profile.item_class == "weapon":
        props["Brand"] = _choose_weighted(MELEE_BRANDS, rng)

    quality = 1 + _binomial(6, 1 / 21, rng)
    bad = _binomial(2, 1 / 21, rng)
    good = quality + bad
    max_properties = 4 + (1 if rng.randrange(20) == 0 else 0)
    max_properties += 1 if rng.randrange(40) == 0 else 0
    enhance = 0
    if good + bad > max_properties:
        enhance = good + bad - max_properties
        good = max_properties - bad

    weights = [
        (name, prop.weight)
        for name, prop in PROPS.items()
        if prop.weight > 0 and _can_randomly_generate(name, profile)
    ]

    while good > 0 or bad > 0:
        prop_name = _choose_weighted(weights, rng)
        prop = PROPS[prop_name]
        prop_value = props.get(prop_name, 0)
        can_good = good > 0 and prop.good is not None and prop_value >= 0
        can_bad = bad > 0 and prop.bad is not None and prop_value == 0
        gen_good = can_good and (not can_bad or rng.randrange(2) == 0)

        if gen_good:
            added = False
            chance_denom = 1
            while prop_value <= prop.max_dup and (
                enhance > 0 or good > 0 and rng.randrange(chance_denom) == 0
            ):
                prop_value += prop.good(rng)
                props[prop_name] = prop_value
                added = True
                if enhance > 0 and chance_denom > 1:
                    enhance -= 1
                else:
                    good -= 1
                chance_denom += prop.odds_inc
                if prop.odds_inc == 0:
                    break
            if not added:
                continue
        elif can_bad:
            props[prop_name] = prop.bad(rng)
            bad -= 1
        else:
            continue

        weights = [(name, weight) for name, weight in weights if name != prop_name]

    return _tokens(props), quality, bad


def _can_randomly_generate(prop: str, profile: ItemProfile) -> bool:
    item_class = profile.item_class
    non_swappable = item_class in {"armour", "talisman"} or profile.jewellery_slot == "amulet"
    if prop == "Slay":
        return item_class not in {"weapon", "staff"}
    if prop in {"Regen", "-Tele", "+Inv", "Harm", "Rampage"}:
        return non_swappable
    if prop == "MP":
        return item_class not in {"weapon", "staff"}
    if prop == "^Fragile":
        return item_class not in {"armour", "talisman"} and (
            item_class != "jewellery" or profile.jewellery_slot == "amulet"
        )
    if prop == "Archmagi":
        return profile.robe
    if prop in {"Conj", "Hexes", "Summ", "Necro", "Tloc", "Fire", "Ice", "Air", "Earth", "Alch"}:
        return profile.staff or (
            prop == "Earth" and profile.aux_type in {"boots", "barding"}
            or prop == "Fire" and profile.aux_type == "gloves"
            or prop == "Air" and profile.aux_type == "cloak"
            or prop == "Ice" and profile.aux_type in {"helmet", "hat"}
        )
    return True


def _tokens(props: dict[str, int | str]) -> list[str]:
    tokens: list[str] = []
    brand = props.get("Brand")
    if isinstance(brand, str):
        tokens.append(brand)
    for name, value in props.items():
        if name == "Brand":
            continue
        if name in {"Str", "Int", "Dex", "Slay", "Stlth", "MP"}:
            tokens.append(f"{name}{value:+d}")
        elif name in {"rF", "rC", "rN", "Will"}:
            sign = "+" if value > 0 else "-"
            tokens.append(f"{name}{sign * abs(int(value))}")
        elif value:
            tokens.append(name)
    return tokens


def _artifact(profile: ItemProfile, attributes: list[str]) -> SimpleNamespace:
    return SimpleNamespace(
        random_attributes=attributes,
        base_item=profile.base_item,
        enchantment=profile.enchantment,
        item_class=profile.item_class,
        armour_slot=profile.armour_slot,
        jewellery_slot=profile.jewellery_slot,
    )


def _luxury_signals(profile: ItemProfile, attributes: list[str], total: int) -> list[str]:
    parsed = dict(_parse_token(token) for token in attributes)
    signals: list[str] = []
    slay = parsed.get("Slay")
    if isinstance(slay, int) and slay >= 4:
        signals.append("Slay+4 이상")
    if isinstance(slay, int) and slay >= 6:
        signals.append("Slay+6 이상")
    if _resist_count(parsed) >= 3:
        signals.append("저항 3종 이상")
    if profile.item_class == "jewellery" and total >= 80:
        signals.append("장신구 명품")
    if profile.item_class == "armour" and profile.armour_slot in {"cloak", "boots", "gloves", "helmet"} and total >= 80:
        signals.append("보조 방어구 명품")
    if profile.item_class == "weapon" and total >= 80:
        signals.append("무기 명품")
    if profile.item_class == "weapon" and profile.enchantment is not None and profile.enchantment >= 9:
        signals.append("무기 +9 이상")
    if (
        profile.item_class == "armour"
        and profile.armour_slot not in {"cloak", "boots", "gloves", "helmet"}
        and profile.enchantment is not None
        and profile.enchantment >= 10
    ):
        signals.append("중갑/방패 +10 이상")
    if (
        profile.item_class == "armour"
        and profile.armour_slot in {"cloak", "boots", "gloves", "helmet"}
        and profile.enchantment is not None
        and profile.enchantment >= 4
    ):
        signals.append("보조 방어구 +4 이상")
    if not any(_is_bad_token(token) for token in attributes):
        signals.append("무페널티")
    return signals


def _parse_token(token: str) -> tuple[str, int | bool]:
    for key in ("Str", "Int", "Dex", "Slay", "Stlth", "MP"):
        if token.startswith(key) and token[len(key) : len(key) + 1] in {"+", "-"}:
            suffix = token[len(key) :]
            if len(suffix) > 1 and suffix[1:].isdigit():
                return key, int(suffix)
            if set(suffix) <= {"+", "-"}:
                sign = -1 if suffix[0] == "-" else 1
                return key, sign * len(suffix)
    for key in ("rF", "rC", "rN", "Will"):
        if token.startswith(key):
            suffix = token[len(key) :]
            if suffix and set(suffix) <= {"+", "-"}:
                sign = -1 if suffix[0] == "-" else 1
                return key, sign * len(suffix)
    return token, True


def _resist_count(parsed: dict[str, int | bool]) -> int:
    count = 0
    for key in ("rF", "rC", "rN", "Will"):
        value = parsed.get(key)
        if isinstance(value, int) and value > 0:
            count += 1
    for key in ("rElec", "rPois", "rCorr"):
        if parsed.get(key) is True:
            count += 1
    return count


def _is_bad_token(token: str) -> bool:
    key, value = _parse_token(token)
    if token in {"*Noise", "-Tele", "*Rage", "^Contam", "*Corrode", "^Drain", "*Slow", "^Fragile"}:
        return True
    return isinstance(value, int) and value < 0


def _choose_weighted(choices: list[tuple[T, int]] | tuple[tuple[T, int], ...], rng: random.Random) -> T:
    total = sum(weight for _, weight in choices)
    pick = rng.randrange(total)
    upto = 0
    for value, weight in choices:
        upto += weight
        if pick < upto:
            return value
    return choices[-1][0]


def _binomial(n: int, p: float, rng: random.Random) -> int:
    return sum(1 for _ in range(n) if rng.random() < p)


def _score_bucket(score: int) -> str:
    if score >= 90:
        return "90-100"
    if score >= 80:
        return "80-89"
    if score >= 65:
        return "65-79"
    if score >= 45:
        return "45-64"
    return "0-44"


def _record_example(
    examples: dict[str, dict],
    grade: str,
    profile: ItemProfile,
    attributes: list[str],
    score: int,
    quality: int,
    bad_count: int,
) -> None:
    current = examples.get(grade)
    if current and current["score"] >= score:
        return
    examples[grade] = {
        "profile": profile.label,
        "score": score,
        "quality": quality,
        "bad_count": bad_count,
        "attributes": attributes,
    }


def _rates(counter: Counter[str], samples: int) -> dict[str, dict[str, float | int]]:
    return {
        key: {"count": counter[key], "rate": counter[key] / samples}
        for key in sorted(counter)
    }


def _aggregate(profile_results: list[dict]) -> dict:
    samples = sum(result["samples"] for result in profile_results)
    grades: Counter[str] = Counter()
    luxury_grades: Counter[str] = Counter()
    signals: Counter[str] = Counter()
    max_score = 0
    weighted_score = 0.0
    for result in profile_results:
        result_samples = result["samples"]
        weighted_score += result["average_score"] * result_samples
        max_score = max(max_score, result["max_score"])
        for grade, data in result["grades"].items():
            grades[grade] += int(data["count"])
        for grade, data in result["luxury_grades"].items():
            luxury_grades[grade] += int(data["count"])
        for signal, data in result["luxury_signals"].items():
            signals[signal] += int(data["count"])
    return {
        "samples": samples,
        "average_score": round(weighted_score / samples, 2),
        "max_score": max_score,
        "grades": _rates(grades, samples),
        "luxury_grades": _rates(luxury_grades, samples),
        "luxury_signals": _rates(signals, samples),
    }


def _load_corpus_summary() -> dict:
    corpus_path = Path("crawl_service/docs/research/randart-corpus/corpus.json")
    if not corpus_path.exists():
        return {}
    corpus = json.loads(corpus_path.read_text(encoding="utf-8"))
    artifacts = corpus.get("artifacts", [])
    grades: Counter[str] = Counter()
    luxury_grades: Counter[str] = Counter()
    scores: list[int] = []
    rarity_scores: list[int] = []
    signals = Counter()
    for artifact in artifacts:
        attrs = artifact.get("random_attributes", [])
        profile = ItemProfile(
            "corpus",
            "corpus",
            artifact.get("item_class", "unknown"),
            artifact.get("base_item", "unknown"),
            artifact.get("enchantment"),
            armour_slot=artifact.get("armour_slot"),
            jewellery_slot=artifact.get("jewellery_slot"),
        )
        evaluation = evaluate_artifact(_artifact(profile, attrs))
        grades[evaluation.grade] += 1
        luxury_grades[evaluation.luxury_grade] += 1
        scores.append(evaluation.total)
        rarity_scores.append(evaluation.rarity_score)
        for signal in _luxury_signals(profile, attrs, evaluation.total):
            signals[signal] += 1
    return {
        "samples": len(artifacts),
        "average_score": round(mean(scores), 2) if scores else 0,
        "max_score": max(scores) if scores else 0,
        "average_rarity_score": round(mean(rarity_scores), 2) if rarity_scores else 0,
        "max_rarity_score": max(rarity_scores) if rarity_scores else 0,
        "grades": _rates(grades, len(artifacts)) if artifacts else {},
        "luxury_grades": _rates(luxury_grades, len(artifacts)) if artifacts else {},
        "luxury_signals": _rates(signals, len(artifacts)) if artifacts else {},
    }


def _render_report(results: dict) -> str:
    meta = results["metadata"]
    aggregate = results["aggregate"]
    corpus = results["corpus"]
    lines = [
        "# Randart Rarity and Luxury Report",
        "",
        "이 문서는 DCSS randart 속성 생성 메커니즘을 단순 Monte Carlo로 재현해,",
        "현재 repo의 실전성/희소도/명품 판정 사이의 관계를 정리한다.",
        "",
        "## Scope",
        "",
        f"- Source baseline: Crawl `{meta['source_version']}` `artefact.cc` randart property generation.",
        f"- Source URL: <{meta['source_url']}>",
        f"- Samples: `{meta['samples_per_profile']:,}` per profile, `{aggregate['samples']:,}` total.",
        f"- Seed: `{meta['seed']}`.",
        "- This is conditional on an item already becoming a randart; it does not model whole-game item placement, shop generation, acquirement, or exact base-item frequency.",
        "- Weapon brand generation and item-specific artprop eligibility are approximated from `artefact.cc`; fixed props, god gifts, unrand replacement, and full ego/base generation are out of scope.",
        "- High enchantment is included as a luxury signal for fixed representative profiles and real corpus items. Whole-game probability for those enchantment/base outcomes still requires the full item generator.",
        "",
        "## Mechanism Rarity",
        "",
        "Before item class or scoring is considered, the source quality roll is already strongly low-biased.",
        "`quality = 1 + Binomial(6, 1/21)`, and bad props are `Binomial(2, 1/21)`.",
        "",
        "### Quality Roll",
        "",
        _mechanism_quality_table(),
        "",
        "### Good Property/Enhancement Opportunities",
        "",
        _mechanism_good_table(),
        "",
        "## Aggregate Simulation",
        "",
        f"| Metric | Value |",
        "| --- | ---: |",
        f"| Average score | {aggregate['average_score']:.2f} |",
        f"| Max score observed | {aggregate['max_score']} |",
        "",
        "### Practical Grade Rarity",
        "",
        _rate_table(aggregate["grades"], GRADE_ORDER),
        "",
        "### Luxury Grade Rarity",
        "",
        _rate_table(aggregate["luxury_grades"]),
        "",
        "### Luxury Signals",
        "",
        _rate_table(aggregate["luxury_signals"]),
        "",
        "## By Item Profile",
        "",
        "| Profile | Avg | Max | practical 실전템+ | luxury 명품+ | 돌품명품 후보+ | Slay+4+ | Slay+6+ |",
        "| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |",
    ]
    for result in results["profiles"]:
        grades = result["grades"]
        luxury_grades = result["luxury_grades"]
        signals = result["luxury_signals"]
        practical = _sum_rates(grades, ["실전템", "명품", "돌품명품"])
        luxury = _sum_rates(luxury_grades, ["명품", "돌품명품 후보", "전설급"])
        candidate = _sum_rates(luxury_grades, ["돌품명품 후보", "전설급"])
        lines.append(
            "| {label} | {avg:.2f} | {max_score} | {practical} | {luxury} | {candidate} | {slay4} | {slay6} |".format(
                label=result["label"],
                avg=result["average_score"],
                max_score=result["max_score"],
                practical=_pct(practical),
                luxury=_pct(luxury),
                candidate=_pct(candidate),
                slay4=_pct(_rate(signals, "Slay+4 이상")),
                slay6=_pct(_rate(signals, "Slay+6 이상")),
            )
        )
    lines.extend(
        [
            "",
            "## Real Morgue Corpus Comparison",
            "",
            "기존 `crawl_service/docs/research/randart-corpus/corpus.json` 150개 표본은 생성 확률 표본이 아니라",
            "실제 morgue에서 관측된 아이템 표본이다. 그래도 시뮬레이션 결과의 고점 희소성과",
            "현실 관측의 온도를 비교하는 참고값으로 쓸 수 있다.",
            "",
            f"| Metric | Value |",
            "| --- | ---: |",
            f"| Corpus artifacts | {corpus.get('samples', 0):,} |",
            f"| Average score | {corpus.get('average_score', 0):.2f} |",
            f"| Max score | {corpus.get('max_score', 0)} |",
            f"| Average rarity score | {corpus.get('average_rarity_score', 0):.2f} |",
            f"| Max rarity score | {corpus.get('max_rarity_score', 0)} |",
            "",
            "### Corpus Practical Grades",
            "",
            _rate_table(corpus.get("grades", {}), GRADE_ORDER),
            "",
            "### Corpus Luxury Grades",
            "",
            _rate_table(corpus.get("luxury_grades", {})),
            "",
            "### Corpus Luxury Signals",
            "",
            _rate_table(corpus.get("luxury_signals", {})),
            "",
            "## Interpretation",
            "",
            "- `grade`는 실전성 등급이고, `luxury_grade`는 실전성에 `rarity_score`를 결합한 커뮤니티식 명품 판정이다.",
            "- 명품 등급은 단순히 좋은 속성이 하나 붙는 사건이 아니다. 품질값이 3 이상으로 올라갈 확률부터 약 5%대이고, 4회 이상 좋은 속성/강화 기회는 약 0.5%대다.",
            "- `Slay+4` 이상은 source 로직상 같은 `Slay` prop을 여러 번 강화해야 하는 쪽에 가까워, 장신구와 방어구에서 강한 희소도 신호가 된다.",
            "- 강화수치는 명품성의 핵심 신호라 `rarity_score`에 반영한다. 다만 이 시뮬레이션은 대표 프로필의 고정 강화수치를 쓰므로, 게임 전체에서 해당 강화수치와 base가 함께 나올 확률은 별도 item generator 분석이 필요하다.",
            "- 무기는 `Slay`가 randart property로 붙지 않기 때문에 명품 판정이 base, enchantment, brand, 저항 압축에 더 의존한다. 같은 점수라도 장신구/보조 방어구의 `Slay` spike와 성격이 다르다.",
            "- 이 결과는 randart 하나당 조건부 확률이다. 한 게임에서 체감되는 희소도는 randart 생성 기회 수, branch/shop/acquirement, base item 분포까지 곱해져 더 낮아진다.",
            "",
            "## Reproduction",
            "",
            "```sh",
            f"python3 scripts/simulate_randart_rarity.py --samples {meta['samples_per_profile']} --seed {meta['seed']}",
            "```",
            "",
            f"Raw simulation output: `crawl_service/docs/research/randart-corpus/rarity_simulation.json`.",
            "",
        ]
    )
    return "\n".join(lines)


def _rate_table(rates: dict, preferred_order: tuple[str, ...] = ()) -> str:
    if not rates:
        return "_No data._"
    keys = [key for key in preferred_order if key in rates]
    keys.extend(sorted(key for key in rates if key not in keys))
    lines = ["| Value | Count | Rate |", "| --- | ---: | ---: |"]
    for key in keys:
        data = rates[key]
        lines.append(f"| `{key}` | {int(data['count']):,} | {_pct(float(data['rate']))} |")
    return "\n".join(lines)


def _mechanism_quality_table() -> str:
    rows = []
    for quality in range(1, 8):
        probability = _binomial_probability(6, quality - 1, 1 / 21)
        rows.append((str(quality), probability))
    return _probability_table(rows)


def _mechanism_good_table() -> str:
    rows = []
    for threshold in range(1, 8):
        probability = 0.0
        for quality in range(1, 8):
            for bad in range(3):
                good = quality + bad
                if good >= threshold:
                    probability += (
                        _binomial_probability(6, quality - 1, 1 / 21)
                        * _binomial_probability(2, bad, 1 / 21)
                    )
        rows.append((f">= {threshold}", probability))
    return _probability_table(rows)


def _binomial_probability(n: int, k: int, p: float) -> float:
    from math import comb

    return comb(n, k) * p**k * (1 - p) ** (n - k)


def _probability_table(rows: list[tuple[str, float]]) -> str:
    lines = ["| Value | Probability |", "| --- | ---: |"]
    for label, probability in rows:
        lines.append(f"| `{label}` | {_pct(probability)} |")
    return "\n".join(lines)


def _rate(rates: dict, key: str) -> float:
    return float(rates.get(key, {}).get("rate", 0.0))


def _sum_rates(rates: dict, keys: list[str]) -> float:
    return sum(_rate(rates, key) for key in keys)


def _pct(rate: float) -> str:
    if rate == 0:
        return "0%"
    percent = rate * 100
    if percent < 0.0001:
        return "<0.0001%"
    if rate < 0.0001:
        return f"{rate * 100:.4f}%"
    if rate < 0.01:
        return f"{rate * 100:.3f}%"
    return f"{rate * 100:.2f}%"


if __name__ == "__main__":
    main()
