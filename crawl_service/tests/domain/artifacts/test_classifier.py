from __future__ import annotations

import unittest

from crawl_service.domain.artifacts.classifier import build_random_artifact
from crawl_service.domain.artifacts.info_parser import parse_artifact_info
from crawl_service.domain.artifacts.raw_parser import (
    get_lst_artifact_raw_info,
    get_txt_artifact_raw_info,
)
from crawl_service.domain.artifacts.types import RandomArtifact


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
SAMPLE_LST = "\n".join(
    [
        "Level 4 of the Dungeon",
        "[Shop] Ufeuf's Jewellery",
        "  the fire staff of the First Visions {rF+ Fire Stlth+ Ice Air}",
        "    [staff of fire]",
        "(3, 7, D:5)",
        "  the inkwell talisman of Soss {Will+}",
        "    [inkwell talisman]",
        "  the +6 shortbow of Ugus {heavy Dex+2}",
    ]
)


def random_artifact_from_inventory_lines(lines: list[str]) -> RandomArtifact:
    raw_info = get_txt_artifact_raw_info("\n".join(["Inventory:", *lines, "   Skills:"]))[0]
    return build_random_artifact(parse_artifact_info(raw_info))


class ArtifactClassifierTest(unittest.TestCase):
    def test_build_random_artifact_returns_document_friendly_object(self) -> None:
        artifacts = get_txt_artifact_raw_info(SAMPLE_TXT)

        random_artifact = build_random_artifact(parse_artifact_info(artifacts[0]))

        self.assertIsInstance(random_artifact, RandomArtifact)
        self.assertEqual(random_artifact.item_class, "weapon")
        self.assertEqual(random_artifact.weapon_subtype, "melee")
        self.assertIsNone(random_artifact.armour_slot)
        self.assertEqual(random_artifact.base_item, "broad axe")
        self.assertEqual(random_artifact.enchantment, 6)
        self.assertEqual(random_artifact.all_attribute_text, "chaos, rC+, Str+3, Stlth+")

    def test_brand_is_split_to_field_and_kept_as_attribute_token(self) -> None:
        random_artifact = random_artifact_from_inventory_lines(
            [
                ' a - the +1 trishula "Dawn" {holy wrath, rF-, Str+3, *Slow}',
            ]
        )

        self.assertEqual(random_artifact.brand, "holy wrath")
        self.assertEqual(
            random_artifact.random_attributes,
            ["holy wrath", "rF-", "Str+3", "*Slow"],
        )
        self.assertIn("holy wrath", random_artifact.all_attributes)

    def test_of_brand_is_split_even_when_not_in_property_braces(self) -> None:
        random_artifact = random_artifact_from_inventory_lines(
            [
                ' a - the +9 broad axe of holy wrath "Dawn" {rN+}',
            ]
        )

        self.assertEqual(random_artifact.brand, "holy wrath")
        self.assertEqual(random_artifact.all_attributes, ["rN+", "holy wrath"])
        self.assertEqual(random_artifact.random_attribute_text, "rN+, holy wrath")

    def test_subtype_intrinsics_are_base_attributes_not_random_attributes(self) -> None:
        ring = random_artifact_from_inventory_lines(
            [
                ' a - the ring "Miracles" {rCorr AC+4}',
                "     [ring of protection]",
                "     AC+4: It affects your AC (+4).",
            ]
        )
        amulet = random_artifact_from_inventory_lines(
            [
                ' a - the amulet "Buosiylo" {Reflect Rampage rC++ Regen+ SH+5}',
                "     [amulet of reflection]",
                "     Reflect: It reflects blocked missile attacks.",
            ]
        )

        self.assertEqual(ring.base_subtype, "ring of protection")
        self.assertEqual(ring.base_attributes, ["AC+4"])
        self.assertEqual(ring.random_attributes, ["rCorr"])
        self.assertEqual(ring.base_attribute_text, "AC+4")
        self.assertEqual(ring.random_attribute_text, "rCorr")

        self.assertEqual(amulet.base_attributes, ["Reflect", "SH+5"])
        self.assertEqual(amulet.random_attributes, ["Rampage", "rC++", "Regen+"])

    def test_staff_base_subtype_intrinsics_are_base_attributes(self) -> None:
        artifacts = get_lst_artifact_raw_info(SAMPLE_LST)
        staff_artifact = next(
            artifact
            for artifact in artifacts
            if artifact.artifact_name.startswith("the fire staff of the First Visions")
        )

        random_artifact = build_random_artifact(parse_artifact_info(staff_artifact))

        self.assertEqual(random_artifact.base_attributes, ["rF+", "Fire"])
        self.assertEqual(random_artifact.random_attributes, ["Stlth+", "Ice", "Air"])
        self.assertEqual(random_artifact.item_class, "staff")
        self.assertEqual(random_artifact.item_subtype, "staff of fire")

    def test_troll_leather_armour_base_intrinsic_is_added_when_not_visible(self) -> None:
        random_artifact = random_artifact_from_inventory_lines(
            [
                ' a - the +2 troll leather armour "Root" {rC+ Slay+2}',
            ]
        )

        self.assertEqual(random_artifact.item_class, "armour")
        self.assertEqual(random_artifact.armour_slot, "body armour")
        self.assertEqual(random_artifact.base_attributes, ["Regen+"])
        self.assertEqual(random_artifact.random_attributes, ["rC+", "Slay+2"])
        self.assertEqual(random_artifact.all_attributes, ["rC+", "Slay+2", "Regen+"])

    def test_classifier_identifies_jewellery_talisman_and_ranged_weapon(self) -> None:
        txt_artifacts = get_txt_artifact_raw_info(SAMPLE_TXT)
        jewellery_artifact = next(
            artifact
            for artifact in txt_artifacts
            if artifact.artifact_name.startswith('the ring "Jiogot"')
        )
        jewellery = build_random_artifact(parse_artifact_info(jewellery_artifact))

        lst_artifacts = get_lst_artifact_raw_info(SAMPLE_LST)
        talisman_artifact = next(
            artifact
            for artifact in lst_artifacts
            if artifact.artifact_name.startswith("the inkwell talisman of Soss")
        )
        talisman = build_random_artifact(parse_artifact_info(talisman_artifact))
        ranged_artifact = next(
            artifact
            for artifact in lst_artifacts
            if artifact.artifact_name.startswith('the +6 shortbow of Ugus')
        )
        ranged = build_random_artifact(parse_artifact_info(ranged_artifact))

        self.assertEqual(jewellery.item_class, "jewellery")
        self.assertEqual(jewellery.jewellery_slot, "ring")
        self.assertEqual(talisman.item_class, "talisman")
        self.assertEqual(talisman.item_subtype, "inkwell talisman")
        self.assertEqual(ranged.item_class, "weapon")
        self.assertEqual(ranged.weapon_subtype, "ranged")


if __name__ == "__main__":
    unittest.main()
