from __future__ import annotations

import unittest

from crawl_service.artifacts.info_parser import (
    artifact_attributes,
    artifact_base_item,
    artifact_display_name,
    artifact_enchantment_and_base_text,
)
from crawl_service.artifacts.extractor import get_txt_artifact_raw_info


SAMPLE_TXT = "\n".join(
    [
        "Inventory:",
        ' a - the +6 broad axe of Plog {chaos rC+ Str+3 Stlth+}',
        "     (Found on D:1.)",
        "     Chaos: It unleashes unpredictable effects.",
        ' b - the ring "Jiogot" {rCorr AC+4}',
        "     (Found on D:2.)",
        "     [ring of protection]",
        "     AC+4: It affects your AC (+4).",
        "   Skills:",
    ]
)


class ArtifactInfoParserTest(unittest.TestCase):
    def test_artifact_parsing_functions_tokenizes_properties_and_base_item(self) -> None:
        artifact = get_txt_artifact_raw_info(SAMPLE_TXT)[0]

        display_name = artifact_display_name(artifact["artifact_name"])
        enchantment, base_text = artifact_enchantment_and_base_text(display_name)
        attributes = artifact_attributes(
            artifact["artifact_name"],
            artifact["visible_item_description"],
        )

        self.assertEqual(display_name, '+6 broad axe of Plog')
        self.assertEqual(artifact_base_item(base_text, artifact["bracket_subtype"]), "broad axe")
        self.assertEqual(enchantment, 6)
        self.assertEqual(
            [attribute.token for attribute in attributes],
            ["chaos", "rC+", "Str+3", "Stlth+"],
        )
        self.assertEqual(attributes[1].key, "rC")
        self.assertEqual(attributes[1].value, 1)
        self.assertEqual(attributes[2].value, 3)

    def test_artifact_parsing_functions_handles_cursed_and_negative_enchantments(self) -> None:
        artifacts = get_txt_artifact_raw_info(
            "\n".join(
                [
                    "Inventory:",
                    ' a - the cursed +9 broad axe of Supernal Understanding {speed, rPois Dex+8}',
                    ' b - the -2 hat of the Alchemist {rElec rPois rF+}',
                    "   Skills:",
                ]
            )
        )

        cursed_display_name = artifact_display_name(artifacts[0]["artifact_name"])
        negative_display_name = artifact_display_name(artifacts[1]["artifact_name"])
        cursed_enchantment, cursed_base_text = artifact_enchantment_and_base_text(cursed_display_name)
        negative_enchantment, negative_base_text = artifact_enchantment_and_base_text(negative_display_name)

        self.assertEqual(cursed_enchantment, 9)
        self.assertEqual(artifact_base_item(cursed_base_text, artifacts[0]["bracket_subtype"]), "broad axe")
        self.assertEqual(negative_enchantment, -2)
        self.assertEqual(artifact_base_item(negative_base_text, artifacts[1]["bracket_subtype"]), "hat")

    def test_artifact_parsing_functions_preserves_known_multi_word_properties(self) -> None:
        artifacts = get_txt_artifact_raw_info(
            "\n".join(
                [
                    "Inventory:",
                    ' a - the +1 trishula "Dawn" {holy wrath, rN+}',
                    ' b - the +11 Singing Sword {sonic wave}',
                    "   Skills:",
                ]
            )
        )
        artifact = artifacts[0]
        singing_sword = artifacts[1]

        attributes = artifact_attributes(artifact["artifact_name"], artifact["visible_item_description"])
        singing_sword_attributes = artifact_attributes(
            singing_sword["artifact_name"],
            singing_sword["visible_item_description"],
        )

        self.assertEqual([attribute.token for attribute in attributes], ["holy wrath", "rN+"])
        self.assertEqual([attribute.token for attribute in singing_sword_attributes], ["sonic wave"])

    def test_artifact_parsing_functions_splits_first_comma_group_and_drops_internal_tags(self) -> None:
        artifact = get_txt_artifact_raw_info(
            "\n".join(
                [
                    "Inventory:",
                    ' a - the ring "Keus" {Rampage rCorr Int+2, Self, Sorc}',
                    "     Rampage: It bestows one free step when moving towards enemies.",
                    "     rCorr: It protects you from acid and corrosion.",
                    "     Int+2: It affects your intelligence (+2).",
                    "   Skills:",
                ]
            )
        )
        artifact = artifact[0]

        attributes = artifact_attributes(artifact["artifact_name"], artifact["visible_item_description"])

        self.assertEqual([attribute.token for attribute in attributes], ["Rampage", "rCorr", "Int+2"])

    def test_artifact_parsing_functions_drops_lowercase_internal_tags_without_dropping_vampirism(self) -> None:
        artifact = get_txt_artifact_raw_info(
            "\n".join(
                [
                    "Inventory:",
                    ' a - the +4 dagger "Biter" {vampirism rN+ vamp self Melee}',
                    "     rN+: It protects you from negative energy.",
                    "   Skills:",
                ]
            )
        )
        artifact = artifact[0]

        attributes = artifact_attributes(artifact["artifact_name"], artifact["visible_item_description"])

        self.assertEqual([attribute.token for attribute in attributes], ["vampirism", "rN+"])

    def test_artifact_parsing_functions_normalizes_step_boolean_and_penalty_values(self) -> None:
        artifact = get_txt_artifact_raw_info(
            "\n".join(
                [
                    "Inventory:",
                    ' a - the ring "Keus" {Stlth++ rPois- RegenMP+ +Inv -Tele}',
                    "     Stlth++: It makes you much more stealthy.",
                    "   Skills:",
                ]
            )
        )
        artifact = artifact[0]

        attributes = artifact_attributes(artifact["artifact_name"], artifact["visible_item_description"])

        self.assertEqual(
            [(attribute.token, attribute.key, attribute.value) for attribute in attributes],
            [
                ("Stlth++", "Stlth", 2),
                ("rPois-", "rPois", -1),
                ("RegenMP+", "RegenMP", True),
                ("+Inv", "+Inv", True),
                ("-Tele", "-Tele", True),
            ],
        )

    def test_artifact_parsing_functions_links_property_token_description_labels(self) -> None:
        artifact = get_txt_artifact_raw_info(
            "\n".join(
                [
                    "Inventory:",
                    ' a - the ring "Keus" {rF+ Will+ Stlth++ +Inv Fire}',
                    "     rF+: It protects you from fire.",
                    "       This line continues the fire description.",
                    "     Will+: It increases your willpower.",
                    "     Stlth++: It makes you much more stealthy.",
                    "     +Inv: It lets you turn invisible.",
                    "     Fire: It enhances your fire magic.",
                    "   Skills:",
                ]
            )
        )
        artifact = artifact[0]

        attributes = artifact_attributes(artifact["artifact_name"], artifact["visible_item_description"])
        descriptions = {
            attribute.token: attribute.description
            for attribute in attributes
        }

        self.assertEqual(
            descriptions["rF+"],
            "     rF+: It protects you from fire.",
        )
        self.assertEqual(
            descriptions["Will+"],
            "     Will+: It increases your willpower.",
        )
        self.assertEqual(
            descriptions["Stlth++"],
            "     Stlth++: It makes you much more stealthy.",
        )
        self.assertEqual(
            descriptions["+Inv"],
            "     +Inv: It lets you turn invisible.",
        )
        self.assertEqual(
            descriptions["Fire"],
            "     Fire: It enhances your fire magic.",
        )

    def test_artifact_parsing_functions_preserves_negative_property_description_lines(self) -> None:
        artifact = get_txt_artifact_raw_info(
            "\n".join(
                [
                    "Inventory:",
                    ' a - the ring "Risk" {-Tele *Slow}',
                    "     -Tele: It prevents most forms of teleportation.",
                    "       This line continues the teleport restriction.",
                    "     *Slow: It may slow you when you take damage.",
                    "   Skills:",
                ]
            )
        )[0]

        attributes = artifact_attributes(artifact["artifact_name"], artifact["visible_item_description"])
        descriptions = {
            attribute.token: attribute.description
            for attribute in attributes
        }

        self.assertEqual(artifact["visible_description_labels"], ["-Tele", "*Slow"])
        self.assertEqual(
            artifact["visible_item_description"],
            [
                "     -Tele: It prevents most forms of teleportation.",
                "       This line continues the teleport restriction.",
                "     *Slow: It may slow you when you take damage.",
            ],
        )
        self.assertEqual(
            descriptions["-Tele"],
            "     -Tele: It prevents most forms of teleportation.",
        )
        self.assertEqual(
            descriptions["*Slow"],
            "     *Slow: It may slow you when you take damage.",
        )


if __name__ == "__main__":
    unittest.main()
