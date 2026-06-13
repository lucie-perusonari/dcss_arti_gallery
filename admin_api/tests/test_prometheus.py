from __future__ import annotations

import unittest
from unittest.mock import patch

import httpx

from admin_api.prometheus import PrometheusGalleryApiMetricsRepository


class PrometheusGalleryApiMetricsRepositoryTest(unittest.TestCase):
    def test_queries_gallery_api_metrics(self) -> None:
        responses = iter(
            [
                _response("1.5"),
                _response("0.25"),
                _response("0.125"),
                _response("2"),
            ]
        )
        repository = PrometheusGalleryApiMetricsRepository("http://prometheus:9090")

        with patch("admin_api.prometheus.httpx.get", side_effect=lambda *args, **kwargs: next(responses)):
            metrics = repository.get_gallery_api_metrics()

        self.assertEqual(metrics.status, "ok")
        self.assertEqual(metrics.windowSeconds, 300)
        self.assertEqual(metrics.requestRatePerSecond, 1.5)
        self.assertEqual(metrics.errorRatePerSecond, 0.25)
        self.assertEqual(metrics.p95LatencySeconds, 0.125)
        self.assertEqual(metrics.inFlightRequests, 2.0)

    def test_returns_unavailable_when_prometheus_fails(self) -> None:
        repository = PrometheusGalleryApiMetricsRepository("http://prometheus:9090")

        with patch("admin_api.prometheus.httpx.get", side_effect=httpx.ConnectError("down")):
            metrics = repository.get_gallery_api_metrics()

        self.assertEqual(metrics.status, "unavailable")
        self.assertEqual(metrics.windowSeconds, 300)
        self.assertIsNone(metrics.requestRatePerSecond)
        self.assertIn("down", metrics.error or "")


def _response(value: str) -> httpx.Response:
    return httpx.Response(
        200,
        request=httpx.Request("GET", "http://prometheus:9090/api/v1/query"),
        json={
            "status": "success",
            "data": {
                "resultType": "vector",
                "result": [{"value": [1760000000, value]}],
            },
        },
    )


if __name__ == "__main__":
    unittest.main()
