from __future__ import annotations

import re
import unittest
from pathlib import Path

from api.presenter import present_artifact_document


EXPECTED_ARTIFACT_KEYS = {
    "id",
    "name",
    "baseItem",
    "type",
    "subtype",
    "weaponSubtype",
    "armourSlot",
    "jewellerySlot",
    "tile",
    "source",
    "randomAttributes",
    "score",
    "dcssDescription",
}

EXPECTED_SOURCE_KEYS = {"player"}
REMOVED_ARTIFACT_KEYS = {
    "allAttributes",
    "attributes",
    "baseAttributes",
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
        self.assertFalse(REMOVED_ARTIFACT_KEYS & set(artifact))

    def test_frontend_artifact_type_matches_api_contract_fields(self) -> None:
        frontend_type = _frontend_artifact_type_body()
        frontend_fields = set(re.findall(r"^  ([A-Za-z][A-Za-z0-9]*)\??:", frontend_type, re.MULTILINE))

        self.assertEqual(frontend_fields, EXPECTED_ARTIFACT_KEYS)
        self.assertFalse(REMOVED_ARTIFACT_KEYS & frontend_fields)
        self.assertRegex(frontend_type, r"source:\s*\{\s*player: string;\s*\};")


def _mongo_artifact_document() -> dict:
    return {
        "_id": "mongo-internal-id",
        "id": "the-ring-of-contracts",
        "name": 'the ring "Contracts" {rF+ Str+4}',
        "base_item": "ring",
        "item_class": "jewellery",
        "item_subtype": "ring of strength",
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
        "attributes": [
            {"token": "rF+", "key": "rF", "value": 1, "description": ""},
            {"token": "Str+4", "key": "Str", "value": 4, "description": ""},
        ],
        "all_attributes": ["rF+", "Str+4"],
        "base_attributes": [],
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


def _frontend_artifact_type_body() -> str:
    artifact_type_path = Path(__file__).resolve().parents[2] / "frontend/src/types/artifact.ts"
    source = artifact_type_path.read_text(encoding="utf-8")
    match = re.search(r"export type Artifact = \{(?P<body>.*?)\n\};", source, re.DOTALL)
    if not match:
        raise AssertionError("frontend Artifact type was not found")
    return match.group("body")


if __name__ == "__main__":
    unittest.main()
