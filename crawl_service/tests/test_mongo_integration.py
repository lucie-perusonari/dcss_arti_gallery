from __future__ import annotations

import os
import subprocess
import time
import unittest
import uuid
from datetime import date

from pymongo import MongoClient

from crawl_service.fetcher import MorgueFile, MorgueUser
from crawl_service.repository import create_mongo_crawl_repository
from crawl_service.worker import CrawlWorker, CrawlWorkerConfig, RequestThrottle


if os.environ.get("CRAWL_SERVICE_MONGO_INTEGRATION") != "1":
    raise unittest.SkipTest("set CRAWL_SERVICE_MONGO_INTEGRATION=1 to run disposable MongoDB integration tests")


class CrawlServiceMongoIntegrationTest(unittest.TestCase):
    container_name = f"dcss-crawl-service-test-mongo-{uuid.uuid4().hex}"
    uri: str
    client: MongoClient

    @classmethod
    def setUpClass(cls) -> None:
        subprocess.run(
            [
                "docker",
                "run",
                "--rm",
                "-d",
                "--name",
                cls.container_name,
                "-p",
                "127.0.0.1::27017",
                "mongo:7.0",
            ],
            check=True,
            capture_output=True,
            text=True,
        )
        port = subprocess.run(
            ["docker", "port", cls.container_name, "27017/tcp"],
            check=True,
            capture_output=True,
            text=True,
        ).stdout.strip().rsplit(":", 1)[-1]
        cls.uri = f"mongodb://127.0.0.1:{port}"
        cls.client = MongoClient(cls.uri, serverSelectionTimeoutMS=250)
        deadline = time.monotonic() + 20
        last_error: Exception | None = None
        while time.monotonic() < deadline:
            try:
                cls.client.admin.command("ping")
                return
            except Exception as exc:
                last_error = exc
                time.sleep(0.2)
        raise RuntimeError(f"temporary MongoDB did not become ready: {last_error}")

    @classmethod
    def tearDownClass(cls) -> None:
        try:
            cls.client.close()
        finally:
            subprocess.run(
                ["docker", "rm", "-f", cls.container_name],
                check=False,
                capture_output=True,
                text=True,
            )

    def test_worker_persists_raw_file_and_crawl_state_to_real_mongodb(self) -> None:
        database_name = f"crawl_service_integration_{uuid.uuid4().hex}"
        repository = create_mongo_crawl_repository(
            uri=self.uri,
            database=database_name,
            crawl_files_collection="crawl_files",
            crawl_users_collection="crawl_users",
            raw_files_collection="raw_morgue_files",
            client_factory=lambda _uri: self.client,
        )
        database = self.client[database_name]
        self.addCleanup(lambda: self.client.drop_database(database_name))

        worker = CrawlWorker(
            repository,
            config=CrawlWorkerConfig(
                base_url="https://example.test/morgue",
                start_date=date(2026, 1, 1),
                request_delay_seconds=0,
                loop_interval_seconds=0,
                timeout=1,
                user_agent="test-agent",
            ),
            throttle=RequestThrottle(0, sleep=lambda _seconds: None),
            list_users=lambda *args, **kwargs: [
                MorgueUser("WiiWiWi", "https://example.test/morgue/WiiWiWi/", "2026-Jan-02 00:00")
            ],
            list_files=lambda *args, **kwargs: [
                MorgueFile("morgue-WiiWiWi-20260101-000001.txt", "https://example.test/new.txt")
            ],
            fetch_file_text=lambda *args, **kwargs: "raw morgue text",
        )

        summary = worker._crawl_once()

        raw_file = database.raw_morgue_files.find_one({"player": "wiiwiwi"})
        crawl_file = database.crawl_files.find_one({"player": "wiiwiwi"})
        crawl_user = database.crawl_users.find_one({"player": "wiiwiwi"})
        self.assertEqual(summary.files_processed, 1)
        self.assertIsNotNone(raw_file)
        self.assertIsNotNone(crawl_file)
        self.assertIsNotNone(crawl_user)
        assert raw_file is not None
        assert crawl_file is not None
        assert crawl_user is not None
        self.assertEqual(raw_file["name"], "morgue-WiiWiWi-20260101-000001.txt")
        self.assertEqual(raw_file["text"], "raw morgue text")
        self.assertEqual(raw_file["fetch_status"], "fetched")
        self.assertEqual(crawl_file["status"], "completed")
        self.assertEqual(crawl_user["status"], "completed")
        self.assertEqual(crawl_user["stored_files"], 1)


if __name__ == "__main__":
    unittest.main()
