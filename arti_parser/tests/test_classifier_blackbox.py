from __future__ import annotations

import unittest

from arti_parser.classifier import classify_artifact
from arti_parser.models import ArtifactDocumentAttribute


class ArtifactClassifierBlackBoxTest(unittest.TestCase):
    def test_dragon_scales_intrinsic_resistance_is_not_duplicated_in_display(self) -> None:
        classification = classify_artifact(
            attributes=[
                _attribute("rPois", "rPois", True),
                _attribute("rF+++", "rF", 3),
                _attribute("rC+", "rC", 1),
                _attribute("rCorr", "rCorr", True),
                _attribute("Str+3", "Str", 3),
                _attribute("Dex-2", "Dex", -2),
            ],
            display_name="+15 golden dragon scales of Alimpaim",
            base_item="golden dragon scales",
            base_subtype=None,
            enchantment=15,
        )

        self.assertEqual(classification.base_attributes, ["rF+", "rC+", "rPois"])
        self.assertEqual(
            classification.all_attributes,
            ["rPois", "rF+++", "rC+", "rCorr", "Str+3", "Dex-2"],
        )
        self.assertEqual(
            classification.random_attributes,
            ["rF++", "rCorr", "Str+3", "Dex-2"],
        )

    def test_missing_intrinsic_attribute_is_still_added_to_display_only(self) -> None:
        classification = classify_artifact(
            attributes=[
                _attribute("rF++", "rF", 2),
            ],
            display_name="+3 fire dragon scales of Warmth",
            base_item="fire dragon scales",
            base_subtype=None,
            enchantment=3,
        )

        self.assertEqual(classification.base_attributes, ["rF++", "rC-"])
        self.assertEqual(classification.all_attributes, ["rF++", "rC-"])
        self.assertEqual(classification.random_attributes, [])


def _attribute(token: str, key: str, value: int | bool) -> ArtifactDocumentAttribute:
    return ArtifactDocumentAttribute(
        token=token,
        key=key,
        value=value,
        description=None,
    )


if __name__ == "__main__":
    unittest.main()
