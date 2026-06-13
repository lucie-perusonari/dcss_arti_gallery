from __future__ import annotations

import os
import unittest

from fastapi.testclient import TestClient

from api.app import create_app
from api.models import ArtifactDocument


class GalleryApiMetricsTest(unittest.TestCase):
    def setUp(self) -> None:
        self._previous_enabled = os.environ.get("ARTIFACT_API_METRICS_ENABLED")
        os.environ["ARTIFACT_API_METRICS_ENABLED"] = "1"

    def tearDown(self) -> None:
        if self._previous_enabled is None:
            os.environ.pop("ARTIFACT_API_METRICS_ENABLED", None)
        else:
            os.environ["ARTIFACT_API_METRICS_ENABLED"] = self._previous_enabled

    def test_metrics_endpoint_exports_gallery_api_metrics(self) -> None:
        client = TestClient(create_app(MetricsRepository()))

        response = client.get("/metrics")

        self.assertEqual(response.status_code, 200)
        self.assertIn("text/plain", response.headers["content-type"])
        self.assertIn("dcss_gallery_api_http_requests_total", response.text)
        self.assertIn("dcss_gallery_api_service_info", response.text)

    def test_success_and_not_found_requests_are_counted(self) -> None:
        client = TestClient(create_app(MetricsRepository()))

        self.assertEqual(client.get("/artifacts").status_code, 200)
        self.assertEqual(client.get("/missing").status_code, 404)
        metrics = client.get("/metrics").text

        self.assertIn(
            'dcss_gallery_api_http_requests_total{method="GET",route="/artifacts",status="200"} 1.0',
            metrics,
        )
        self.assertIn(
            'dcss_gallery_api_http_requests_total{method="GET",route="unmatched",status="404"} 1.0',
            metrics,
        )
        self.assertNotIn('route="/metrics"', metrics)


class MetricsRepository:
    def list_artifacts(
        self,
        query: str | None = None,
        item_type: str = "all",
        player: str | None = None,
    ) -> list[ArtifactDocument]:
        return []

    def get_artifact(self, artifact_id: str) -> ArtifactDocument | None:
        return None

    def list_artifact_types(self) -> list[str]:
        return ["all"]


if __name__ == "__main__":
    unittest.main()
