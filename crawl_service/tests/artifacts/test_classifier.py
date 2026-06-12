from __future__ import annotations

import unittest

from crawl_service.morgue.types import MorgueRawText
from crawl_service.core.processor import ArtifactProcessor


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


def documents_from_inventory_lines(lines: list[str]):
    return ArtifactProcessor().documents_from_raw_text(
        MorgueRawText(
            name="morgue-test-20260101-000001.txt",
            url="https://example.test/morgue.txt",
            extension="txt",
            text="\n".join(["Inventory:", *lines, "   Skills:"]),
        )
    )


class ArtifactClassifierTest(unittest.TestCase):
    def test_processor_returns_document_friendly_classification(self) -> None:
        document = documents_from_inventory_lines(
            [' a - the +6 broad axe of Plog {chaos rC+ Str+3 Stlth+}']
        )[0]

        self.assertEqual(document.item_class, "weapon")
        self.assertEqual(document.weapon_subtype, "melee")
        self.assertIsNone(document.armour_slot)
        self.assertEqual(document.base_item, "broad axe")
        self.assertEqual(document.enchantment, 6)
        self.assertEqual(document.all_attribute_text, "chaos, rC+, Str+3, Stlth+")

    def test_brand_is_split_to_field_and_kept_as_attribute_token(self) -> None:
        document = documents_from_inventory_lines(
            [' a - the +1 trishula "Dawn" {holy wrath, rF-, Str+3, *Slow}']
        )[0]

        self.assertEqual(document.brand, "holy wrath")
        self.assertEqual(
            document.random_attributes,
            ["holy wrath", "rF-", "Str+3", "*Slow"],
        )
        self.assertIn("holy wrath", document.all_attributes)

    def test_of_brand_is_split_even_when_not_in_property_braces(self) -> None:
        document = documents_from_inventory_lines(
            [' a - the +9 broad axe of holy wrath "Dawn" {rN+}']
        )[0]

        self.assertEqual(document.brand, "holy wrath")
        self.assertEqual(document.all_attributes, ["rN+", "holy wrath"])
        self.assertEqual(document.random_attribute_text, "rN+, holy wrath")

    def test_subtype_intrinsics_are_base_attributes_not_random_attributes(self) -> None:
        documents = documents_from_inventory_lines(
            [
                ' a - the ring "Miracles" {rCorr AC+4}',
                "     [ring of protection]",
                "     AC+4: It affects your AC (+4).",
                ' b - the amulet "Buosiylo" {Reflect Rampage rC++ Regen+ SH+5}',
                "     [amulet of reflection]",
                "     Reflect: It reflects blocked missile attacks.",
            ]
        )
        ring = next(document for document in documents if document.name.startswith('the ring "Miracles"'))
        amulet = next(document for document in documents if document.name.startswith('the amulet "Buosiylo"'))

        self.assertEqual(ring.base_subtype, "ring of protection")
        self.assertEqual(ring.base_attributes, ["AC+4"])
        self.assertEqual(ring.random_attributes, ["rCorr"])
        self.assertEqual(ring.base_attribute_text, "AC+4")
        self.assertEqual(ring.random_attribute_text, "rCorr")

        self.assertEqual(amulet.base_attributes, ["Reflect", "SH+5"])
        self.assertEqual(amulet.random_attributes, ["Rampage", "rC++", "Regen+"])

    def test_staff_base_subtype_intrinsics_are_base_attributes(self) -> None:
        documents = ArtifactProcessor().documents_from_raw_text(
            MorgueRawText(
                name="morgue-test-20260101-000001.lst",
                url="https://example.test/morgue.lst",
                extension="lst",
                text=SAMPLE_LST,
            )
        )
        staff = next(
            document
            for document in documents
            if document.name.startswith("the fire staff of the First Visions")
        )

        self.assertEqual(staff.base_attributes, ["rF+", "Fire"])
        self.assertEqual(staff.random_attributes, ["Stlth+", "Ice", "Air"])
        self.assertEqual(staff.item_class, "staff")
        self.assertEqual(staff.item_subtype, "staff of fire")

    def test_troll_leather_armour_base_intrinsic_is_added_when_not_visible(self) -> None:
        document = documents_from_inventory_lines(
            [' a - the +2 troll leather armour "Root" {rC+ Slay+2}']
        )[0]

        self.assertEqual(document.item_class, "armour")
        self.assertEqual(document.armour_slot, "body armour")
        self.assertEqual(document.base_attributes, ["Regen+"])
        self.assertEqual(document.random_attributes, ["rC+", "Slay+2"])
        self.assertEqual(document.all_attributes, ["rC+", "Slay+2", "Regen+"])

    def test_classifier_identifies_jewellery_talisman_and_ranged_weapon(self) -> None:
        txt_documents = ArtifactProcessor().documents_from_raw_text(
            MorgueRawText(
                name="morgue-test-20260101-000001.txt",
                url="https://example.test/morgue.txt",
                extension="txt",
                text=SAMPLE_TXT,
            )
        )
        jewellery = next(
            document
            for document in txt_documents
            if document.name.startswith('the ring "Jiogot"')
        )

        lst_documents = ArtifactProcessor().documents_from_raw_text(
            MorgueRawText(
                name="morgue-test-20260101-000001.lst",
                url="https://example.test/morgue.lst",
                extension="lst",
                text=SAMPLE_LST,
            )
        )
        talisman = next(
            document
            for document in lst_documents
            if document.name.startswith("the inkwell talisman of Soss")
        )
        ranged = next(
            document
            for document in lst_documents
            if document.name.startswith("the +6 shortbow of Ugus")
        )

        self.assertEqual(jewellery.item_class, "jewellery")
        self.assertEqual(jewellery.jewellery_slot, "ring")
        self.assertEqual(talisman.item_class, "talisman")
        self.assertEqual(talisman.item_subtype, "inkwell talisman")
        self.assertEqual(ranged.item_class, "weapon")
        self.assertEqual(ranged.weapon_subtype, "ranged")


if __name__ == "__main__":
    unittest.main()
