import unittest

from crawl_service.morgue import fetcher
from crawl_service.morgue.types import MorgueFile


class FakeResponse:
    def __init__(self, text: str) -> None:
        self.text = text


class HttpRequestTest(unittest.TestCase):
    def test_user_list_parser_keeps_player_directories_with_dates(self) -> None:
        html = """
        <html><body><table id="list"><tbody>
          <tr><td class="link"><a href="../">Parent directory/</a></td><td>-</td><td>-</td></tr>
          <tr><td class="link"><a href="?C=N&amp;O=A">sort</a></td><td>-</td><td>-</td></tr>
          <tr><td class="link"><a href="wiiwiwi/" title="wiiwiwi">wiiwiwi/</a></td><td>-</td><td class="date">2026-May-16 18:54</td></tr>
          <tr><td class="link"><a href="old/" title="old">old/</a></td><td>-</td><td class="date">2025-Dec-31 23:59</td></tr>
          <tr><td class="link"><a href="notes.txt">notes</a></td><td>10</td><td class="date">2026-Jan-01 00:00</td></tr>
        </tbody></table></body></html>
        """

        original_get = fetcher._get
        try:
            fetcher._get = lambda *args, **kwargs: FakeResponse(html)
            users = fetcher.fetch_morgue_users("https://archive.nemelex.cards/morgue/")
        finally:
            fetcher._get = original_get

        self.assertEqual([user.nickname for user in users], ["old", "wiiwiwi"])
        self.assertEqual(users[1].url, "https://archive.nemelex.cards/morgue/wiiwiwi/")
        self.assertEqual(users[1].modified_at, "2026-May-16 18:54")

    def test_user_list_parser_preserves_base_path_without_trailing_slash(self) -> None:
        html = """
        <html><body><table id="list"><tbody>
          <tr><td class="link"><a href="wiiwiwi/" title="wiiwiwi">wiiwiwi/</a></td><td>-</td><td class="date">2026-May-16 18:54</td></tr>
        </tbody></table></body></html>
        """

        original_get = fetcher._get
        try:
            fetcher._get = lambda *args, **kwargs: FakeResponse(html)
            users = fetcher.fetch_morgue_users("https://archive.nemelex.cards/morgue")
        finally:
            fetcher._get = original_get

        self.assertEqual(len(users), 1)
        self.assertEqual(users[0].url, "https://archive.nemelex.cards/morgue/wiiwiwi/")

    def test_list_parser_keeps_txt_and_lst_files(self) -> None:
        html = """
        <html><body>
          <a href="../">Parent Directory</a>
          <a href="morgue-wiiwiwi-20260516-185425.txt">txt</a>
          <a href="morgue-wiiwiwi-20260516-185425.lst">lst</a>
          <a href="notes.html">notes</a>
        </body></html>
        """
        original_get = fetcher._get
        try:
            fetcher._get = lambda *args, **kwargs: FakeResponse(html)
            entries = fetcher.fetch_morgue_files(
                "https://archive.nemelex.cards/morgue/wiiwiwi/"
            )
        finally:
            fetcher._get = original_get

        self.assertEqual(
            [entry.name for entry in entries],
            [
                "morgue-wiiwiwi-20260516-185425.lst",
                "morgue-wiiwiwi-20260516-185425.txt",
            ],
        )

    def test_build_morgue_raw_texts_fetches_parser_ready_text(self) -> None:
        fetched_urls: list[str] = []
        file = MorgueFile(
            "morgue-wiiwiwi-20260516-185425.lst",
            "https://example.test/morgue-wiiwiwi-20260516-185425.lst",
        )

        def fake_fetch_file(
            url: str,
            timeout: float = fetcher.DEFAULT_TIMEOUT,
            verify_tls: bool = True,
            user_agent: str = fetcher.DEFAULT_USER_AGENT,
        ) -> str:
            fetched_urls.append(url)
            return f"content from {url}"

        raw_texts = fetcher.build_morgue_raw_texts(
            [file],
            fetch_file=fake_fetch_file,
            delay=0,
        )

        self.assertEqual(fetched_urls, [file.url])
        self.assertEqual(len(raw_texts), 1)
        self.assertEqual(raw_texts[0].name, file.name)
        self.assertEqual(raw_texts[0].url, file.url)
        self.assertEqual(raw_texts[0].extension, "lst")
        self.assertEqual(raw_texts[0].text, f"content from {file.url}")

    def test_fetch_morgue_files_fetches_html_and_parses_entries(self) -> None:
        calls: list[str] = []
        html = """
        <html><body>
          <a href="morgue-wiiwiwi-20260516-185425.txt">txt</a>
          <a href="morgue-wiiwiwi-20260516-185425.lst">lst</a>
        </body></html>
        """

        def fake_get(
            url: str,
            timeout: float = fetcher.DEFAULT_TIMEOUT,
            verify_tls: bool = True,
            user_agent: str = fetcher.DEFAULT_USER_AGENT,
        ) -> FakeResponse:
            calls.append(url)
            return FakeResponse(html)

        original_get = fetcher._get
        try:
            fetcher._get = fake_get
            entries = fetcher.fetch_morgue_files("https://example.test/morgue/")
        finally:
            fetcher._get = original_get

        self.assertEqual(calls, ["https://example.test/morgue/"])
        self.assertEqual(
            [entry.name for entry in entries],
            [
                "morgue-wiiwiwi-20260516-185425.lst",
                "morgue-wiiwiwi-20260516-185425.txt",
            ],
        )

    def test_select_morgue_files_by_name_matches_hidden_example_names(self) -> None:
        files = [
            MorgueFile(
                "morgue-wiiwiwi-20260516-185425.lst",
                "https://example.test/morgue-wiiwiwi-20260516-185425.lst",
            ),
            MorgueFile(
                "morgue-wiiwiwi-20260516-185425.txt",
                "https://example.test/morgue-wiiwiwi-20260516-185425.txt",
            ),
        ]

        selected = fetcher.select_morgue_files_by_name(
            files,
            [
                ".morgue-wiiwiwi-20260516-185425.txt",
                ".morgue-wiiwiwi-20260516-185425.lst",
            ],
        )

        self.assertEqual(
            [file.name for file in selected],
            [
                "morgue-wiiwiwi-20260516-185425.txt",
                "morgue-wiiwiwi-20260516-185425.lst",
            ],
        )

    def test_select_recent_morgue_files_limits_to_latest_entries(self) -> None:
        files = [
            MorgueFile(
                f"morgue-wiiwiwi-20260516-18542{index}.txt",
                f"https://example.test/morgue-{index}.txt",
            )
            for index in range(5)
        ]

        selected = fetcher.select_recent_morgue_files(files, file_limit=2)

        self.assertEqual(
            [file.name for file in selected],
            [
                "morgue-wiiwiwi-20260516-185423.txt",
                "morgue-wiiwiwi-20260516-185424.txt",
            ],
        )

    def test_fetch_morgue_file_text_fetches_one_file_body(self) -> None:
        calls: list[str] = []

        def fake_get(
            url: str,
            timeout: float = fetcher.DEFAULT_TIMEOUT,
            verify_tls: bool = True,
            user_agent: str = fetcher.DEFAULT_USER_AGENT,
        ) -> FakeResponse:
            calls.append(url)
            return FakeResponse(f"body from {url}")

        original_get = fetcher._get
        try:
            fetcher._get = fake_get
            text = fetcher.fetch_morgue_file_text("https://example.test/morgue/m.txt")
        finally:
            fetcher._get = original_get

        self.assertEqual(calls, ["https://example.test/morgue/m.txt"])
        self.assertEqual(text, "body from https://example.test/morgue/m.txt")

if __name__ == "__main__":
    unittest.main()
