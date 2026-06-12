from __future__ import annotations

import unittest

from crawl_service.artifacts.models import ArtifactDocument
from crawl_service.tests.artifacts.helpers import artifact_document


class DocumentModelTest(unittest.TestCase):
    def test_document_model_uses_artifact_shaped_input(self) -> None:
        document = artifact_document()

        self.assertIsInstance(document, ArtifactDocument)
        self.assertTrue(document.id)
        self.assertEqual(document.name, 'the +1 cloak "Rain" {rPois}')
        self.assertEqual(document.source.file, "morgue-wiiwiwi-20260516-185425.txt")
        self.assertEqual(document.source.player, "wiiwiwi")
        self.assertEqual(document.evaluation.total, 42)

    def test_document_model_stores_canonical_snake_case_fields(self) -> None:
        document = artifact_document(
            name='the +6 broad axe "Axe" {heavy Slay+3 rF+ *Slow}',
            base_item="broad axe",
            item_class="weapon",
            item_subtype="broad axe",
            armour_slot=None,
            attributes=["heavy", "Slay+3", "rF+", "*Slow"],
            description_lines=[
                "Slay+3: It affects your accuracy & damage with ranged weapons and melee",
                "(+3).",
                "rF+: It protects you from fire.",
                "*Slow: It may slow you when you take damage.",
            ],
        )
        data = document.to_dict()

        self.assertEqual(data["base_item"], "broad axe")
        self.assertEqual(data["item_class"], "weapon")
        self.assertEqual(data["random_attributes"], ["heavy", "Slay+3", "rF+", "*Slow"])
        self.assertEqual(data["visible_item_description"][0], "Slay+3: It affects your accuracy & damage with ranged weapons and melee")
        self.assertEqual(data["attributes"][0]["token"], "heavy")
        self.assertIn("evaluation", data)
        self.assertNotIn("baseItem", data)
        self.assertNotIn("tile", data)
        self.assertNotIn("score", data)
        self.assertNotIn("dcssDescription", data)
        self.assertNotIn("rawDescription", data)


if __name__ == "__main__":
    unittest.main()
