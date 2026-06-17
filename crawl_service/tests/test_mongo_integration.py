from __future__ import annotations

import os
import subprocess
import time
import unittest
import uuid
from unittest.mock import patch

import responses
from pymongo import MongoClient

from crawl_service.repository import DEFAULT_MONGO_DATABASE, create_mongo_crawl_repository
from crawl_service.worker import CrawlWorker


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

    def test_worker_fetches_http_morgue_file_and_persists_to_real_mongodb(self) -> None:
        database = self.client[DEFAULT_MONGO_DATABASE]
        self.addCleanup(lambda: self.client.drop_database(DEFAULT_MONGO_DATABASE))
        base_url = "https://archive.test/morgue"

        with (
            patch.dict(
                os.environ,
                {
                    "MONGODB_URI": self.uri,
                },
            ),
            patch("crawl_service.worker.time.sleep"),
            responses.RequestsMock(assert_all_requests_are_fired=True) as http,
        ):
            http.add(
                responses.GET,
                base_url,
                body="""
                <table>
                  <tr>
                    <td><a href="WiiWiWi/">WiiWiWi/</a></td>
                    <td></td>
                    <td>2026-Jan-02 00:00</td>
                  </tr>
                </table>
                """,
            )
            http.add(
                responses.GET,
                f"{base_url}/WiiWiWi/",
                body="""
                <a href="morgue-WiiWiWi-20251231-235959.txt">old</a>
                <a href="morgue-WiiWiWi-20260101-000001.txt">new</a>
                """,
            )
            http.add(
                responses.GET,
                f"{base_url}/WiiWiWi/morgue-WiiWiWi-20260101-000001.txt",
                body="raw morgue text",
            )
            repository = create_mongo_crawl_repository()
            self.addCleanup(repository.close)
            worker = CrawlWorker(repository, base_url=base_url)
            worker.run_once()

        raw_file = database.raw_morgue_files.find_one({"player": "WiiWiWi"})
        self.assertIsNotNone(raw_file)
        assert raw_file is not None
        self.assertEqual(raw_file["name"], "morgue-WiiWiWi-20260101-000001.txt")
        self.assertEqual(raw_file["text"], "raw morgue text")
        self.assertEqual(raw_file["fetch_status"], "fetched")
        self.assertEqual(raw_file["url"], f"{base_url}/WiiWiWi/morgue-WiiWiWi-20260101-000001.txt")
        self.assertEqual(database.crawl_errors.count_documents({}), 0)


if __name__ == "__main__":
    unittest.main()
