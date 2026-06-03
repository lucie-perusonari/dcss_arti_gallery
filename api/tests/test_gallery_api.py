from __future__ import annotations

import unittest
from pathlib import Path

from fastapi.testclient import TestClient

from api.app import create_app
from api.tests.helpers import artifact_document
from api.tests.mongo_test_utils import (
    drop_repository_collections,
    insert_artifacts,
    mongo_repository_for_test,
)


class GalleryApiTest(unittest.TestCase):
    def setUp(self) -> None:
        self.repository = mongo_repository_for_test("api_test")

    def tearDown(self) -> None:
        drop_repository_collections(self.repository)

    def test_fastapi_gallery_endpoints_use_repository(self) -> None:
        weapon = artifact_document(
            name='the +6 broad axe "Axe" {heavy Slay+3 rF+ *Slow}',
            base_item="broad axe",
            item_class="weapon",
            item_subtype="broad axe",
            armour_slot=None,
            attributes=["heavy", "Slay+3", "rF+", "*Slow"],
        )
        ring = artifact_document(
            name='the ring "Miracles" {rCorr AC+4}',
            base_item="ring",
            item_class="jewellery",
            item_subtype="ring of protection",
            armour_slot=None,
            jewellery_slot="ring",
            base_subtype="ring of protection",
            attributes=["rCorr", "AC+4"],
            line_no=3,
        )
        weapon["_id"] = "mongo-internal-id"
        insert_artifacts(self.repository, [weapon, ring])
        client = TestClient(create_app(self.repository))

        list_response = client.get("/artifacts", params={"type": "weapon"})
        self.assertEqual(list_response.status_code, 200)
        self.assertEqual(len(list_response.json()["artifacts"]), 1)
        self.assertEqual(list_response.json()["artifacts"][0]["id"], weapon["id"])
        self.assertNotIn("_id", list_response.json()["artifacts"][0])
        self.assertEqual(list_response.json()["artifacts"][0]["baseItem"], "broad axe")
        self.assertEqual(list_response.json()["artifacts"][0]["type"], "weapon")
        self.assertTrue(
            list_response.json()["artifacts"][0]["tile"].startswith("/tiles/randart/weapon/broad-axe-")
        )
        self.assertEqual(list_response.json()["artifacts"][0]["score"]["total"], 42)
        self.assertIn("scoreImpact", list_response.json()["artifacts"][0]["attributes"][0])

        search_response = client.get("/artifacts", params={"q": "miracles"})
        self.assertEqual(search_response.status_code, 200)
        self.assertEqual(search_response.json()["artifacts"][0]["id"], ring["id"])

        detail_response = client.get(f"/artifacts/{ring['id']}")
        self.assertEqual(detail_response.status_code, 200)
        self.assertEqual(detail_response.json()["name"], ring["name"])
        self.assertIn("score", detail_response.json())
        self.assertTrue(detail_response.json()["tile"].startswith("/tiles/randart/ring/ring-"))

        missing_response = client.get("/artifacts/missing")
        self.assertEqual(missing_response.status_code, 404)

        self.assertEqual(client.get("/artifact-types").json(), ["all", "jewellery", "weapon"])
        self.assertEqual(client.get("/filters").json(), {"types": ["all", "jewellery", "weapon"]})

    def test_artifacts_endpoint_filters_by_player(self) -> None:
        wiiwiwi_artifact = artifact_document(
            name='the +1 cloak "Rain" {rPois}',
            source_name="morgue-wiiwiwi-20260516-185425.txt",
        )
        other_artifact = artifact_document(
            name='the +2 hat "Stars" {Int+4}',
            source_name="morgue-other-20260516-185425.txt",
            attributes=["Int+4"],
        )
        insert_artifacts(self.repository, [wiiwiwi_artifact, other_artifact])
        client = TestClient(create_app(self.repository))

        response = client.get("/artifacts", params={"player": "WIIWIWI"})

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            [artifact["id"] for artifact in response.json()["artifacts"]],
            [wiiwiwi_artifact["id"]],
        )

    def test_api_project_does_not_import_crawl_service(self) -> None:
        api_root = Path(__file__).resolve().parents[2] / "api"
        imports = "\n".join(path.read_text() for path in api_root.glob("*.py"))

        self.assertNotIn("crawl_service", imports)


if __name__ == "__main__":
    unittest.main()
