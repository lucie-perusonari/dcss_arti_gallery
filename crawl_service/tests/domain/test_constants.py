from __future__ import annotations

import unittest

from crawl_service.domain.constants import (
    BODY_ARMOUR_MARKERS,
    HELMET_ITEMS,
    ITEM_FLAVOUR_TEXT,
    UNRANDART_NAME_KEYS,
)


class DomainConstantsTest(unittest.TestCase):
    def test_generated_dcss_descriptions_extend_item_flavour_text(self) -> None:
        self.assertIn("animal skin", ITEM_FLAVOUR_TEXT)
        self.assertIn("book of annihilations", ITEM_FLAVOUR_TEXT)
        self.assertIn("gell's gravitambourine", ITEM_FLAVOUR_TEXT)

    def test_generated_unrand_names_extend_unrand_filter_keys(self) -> None:
        self.assertIn("glaive of prune", UNRANDART_NAME_KEYS)
        self.assertIn("amulet of the four winds", UNRANDART_NAME_KEYS)

    def test_generated_armour_slots_extend_classifier_constants(self) -> None:
        self.assertIn("animal skin", BODY_ARMOUR_MARKERS)
        self.assertIn("cap", HELMET_ITEMS)


if __name__ == "__main__":
    unittest.main()
