from __future__ import annotations

import unittest

from crawl_service.morgue.types import MorgueRawText
from crawl_service.core.processor import ArtifactProcessor


def documents_from_lines(lines: list[str]):
    return ArtifactProcessor().documents_from_raw_text(
        MorgueRawText(
            name="morgue-test-20260101-000001.txt",
            url="https://example.test/morgue.txt",
            extension="txt",
            text="\n".join(["Inventory:", *lines, "   Skills:"]),
        )
    )


class ArtifactFilterTest(unittest.TestCase):
    def test_filter_excludes_fixed_unrandarts(self) -> None:
        documents = documents_from_lines(
            [
                ' a - the +4 dagger "Morg" {pain, Will+ Int+5}',
                " b - the +3 hat of Pondering {Ponderous, Will+ MP+10 Int+5}",
                ' c - the sword of the Dread Knight {decimate ^Drain *Silence Will+}',
            ]
        )

        self.assertEqual(documents, [])

    def test_filter_excludes_sprint(self) -> None:
        documents = documents_from_lines(
            [" a - the sprint {rF+, Str+1}"]
        )

        self.assertEqual(documents, [])

    def test_filter_keeps_quoted_randart_weapon(self) -> None:
        documents = documents_from_lines(
            [' a - the +6 broad axe "Axe" {heavy Slay+3 rF+ *Slow}']
        )

        self.assertEqual(len(documents), 1)
        self.assertEqual(documents[0].base_item, "broad axe")

    def test_filter_excludes_plain_magic_item_with_bracket_subtype(self) -> None:
        documents = documents_from_lines(
            [
                " a - the cursed ring of protection {AC+4, Self}",
                "     [ring of protection]",
            ]
        )

        self.assertEqual(documents, [])

    def test_bracket_subtype_does_not_exclude_quoted_randarts(self) -> None:
        documents = documents_from_lines(
            [
                ' a - the ring "Jiogot" {rCorr AC+4}',
                "     [ring of protection]",
            ]
        )

        self.assertEqual(len(documents), 1)
        self.assertEqual(documents[0].base_subtype, "ring of protection")

    def test_filter_keeps_unquoted_randart_with_distinct_name(self) -> None:
        documents = documents_from_lines(
            [
                " a - the cursed +9 broad axe of Supernal Understanding {speed, rPois Dex+8}"
            ]
        )

        self.assertEqual(len(documents), 1)
        self.assertEqual(documents[0].base_item, "broad axe")


if __name__ == "__main__":
    unittest.main()
