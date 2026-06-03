from __future__ import annotations

import re
import unittest

from crawl_service.domain.artifacts.info_parser import parse_artifact_info
from crawl_service.domain.artifacts.raw_parser import (
    get_artifact_raw_info,
    get_lst_artifact_raw_info,
    get_txt_artifact_raw_info,
)
from crawl_service.domain.artifacts.types import ArtifactRawTextInput


SAMPLE_TXT_NAME = ".morgue-wiiwiwi-20260516-185425.txt"
SAMPLE_LST_NAME = ".morgue-wiiwiwi-20260516-185425.lst"
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
DESC_RE = re.compile(r"^\s+(?P<label>[+*^A-Za-z][^:]*):\s+")
BRACKET_RE = re.compile(r"^\s+\[(?P<subtype>[^]]+)\]\s*$")
PREFIX_RE = re.compile(r"^\s*(?:[A-Za-z] - )?(?P<title>the .*\{[^{}]+\}).*$")
WORN_RE = re.compile(r"\s+\([^)]*\)(?=\s*\{)")
PRICE_RE = re.compile(r"\s+\(\d+ gold\)\s*$")


def raw_title_count(text: str, pattern: re.Pattern[str]) -> int:
    return sum(1 for line in text.splitlines() if pattern.match(line))


def assert_matches_raw_block(testcase: unittest.TestCase, lines: list[str], artifact) -> None:
    block_lines = artifact.raw_text_block.splitlines()
    start = artifact.line_no - 1

    testcase.assertEqual(lines[start : start + len(block_lines)], block_lines)
    title_match = PREFIX_RE.match(block_lines[0])
    testcase.assertIsNotNone(title_match)
    raw_title = PRICE_RE.sub("", WORN_RE.sub("", title_match.group("title"))).strip()
    testcase.assertEqual(artifact.artifact_name, raw_title)

    raw_labels = [
        match.group("label").strip()
        for line in block_lines[1:]
        if (match := DESC_RE.match(line))
    ]
    testcase.assertEqual(artifact.visible_description_labels, raw_labels)

    raw_description_lines = []
    current_description = False
    for line in block_lines[1:]:
        if DESC_RE.match(line):
            raw_description_lines.append(line.rstrip())
            current_description = True
            continue
        if current_description and line.startswith(" ") and line.strip():
            raw_description_lines.append(line.rstrip())
            continue
        current_description = False
    testcase.assertEqual(artifact.visible_item_description, raw_description_lines)

    raw_subtypes = [
        match.group("subtype")
        for line in block_lines[1:]
        if (match := BRACKET_RE.match(line))
    ]
    testcase.assertEqual(artifact.bracket_subtype, raw_subtypes[-1] if raw_subtypes else None)


class ArtifactParserTest(unittest.TestCase):
    def test_txt_block_extraction_uses_inventory_section(self) -> None:
        artifacts = get_txt_artifact_raw_info(
            "\n".join(
                [
                    "Outside inventory:",
                    " a - the ignored item {rF+}",
                    "Inventory:",
                    " a - the ring \"Keus\" {rPois rC+}",
                    "     Found on D:4.",
                    " b - a +0 robe",
                    "   Skills:",
                    " c - the ignored post-skill item {rN+}",
                ]
            )
        )

        self.assertEqual(len(artifacts), 1)
        self.assertEqual(artifacts[0].line_no, 4)
        self.assertEqual(artifacts[0].item_location, None)
        self.assertEqual(artifacts[0].item_source, None)
        self.assertEqual(artifacts[0].raw_text_block.splitlines()[0], ' a - the ring "Keus" {rPois rC+}')

    def test_lst_block_extraction_preserves_location_and_shop_context(self) -> None:
        artifacts = get_lst_artifact_raw_info(
            "\n".join(
                [
                    "Level 4 of the Dungeon",
                    "[Shop] Ufeuf's Jewellery",
                    "  the ring \"Keus\" {rPois rC+}",
                    "    Willpower: It increases your willpower.",
                    "(3, 7, D:5)",
                    "  the amulet \"Orgh\" {Regen+}",
                ]
            )
        )

        self.assertEqual(len(artifacts), 2)
        self.assertEqual(artifacts[0].line_no, 3)
        self.assertEqual(
            artifacts[0].item_location,
            "Level 4 of the Dungeon [Shop] Ufeuf's Jewellery",
        )
        self.assertEqual(artifacts[0].item_source, "[Shop] Ufeuf's Jewellery")
        self.assertEqual(artifacts[1].line_no, 6)
        self.assertEqual(artifacts[1].item_location, "(3, 7, D:5)")
        self.assertIsNone(artifacts[1].item_source)

    def test_info_builder_creates_raw_info_from_block(self) -> None:
        artifacts = get_txt_artifact_raw_info(
            "\n".join(
                [
                    "Inventory:",
                    ' a - the +3 hat "Vubbo" {rF+ rC+}',
                    "     (Found on D:4.)",
                    "     [hat]",
                    "     Fire: It protects you from fire.",
                    "       This line continues the description.",
                    "   Skills:",
                ]
            )
        )
        artifact = artifacts[0]

        self.assertIsNone(artifact.source_name)
        self.assertIsNone(artifact.source_url)
        self.assertEqual(artifact.line_no, 2)
        self.assertEqual(artifact.artifact_name, 'the +3 hat "Vubbo" {rF+ rC+}')
        self.assertEqual(artifact.item_source, "Found on D:4.")
        self.assertEqual(artifact.bracket_subtype, "hat")
        self.assertEqual(artifact.visible_description_labels, ["Fire"])
        self.assertEqual(
            artifact.visible_item_description,
            [
                "     Fire: It protects you from fire.",
                "       This line continues the description.",
            ],
        )

    def test_txt_artifacts_match_raw_inventory_blocks(self) -> None:
        artifacts = get_txt_artifact_raw_info(SAMPLE_TXT)

        self.assertEqual(
            len(artifacts),
            raw_title_count(SAMPLE_TXT, re.compile(r"^\s*[A-Za-z] - the .*\{[^{}]+\}")),
        )
        self.assertEqual(len(artifacts), 2)

        for artifact in artifacts:
            with self.subTest(artifact=artifact.artifact_name):
                self.assertIsNone(artifact.source_name)
                self.assertIsNone(artifact.source_url)
                self.assertIsNone(artifact.item_location)
                self.assertIsNotNone(artifact.item_source)
                assert_matches_raw_block(self, SAMPLE_TXT.splitlines(), artifact)

    def test_lst_artifacts_match_raw_location_blocks(self) -> None:
        artifacts = get_lst_artifact_raw_info(SAMPLE_LST)

        self.assertEqual(
            len(artifacts),
            raw_title_count(SAMPLE_LST, re.compile(r"^\s+the .*\{[^{}]+\}")),
        )
        self.assertEqual(len(artifacts), 3)

        for artifact in artifacts:
            with self.subTest(artifact=artifact.artifact_name):
                self.assertIsNone(artifact.source_name)
                self.assertIsNone(artifact.source_url)
                self.assertIsNotNone(artifact.item_location)
                assert_matches_raw_block(self, SAMPLE_LST.splitlines(), artifact)

        shop_artifacts = [artifact for artifact in artifacts if artifact.item_source]
        self.assertEqual(len(shop_artifacts), 1)
        self.assertTrue(all(artifact.item_source.startswith("[Shop]") for artifact in shop_artifacts))

    def test_parser_does_not_treat_string_as_path(self) -> None:
        artifacts = get_txt_artifact_raw_info(SAMPLE_TXT_NAME)

        self.assertEqual(artifacts, [])

    def test_parser_converts_txt_fetch_raw_to_artifact_raw_info(self) -> None:
        raw = ArtifactRawTextInput(
            name=SAMPLE_TXT_NAME,
            url="https://example.test/morgue.txt",
            extension="txt",
            text=SAMPLE_TXT,
        )

        artifacts = get_artifact_raw_info(raw)

        self.assertEqual(len(artifacts), 2)
        self.assertTrue(all(artifact.source_name == raw.name for artifact in artifacts))
        self.assertTrue(all(artifact.source_url == raw.url for artifact in artifacts))
        assert_matches_raw_block(self, SAMPLE_TXT.splitlines(), artifacts[0])

    def test_parser_converts_multiple_fetch_raws_to_artifact_raw_info(self) -> None:
        txt_raw = ArtifactRawTextInput(
            name=SAMPLE_TXT_NAME,
            url="https://example.test/morgue.txt",
            extension="txt",
            text=SAMPLE_TXT,
        )
        lst_raw = ArtifactRawTextInput(
            name=SAMPLE_LST_NAME,
            url="https://example.test/morgue.lst",
            extension="lst",
            text=SAMPLE_LST,
        )

        artifacts = [*get_artifact_raw_info(txt_raw), *get_artifact_raw_info(lst_raw)]

        self.assertEqual(len(artifacts), 5)
        self.assertEqual(artifacts[0].source_name, txt_raw.name)
        self.assertEqual(artifacts[-1].source_name, lst_raw.name)

    def test_parser_rejects_unknown_fetch_raw_extension(self) -> None:
        raw = ArtifactRawTextInput(
            name="morgue.html",
            url="https://example.test/morgue.html",
            extension="html",
            text="",
        )

        with self.assertRaisesRegex(ValueError, "unsupported morgue raw extension"):
            get_artifact_raw_info(raw)

    def test_parse_artifact_info_tokenizes_properties_and_base_item(self) -> None:
        artifact = get_txt_artifact_raw_info(SAMPLE_TXT)[0]

        info = parse_artifact_info(artifact)

        self.assertEqual(info.display_name, '+6 broad axe of Plog')
        self.assertEqual(info.base_item, "broad axe")
        self.assertEqual(info.enchantment, 6)
        self.assertEqual(
            [attribute.token for attribute in info.attributes],
            ["chaos", "rC+", "Str+3", "Stlth+"],
        )
        self.assertEqual(info.attributes[1].key, "rC")
        self.assertEqual(info.attributes[1].value, 1)
        self.assertEqual(info.attributes[2].value, 3)

    def test_parse_artifact_info_handles_cursed_and_negative_enchantments(self) -> None:
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

        cursed_weapon = parse_artifact_info(artifacts[0])
        negative_armour = parse_artifact_info(artifacts[1])

        self.assertEqual(cursed_weapon.enchantment, 9)
        self.assertEqual(cursed_weapon.base_item, "broad axe")
        self.assertEqual(negative_armour.enchantment, -2)
        self.assertEqual(negative_armour.base_item, "hat")

    def test_parse_artifact_info_preserves_known_multi_word_properties(self) -> None:
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

        info = parse_artifact_info(artifact)
        singing_sword_info = parse_artifact_info(singing_sword)

        self.assertEqual([attribute.token for attribute in info.attributes], ["holy wrath", "rN+"])
        self.assertEqual([attribute.token for attribute in singing_sword_info.attributes], ["sonic wave"])

    def test_parse_artifact_info_splits_first_comma_group_and_drops_internal_tags(self) -> None:
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

        info = parse_artifact_info(artifact)

        self.assertEqual([attribute.token for attribute in info.attributes], ["Rampage", "rCorr", "Int+2"])

    def test_parse_artifact_info_drops_lowercase_internal_tags_without_dropping_vampirism(self) -> None:
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

        info = parse_artifact_info(artifact)

        self.assertEqual([attribute.token for attribute in info.attributes], ["vampirism", "rN+"])


if __name__ == "__main__":
    unittest.main()
