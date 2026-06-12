from __future__ import annotations

import unittest

from crawl_service.artifacts.constants import (
    BODY_ARMOUR_MARKERS,
    HELMET_ITEMS,
    UNRANDART_NAME_KEYS,
)


class DomainConstantsTest(unittest.TestCase):
    def test_generated_unrand_names_extend_unrand_filter_keys(self) -> None:
        self.assertIn("glaive of prune", UNRANDART_NAME_KEYS)
        self.assertIn("amulet of the four winds", UNRANDART_NAME_KEYS)

    def test_generated_armour_slots_extend_classifier_constants(self) -> None:
        self.assertIn("animal skin", BODY_ARMOUR_MARKERS)
        self.assertIn("cap", HELMET_ITEMS)


if __name__ == "__main__":
    unittest.main()
