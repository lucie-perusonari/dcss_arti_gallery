from __future__ import annotations

import unittest
from dataclasses import fields

from crawl_service.domain.artifacts.classifier import build_random_artifact
from crawl_service.domain.artifacts.info_parser import parse_artifact_info
from crawl_service.domain.artifacts.raw_parser import get_txt_artifact_raw_info
from crawl_service.domain.evaluation.evaluator import ArtifactEvaluation, evaluate_artifact


def random_artifact_from_inventory_lines(lines: list[str]):
    raw_info = get_txt_artifact_raw_info("\n".join(["Inventory:", *lines, "   Skills:"]))[0]
    artifact_info = parse_artifact_info(raw_info)
    return build_random_artifact(artifact_info)


class ArtifactEvaluatorTest(unittest.TestCase):
    def test_evaluate_artifact_evaluates_weapon_offense_defense_and_penalty(self) -> None:
        artifact = random_artifact_from_inventory_lines(
            [
                ' a - the +6 broad axe "Axe" {heavy Slay+3 rF+ *Slow}',
                "     Fire: It protects you from fire.",
            ]
        )

        evaluation = evaluate_artifact(artifact)

        self.assertIsInstance(evaluation, ArtifactEvaluation)
        self.assertEqual(evaluation.offense, 20)
        self.assertEqual(evaluation.defense, 4)
        self.assertEqual(evaluation.utility, 0)
        self.assertEqual(evaluation.penalty, -8)
        self.assertEqual(evaluation.base_fit, 20)
        self.assertTrue(0 <= evaluation.total <= 100)

    def test_evaluation_result_is_shallow(self) -> None:
        artifact = random_artifact_from_inventory_lines(
            [
                ' a - the +6 broad axe "Axe" {Slay+3}',
            ]
        )

        evaluation = evaluate_artifact(artifact)

        self.assertEqual(
            [field.name for field in fields(evaluation)],
            [
                "total",
                "practical_score",
                "rarity_score",
                "offense",
                "defense",
                "utility",
                "penalty",
                "base_fit",
                "grade",
                "luxury_grade",
            ],
        )

    def test_evaluate_artifact_uses_random_attributes_after_base_intrinsic_removal(self) -> None:
        artifact = random_artifact_from_inventory_lines(
            [
                ' a - the ring "Miracles" {rCorr AC+4}',
                "     [ring of protection]",
                "     AC+4: It affects your AC (+4).",
            ]
        )

        evaluation = evaluate_artifact(artifact)

        self.assertEqual(artifact.base_attributes, ["AC+4"])
        self.assertEqual(artifact.random_attributes, ["rCorr"])
        self.assertEqual(evaluation.defense, 3)
        self.assertEqual(evaluation.utility, 0)
        self.assertEqual(evaluation.penalty, 0)
        self.assertEqual(evaluation.rarity_score, 0)

    def test_evaluate_artifact_does_not_score_base_item_intrinsics(self) -> None:
        artifact = random_artifact_from_inventory_lines(
            [
                ' a - the +2 troll leather armour "Root" {rC+ Slay+2}',
            ]
        )

        evaluation = evaluate_artifact(artifact)

        self.assertEqual(artifact.base_attributes, ["Regen+"])
        self.assertEqual(artifact.random_attributes, ["rC+", "Slay+2"])
        self.assertEqual(evaluation.utility, 0)

    def test_evaluate_artifact_evaluates_jewellery_utility_and_grade(self) -> None:
        artifact = random_artifact_from_inventory_lines(
            [
                ' a - the amulet "Buosiylo" {Reflect Rampage rC++ Regen+ SH+5}',
                "     [amulet of reflection]",
                "     Reflect: It reflects blocked missile attacks.",
                "     Rampage: It bestows one free step when moving toward enemies.",
                "     Cold: It greatly protects you from cold.",
                "     Regen: It increases your rate of health regeneration.",
            ]
        )

        evaluation = evaluate_artifact(artifact)

        self.assertEqual(
            artifact.random_attributes,
            ["Rampage", "rC++", "Regen+"],
        )
        self.assertEqual(evaluation.defense, 7)
        self.assertEqual(evaluation.utility, 10)
        self.assertGreaterEqual(evaluation.total, 60)
        self.assertEqual(evaluation.grade, "애매템")

    def test_evaluate_artifact_scores_random_slay_as_rarity_signal(self) -> None:
        artifact = random_artifact_from_inventory_lines(
            [
                ' a - the amulet "Spike" {Slay+4 Str+4 rF+}',
            ]
        )

        evaluation = evaluate_artifact(artifact)

        self.assertEqual(artifact.random_attributes, ["Slay+4", "Str+4", "rF+"])
        self.assertEqual(evaluation.rarity_score, 60)
        self.assertEqual(evaluation.luxury_grade, "돌품명품 후보")

    def test_evaluate_artifact_scores_enchantment_as_luxury_rarity_signal(self) -> None:
        low_enchant = random_artifact_from_inventory_lines(
            [
                ' a - the +0 eveningstar "Stars" {elec rF+ rC+}',
            ]
        )
        high_enchant = random_artifact_from_inventory_lines(
            [
                ' a - the +9 eveningstar "Stars" {elec rF+ rC+}',
            ]
        )

        low_evaluation = evaluate_artifact(low_enchant)
        high_evaluation = evaluate_artifact(high_enchant)

        self.assertGreater(high_evaluation.practical_score, low_evaluation.practical_score)
        self.assertGreater(high_evaluation.rarity_score, low_evaluation.rarity_score)
        self.assertEqual(high_evaluation.rarity_score, 35)


if __name__ == "__main__":
    unittest.main()
