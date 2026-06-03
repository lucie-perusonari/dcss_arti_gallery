from __future__ import annotations

import unittest

from crawl_service.domain.artifacts.filter import is_random_artifact_info
from crawl_service.domain.artifacts.info_parser import parse_artifact_info
from crawl_service.domain.artifacts.raw_parser import get_txt_artifact_raw_info


def artifact_info_from_inventory_line(line: str):
    raw_info = get_txt_artifact_raw_info(f"Inventory:\n{line}\n   Skills:")[0]
    return parse_artifact_info(raw_info)


class ArtifactFilterTest(unittest.TestCase):
    def test_known_fixed_unrandarts_are_not_random_artifacts(self) -> None:
        cases = [
            " a - the +8 orange crystal plate armour {Archmagi, Int+3 Clar}",
            " b - the +3 hat of Pondering {Ponderous, Will+ MP+10 Int+5}",
            ' c - the sword of the Dread Knight {decimate ^Drain *Silence Will+}',
            " d - the Charlatan's Orb {orb Charlatan}",
        ]

        for line in cases:
            with self.subTest(line=line):
                self.assertFalse(is_random_artifact_info(artifact_info_from_inventory_line(line)))

    def test_named_randarts_still_pass_filter(self) -> None:
        info = artifact_info_from_inventory_line(
            ' a - the +6 broad axe "Axe" {heavy Slay+3 rF+ *Slow}'
        )

        self.assertTrue(is_random_artifact_info(info))

    def test_ashenzari_stat_magic_items_are_not_random_artifacts(self) -> None:
        cases = [
            (
                " a - the cursed +2 helmet of intelligence {Int+3, Fort}\n"
                "     [helmet of intelligence]"
            ),
            (
                " b - the cursed ring of protection {AC+4, Self}\n"
                "     [ring of protection]"
            ),
        ]

        for line in cases:
            with self.subTest(line=line):
                self.assertFalse(is_random_artifact_info(artifact_info_from_inventory_line(line)))

    def test_bracket_subtype_does_not_exclude_quoted_randarts(self) -> None:
        info = artifact_info_from_inventory_line(
            ' a - the ring "Jiogot" {rCorr AC+4}\n'
            "     [ring of protection]"
        )

        self.assertTrue(is_random_artifact_info(info))

    def test_cursed_named_randarts_still_pass_filter(self) -> None:
        info = artifact_info_from_inventory_line(
            " a - the cursed +9 broad axe of Supernal Understanding {speed, rPois Dex+8}"
        )

        self.assertTrue(is_random_artifact_info(info))


if __name__ == "__main__":
    unittest.main()
