from __future__ import annotations

import unittest

from crawl_service.artifacts.models import ArtifactDocumentEvaluation
from crawl_service.morgue.types import MorgueRawText
from crawl_service.core.processor import ArtifactProcessor


def document_from_inventory_lines(lines: list[str]):
    return ArtifactProcessor().documents_from_raw_text(
        MorgueRawText(
            name="morgue-test-20260101-000001.txt",
            url="https://example.test/morgue.txt",
            extension="txt",
            text="\n".join(["Inventory:", *lines, "   Skills:"]),
        )
    )[0]


class ArtifactEvaluatorTest(unittest.TestCase):
    def test_evaluate_artifact_evaluates_weapon_offense_defense_and_penalty(self) -> None:
        document = document_from_inventory_lines(
            [
                ' a - the +6 broad axe "Axe" {heavy Slay+3 rF+ *Slow}',
                "     rF+: It protects you from fire.",
            ]
        )

        evaluation = document.evaluation

        self.assertEqual(evaluation.offense, 20)
        self.assertEqual(evaluation.defense, 4)
        self.assertEqual(evaluation.utility, 0)
        self.assertEqual(evaluation.penalty, -8)
        self.assertEqual(evaluation.base_fit, 20)
        self.assertTrue(0 <= evaluation.total <= 100)

    def test_evaluation_result_is_shallow(self) -> None:
        self.assertEqual(
            list(ArtifactDocumentEvaluation.model_fields),
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
        document = document_from_inventory_lines(
            [
                ' a - the ring "Miracles" {rCorr AC+4}',
                "     [ring of protection]",
                "     AC+4: It affects your AC (+4).",
            ]
        )

        self.assertEqual(document.base_attributes, ["AC+4"])
        self.assertEqual(document.random_attributes, ["rCorr"])
        self.assertEqual(document.evaluation.defense, 3)
        self.assertEqual(document.evaluation.utility, 0)
        self.assertEqual(document.evaluation.penalty, 0)
        self.assertEqual(document.evaluation.rarity_score, 0)

    def test_evaluate_artifact_does_not_score_base_item_intrinsics(self) -> None:
        document = document_from_inventory_lines(
            [' a - the +2 troll leather armour "Root" {rC+ Slay+2}']
        )

        self.assertEqual(document.base_attributes, ["Regen+"])
        self.assertEqual(document.random_attributes, ["rC+", "Slay+2"])
        self.assertEqual(document.evaluation.utility, 0)

    def test_evaluate_artifact_evaluates_jewellery_utility_and_grade(self) -> None:
        document = document_from_inventory_lines(
            [
                ' a - the amulet "Buosiylo" {Reflect Rampage rC++ Regen+ SH+5}',
                "     [amulet of reflection]",
                "     Reflect: It reflects blocked missile attacks.",
                "     Rampage: It bestows one free step when moving toward enemies.",
                "     rC++: It greatly protects you from cold.",
                "     Regen+: It increases your rate of health regeneration.",
            ]
        )

        self.assertEqual(document.random_attributes, ["Rampage", "rC++", "Regen+"])
        self.assertEqual(document.evaluation.defense, 7)
        self.assertEqual(document.evaluation.utility, 10)
        self.assertGreaterEqual(document.evaluation.total, 60)
        self.assertEqual(document.evaluation.grade, "애매템")

    def test_evaluate_artifact_scores_random_slay_as_rarity_signal(self) -> None:
        document = document_from_inventory_lines(
            [' a - the amulet "Spike" {Slay+4 Str+4 rF+}']
        )

        self.assertEqual(document.random_attributes, ["Slay+4", "Str+4", "rF+"])
        self.assertEqual(document.evaluation.rarity_score, 60)
        self.assertEqual(document.evaluation.luxury_grade, "돌품명품 후보")

    def test_evaluate_artifact_scores_enchantment_as_luxury_rarity_signal(self) -> None:
        low_enchant = document_from_inventory_lines(
            [' a - the +0 eveningstar "Stars" {elec rF+ rC+}']
        )
        high_enchant = document_from_inventory_lines(
            [' a - the +9 eveningstar "Stars" {elec rF+ rC+}']
        )

        self.assertGreater(
            high_enchant.evaluation.practical_score,
            low_enchant.evaluation.practical_score,
        )
        self.assertGreater(
            high_enchant.evaluation.rarity_score,
            low_enchant.evaluation.rarity_score,
        )
        self.assertEqual(high_enchant.evaluation.rarity_score, 35)

    def test_evaluate_artifact_scores_repeated_stealth_and_negative_resistance(self) -> None:
        document = document_from_inventory_lines(
            [' a - the ring "Quiet Risk" {Stlth++ rPois-}']
        )

        self.assertEqual(document.evaluation.utility, 4)
        self.assertEqual(document.evaluation.penalty, -5)


if __name__ == "__main__":
    unittest.main()
