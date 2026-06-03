from __future__ import annotations

import unittest

from api.presenter import present_artifact_document
from api.tests.helpers import artifact_document


class ArtifactPresenterTest(unittest.TestCase):
    def test_presenter_builds_frontend_fields_from_canonical_document(self) -> None:
        document = artifact_document(
            name='the +6 broad axe "Axe" {heavy Slay+3 rF+ *Slow}',
            base_item="broad axe",
            item_class="weapon",
            item_subtype="broad axe",
            armour_slot=None,
            attributes=["heavy", "Slay+3", "rF+", "*Slow"],
        )
        document["visible_item_description"] = [
            "Slay+3: It affects your accuracy & damage with ranged weapons and melee",
            "(+3).",
            "rF+: It protects you from fire.",
            "*Slow: It may slow you when you take damage.",
        ]

        artifact = present_artifact_document(document)

        self.assertEqual(artifact.baseItem, "broad axe")
        self.assertEqual(artifact.type, "weapon")
        self.assertTrue(artifact.tile.startswith("/tiles/randart/weapon/broad-axe-"))
        self.assertTrue(artifact.tile.endswith(".png"))
        self.assertEqual(artifact.score.total, artifact.evaluation.total)
        self.assertEqual(artifact.attributes[-1].scoreImpact, "negative")
        self.assertIn("Slay+3: It affects your accuracy & damage with ranged weapons and melee (+3).", artifact.rawDescription)

    def test_presenter_uses_randart_tile_variants(self) -> None:
        cases = [
            (
                artifact_document(
                    name='the +8 executioner\'s axe "Woe" {speed}',
                    base_item="executioner's axe",
                    item_class="weapon",
                    item_subtype="executioner's axe",
                    armour_slot=None,
                ),
                "/tiles/randart/weapon/executioners-axe-",
            ),
            (
                artifact_document(
                    name='the +5 great mace "Tremor" {heavy}',
                    base_item="great mace",
                    item_class="weapon",
                    item_subtype="great mace",
                    armour_slot=None,
                ),
                "/tiles/randart/weapon/great-mace-",
            ),
            (
                artifact_document(
                    name='the +2 pair of gloves "Leaf" {rC++}',
                    base_item="pair",
                    item_class="armour",
                    item_subtype="gloves",
                    armour_slot="gloves",
                ),
                "/tiles/randart/armour/gloves-",
            ),
            (
                artifact_document(
                    name='the ring "Winter" {Ice rC+ Int+4}',
                    base_item="ring",
                    item_class="jewellery",
                    item_subtype="ring of ice",
                    armour_slot=None,
                    jewellery_slot="ring",
                ),
                "/tiles/randart/ring/ring-",
            ),
            (
                artifact_document(
                    name='the amulet "Lifeline" {RegenMP+ Str+2}',
                    base_item="amulet",
                    item_class="jewellery",
                    item_subtype="amulet of magic regeneration",
                    armour_slot=None,
                    jewellery_slot="amulet",
                ),
                "/tiles/randart/amulet/amulet-",
            ),
            (
                artifact_document(
                    name='the staff "Pyre" {rF+ Fire}',
                    base_item="staff",
                    item_class="staff",
                    item_subtype="staff of fire",
                    armour_slot=None,
                ),
                "/tiles/randart/staff/staff-",
            ),
        ]

        for document, expected_prefix in cases:
            with self.subTest(expected_prefix=expected_prefix):
                tile = present_artifact_document(document).tile
                self.assertTrue(tile.startswith(expected_prefix))
                self.assertTrue(tile.endswith(".png"))

    def test_presenter_uses_specific_non_variant_tile_paths(self) -> None:
        cases = [
            (
                artifact_document(
                    name='the +7 gold dragon scales "Bulwark" {rPois rF+ rC+}',
                    base_item="gold dragon scales",
                    item_class="armour",
                    item_subtype="body_armour",
                    armour_slot="body_armour",
                ),
                "/tiles/gold-dragon-scales.png",
            ),
            (
                artifact_document(
                    name='the talisman "Quill" {Will+}',
                    base_item="talisman",
                    item_class="talisman",
                    item_subtype="quill talisman",
                    armour_slot=None,
                ),
                "/tiles/talisman-quill.png",
            ),
            (
                artifact_document(
                    name="the skull of Zonguldrok {Reaping Hat+ rN+ Int+4}",
                    base_item="skull",
                    item_class="misc",
                    item_subtype="skull of Zonguldrok",
                    armour_slot=None,
                ),
                "/tiles/skull-of-zonguldrok.png",
            ),
        ]

        for document, expected_tile in cases:
            with self.subTest(expected_tile=expected_tile):
                self.assertEqual(present_artifact_document(document).tile, expected_tile)

    def test_randart_tile_variant_is_stable_per_artifact(self) -> None:
        document = artifact_document(
            name='the ring "Winter" {Ice rC+ Int+4}',
            base_item="ring",
            item_class="jewellery",
            item_subtype="ring of ice",
            armour_slot=None,
            jewellery_slot="ring",
        )

        first = present_artifact_document(document).tile
        second = present_artifact_document(document).tile

        self.assertEqual(first, second)


if __name__ == "__main__":
    unittest.main()
