from __future__ import annotations

import re
import unittest
from pathlib import Path

from api.presenter import (
    RANDART_AMULET_TILES,
    RANDART_ARMOUR_TILES,
    RANDART_RING_TILES,
    RANDART_STAFF_TILES,
    RANDART_WEAPON_TILES,
    present_artifact_document,
)


EXPECTED_ARTIFACT_KEYS = {
    "id",
    "name",
    "baseItem",
    "type",
    "subtype",
    "weaponSubtype",
    "armourSubtype",
    "armourSlot",
    "jewellerySlot",
    "tile",
    "source",
    "allAttributes",
    "baseAttributes",
    "randomAttributes",
    "discovery",
    "score",
    "dcssDescription",
}

EXPECTED_SOURCE_KEYS = {"player", "url"}
EXPECTED_DISCOVERY_KEYS = {"version", "datetime"}
REMOVED_ARTIFACT_KEYS = {
    "attributes",
    "brand",
    "enchantment",
    "evaluation",
    "origin",
    "rawDescription",
}


class GalleryApiFrontendContractTest(unittest.TestCase):
    def test_presenter_outputs_only_frontend_artifact_contract_fields(self) -> None:
        artifact = present_artifact_document(_mongo_artifact_document()).model_dump()

        self.assertEqual(set(artifact), EXPECTED_ARTIFACT_KEYS)
        self.assertEqual(set(artifact["source"]), EXPECTED_SOURCE_KEYS)
        self.assertEqual(set(artifact["discovery"]), EXPECTED_DISCOVERY_KEYS)
        self.assertFalse(REMOVED_ARTIFACT_KEYS & set(artifact))
        self.assertEqual(artifact["allAttributes"], ["rF+", "Str+4"])
        self.assertEqual(artifact["baseAttributes"], ["rF+"])
        self.assertEqual(
            artifact["discovery"],
            {"version": "0.32.1", "datetime": "2026-05-16T18:54:25+00:00"},
        )
        self.assertTrue(artifact["dcssDescription"].startswith("[ring of protection from fire]\n"))

    def test_frontend_artifact_type_matches_api_contract_fields(self) -> None:
        frontend_type = _frontend_artifact_type_body()
        frontend_fields = set(re.findall(r"^  ([A-Za-z][A-Za-z0-9]*)\??:", frontend_type, re.MULTILINE))

        self.assertEqual(frontend_fields, EXPECTED_ARTIFACT_KEYS)
        self.assertFalse(REMOVED_ARTIFACT_KEYS & frontend_fields)
        self.assertRegex(
            frontend_type,
            r"source:\s*\{\s*player: string;\s*url\?: string \| null;\s*\};",
        )
        self.assertRegex(frontend_type, r"discovery:\s*ArtifactDiscovery;")

    def test_randart_tile_candidates_exist_as_frontend_assets(self) -> None:
        candidate_groups = [
            RANDART_RING_TILES,
            RANDART_AMULET_TILES,
            RANDART_STAFF_TILES,
            *RANDART_WEAPON_TILES.values(),
            *RANDART_ARMOUR_TILES.values(),
        ]
        missing_paths = [
            path
            for group in candidate_groups
            for path in group
            if not _frontend_public_path(path).exists()
        ]

        self.assertEqual(missing_paths, [])

    def test_randart_equipment_uses_randart_tiles(self) -> None:
        cases = [
            {
                "id": "randart-eudemon-blade",
                "name": 'the +8 eudemon blade "Beacon" {holy rF+}',
                "base_item": "eudemon blade",
                "item_class": "weapon",
                "item_subtype": "eudemon blade",
            },
            {
                "id": "randart-trishula",
                "name": 'the +7 trishula "Dawn" {flame rC+}',
                "base_item": "trishula",
                "item_class": "weapon",
                "item_subtype": "trishula",
            },
            {
                "id": "randart-plate-armour",
                "name": 'the +4 plate armour "Bulwark" {rN+ Str+3}',
                "base_item": "plate armour",
                "item_class": "armour",
                "item_subtype": "plate armour",
            },
            {
                "id": "randart-ring",
                "name": 'the ring "Spark" {rElec Will+}',
                "base_item": "ring",
                "item_class": "jewellery",
                "item_subtype": "ring of willpower",
                "jewellery_slot": "ring",
            },
            {
                "id": "randart-staff",
                "name": 'the staff "Channel" {rC+ Int+5}',
                "base_item": "staff",
                "item_class": "staff",
                "item_subtype": "staff",
            },
        ]

        for fields in cases:
            with self.subTest(fields["id"]):
                artifact = present_artifact_document(_mongo_artifact_document(**fields)).model_dump()
                self.assertTrue(artifact["tile"].startswith("/tiles/equipment/artifact/"))
                self.assertTrue(_frontend_public_path(artifact["tile"]).exists())


def _mongo_artifact_document(**overrides: object) -> dict:
    document = {
        "_id": "mongo-internal-id",
        "id": "the-ring-of-contracts",
        "name": 'the ring "Contracts" {rF+ Str+4}',
        "base_item": "ring",
        "item_class": "jewellery",
        "item_subtype": "ring of protection from fire",
        "base_subtype": "ring of protection from fire",
        "jewellery_slot": "ring",
        "enchantment": None,
        "brand": None,
        "origin": "removed from public contract",
        "source": {
            "player": "wiiwiwi",
            "file": "morgue-wiiwiwi-20260516-185425.txt",
            "url": "https://example.test/morgue.txt",
            "line": 42,
        },
        "first_source": {
            "player": "wiiwiwi",
            "file": "morgue-wiiwiwi-20260516-185425.txt",
            "url": "https://example.test/morgue.txt",
            "line": 42,
            "version": "0.32.1",
            "game_ended_at": "2026-05-16T18:54:25+00:00",
        },
        "attributes": [
            {"token": "rF+", "key": "rF", "value": 1, "description": ""},
            {"token": "Str+4", "key": "Str", "value": 4, "description": ""},
        ],
        "all_attributes": ["rF+", "Str+4"],
        "base_attributes": ["rF+"],
        "random_attributes": ["rF+", "Str+4"],
        "all_attribute_text": "rF+ Str+4",
        "base_attribute_text": "",
        "random_attribute_text": "rF+ Str+4",
        "evaluation": {
            "total": 42,
            "practical_score": 31,
            "rarity_score": 11,
            "offense": 0,
            "defense": 8,
            "utility": 4,
            "penalty": 0,
            "base_fit": 12,
            "grade": "좋음",
            "luxury_grade": None,
        },
        "rawDescription": ["removed from public contract"],
        "visible_item_description": [
            "rF+: It protects you from fire.",
            "Str+4: It affects your strength (+4).",
        ],
        "raw_text_block": 'the ring "Contracts" {rF+ Str+4}',
    }
    document.update(overrides)
    return document


def _frontend_artifact_type_body() -> str:
    artifact_type_path = Path(__file__).resolve().parents[2] / "frontend/src/types/artifact.ts"
    source = artifact_type_path.read_text(encoding="utf-8")
    match = re.search(r"export type Artifact = \{(?P<body>.*?)\n\};", source, re.DOTALL)
    if not match:
        raise AssertionError("frontend Artifact type was not found")
    return match.group("body")


def _frontend_public_path(public_path: str) -> Path:
    if not public_path.startswith("/"):
        raise AssertionError(f"expected absolute public path: {public_path}")
    return Path(__file__).resolve().parents[2] / "frontend/public" / public_path.removeprefix("/")


if __name__ == "__main__":
    unittest.main()
