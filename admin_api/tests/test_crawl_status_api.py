from __future__ import annotations

import unittest

from fastapi.testclient import TestClient

from admin_api.app import create_app
from admin_api.models import CrawlStatus, GalleryApiMetrics, LatestActivity, RawFileStatus
from admin_api.tests.mongo_test_utils import (
    drop_crawl_status_repository_collections,
    mongo_crawl_status_repository_for_test,
)


class AdminCrawlStatusApiTest(unittest.TestCase):
    def setUp(self) -> None:
        self.repository = mongo_crawl_status_repository_for_test("admin_api_test")

    def tearDown(self) -> None:
        drop_crawl_status_repository_collections(self.repository)

    def test_admin_crawl_status_summarizes_crawl_collections(self) -> None:
        self.repository.artifacts_collection.insert_many([{"id": "artifact-1"}])
        self.repository.raw_files_collection.insert_many(
            [
                {
                    "player": "wiiwiwi",
                    "name": "morgue-wiiwiwi-20260101-000001.txt",
                    "fetch_status": "fetched",
                    "process_status": "processed",
                    "fetched_at": "2026-01-01T00:00:00+00:00",
                    "processed_at": "2026-01-01T00:01:00+00:00",
                },
                {
                    "player": "bad",
                    "name": "morgue-bad-20260101-000001.txt",
                    "fetch_status": "failed",
                    "process_status": "pending",
                    "fetch_error": "network down",
                    "fetched_at": "2026-01-01T00:02:00+00:00",
                },
                {
                    "player": "parse",
                    "name": "morgue-parse-20260101-000001.lst",
                    "fetch_status": "fetched",
                    "process_status": "failed",
                    "process_error": "parser failed",
                    "processed_at": "2026-01-01T00:03:00+00:00",
                },
            ]
        )
        self.repository.crawl_files_collection.insert_many(
            [
                {"player": "wiiwiwi", "name": "ok.txt", "status": "completed"},
                {
                    "player": "bad",
                    "name": "bad.txt",
                    "status": "failed",
                    "error": "file failed",
                    "processed_at": "2026-01-01T00:04:00+00:00",
                },
            ]
        )
        self.repository.crawl_users_collection.insert_many(
            [
                {
                    "player": "wiiwiwi",
                    "status": "completed",
                    "scanned_at": "2026-01-01T00:05:00+00:00",
                },
                {
                    "player": "bad",
                    "status": "failed",
                    "error": "directory failed",
                    "scanned_at": "2026-01-01T00:06:00+00:00",
                },
            ]
        )
        client = TestClient(create_app(self.repository, MockGalleryApiMetricsRepository()))

        response = client.get("/admin/crawl-status")

        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["artifactCount"], 1)
        self.assertEqual(data["rawFiles"]["total"], 3)
        self.assertEqual(data["rawFiles"]["fetched"], 2)
        self.assertEqual(data["rawFiles"]["fetchFailed"], 1)
        self.assertEqual(data["rawFiles"]["processPending"], 1)
        self.assertEqual(data["rawFiles"]["processProcessed"], 1)
        self.assertEqual(data["rawFiles"]["processFailed"], 1)
        self.assertEqual(data["crawlFiles"], {"completed": 1, "failed": 1})
        self.assertEqual(data["crawlUsers"], {"completed": 1, "failed": 1})
        self.assertEqual(data["latest"]["fetchedAt"], "2026-01-01T00:02:00+00:00")
        self.assertEqual(data["latest"]["processedAt"], "2026-01-01T00:03:00+00:00")
        self.assertEqual(data["latest"]["scannedAt"], "2026-01-01T00:06:00+00:00")
        self.assertEqual(data["recentErrors"][0]["message"], "directory failed")
        self.assertEqual(
            {error["kind"] for error in data["recentErrors"]},
            {"fetch", "process", "file", "user"},
        )


class MockCrawlStatusApiTest(unittest.TestCase):
    def test_admin_crawl_status_uses_injected_mock_repository(self) -> None:
        client = TestClient(create_app(MockCrawlStatusRepository(), MockGalleryApiMetricsRepository()))

        response = client.get("/admin/crawl-status")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.json(),
            {
                "artifactCount": 7,
                "rawFiles": {
                    "total": 9,
                    "fetched": 8,
                    "fetchFailed": 1,
                    "processPending": 2,
                    "processProcessed": 6,
                    "processFailed": 1,
                },
                "crawlFiles": {"completed": 6, "failed": 1},
                "crawlUsers": {"completed": 3, "pending": 2},
                "latest": {
                    "fetchedAt": "2026-01-01T00:02:00+00:00",
                    "processedAt": "2026-01-01T00:03:00+00:00",
                    "scannedAt": "2026-01-01T00:04:00+00:00",
                },
                "recentErrors": [],
            },
        )


class AdminGalleryApiMetricsTest(unittest.TestCase):
    def test_admin_gallery_api_metrics_uses_injected_repository(self) -> None:
        client = TestClient(create_app(MockCrawlStatusRepository(), MockGalleryApiMetricsRepository()))

        response = client.get("/admin/metrics/gallery-api")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.json(),
            {
                "status": "ok",
                "windowSeconds": 300,
                "requestRatePerSecond": 1.5,
                "errorRatePerSecond": 0.25,
                "p95LatencySeconds": 0.125,
                "inFlightRequests": 2.0,
                "error": None,
            },
        )


class MockCrawlStatusRepository:
    def get_crawl_status(self) -> CrawlStatus:
        return CrawlStatus(
            artifactCount=7,
            rawFiles=RawFileStatus(
                total=9,
                fetched=8,
                fetchFailed=1,
                processPending=2,
                processProcessed=6,
                processFailed=1,
            ),
            crawlFiles={"completed": 6, "failed": 1},
            crawlUsers={"completed": 3, "pending": 2},
            latest=LatestActivity(
                fetchedAt="2026-01-01T00:02:00+00:00",
                processedAt="2026-01-01T00:03:00+00:00",
                scannedAt="2026-01-01T00:04:00+00:00",
            ),
            recentErrors=[],
        )


class MockGalleryApiMetricsRepository:
    def get_gallery_api_metrics(self) -> GalleryApiMetrics:
        return GalleryApiMetrics(
            status="ok",
            windowSeconds=300,
            requestRatePerSecond=1.5,
            errorRatePerSecond=0.25,
            p95LatencySeconds=0.125,
            inFlightRequests=2.0,
        )


if __name__ == "__main__":
    unittest.main()
