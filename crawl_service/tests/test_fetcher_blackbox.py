from __future__ import annotations

import unittest
from unittest.mock import patch

from crawl_service import fetcher


class _Response:
    def __init__(self, text: str) -> None:
        self.text = text

    def raise_for_status(self) -> None:
        return None


class FetcherBlackBoxTest(unittest.TestCase):
    def test_fetch_morgue_users_reads_directory_index(self) -> None:
        html = """
        <table>
          <tr><td><a href="wiiwiwi/">wiiwiwi/</a></td><td></td><td>2026-Jan-02 00:00</td></tr>
          <tr><td><a href="../">../</a></td><td></td><td>-</td></tr>
          <tr><td><a href="Other/">Other/</a></td><td></td><td>2026-Jan-03 00:00</td></tr>
        </table>
        """

        with patch("crawl_service.fetcher.requests.get", return_value=_Response(html)):
            users = fetcher.fetch_morgue_users("https://example.test/morgue")

        self.assertEqual([user.nickname for user in users], ["Other", "wiiwiwi"])
        self.assertEqual(users[0].url, "https://example.test/morgue/Other/")
        self.assertEqual(users[1].modified_at, "2026-Jan-02 00:00")

    def test_fetch_morgue_files_returns_txt_and_lst_entries(self) -> None:
        html = """
        <a href="morgue-wiiwiwi-20260101-000001.txt">txt</a>
        <a href="morgue-wiiwiwi-20260101-000001.lst">lst</a>
        <a href="notes.md">notes</a>
        <a href="subdir/">subdir</a>
        """

        with patch("crawl_service.fetcher.requests.get", return_value=_Response(html)):
            files = fetcher.fetch_morgue_files("https://example.test/morgue/wiiwiwi/")

        self.assertEqual(
            [file.name for file in files],
            [
                "morgue-wiiwiwi-20260101-000001.lst",
                "morgue-wiiwiwi-20260101-000001.txt",
            ],
        )
        self.assertEqual(files[0].extension, "lst")

if __name__ == "__main__":
    unittest.main()
