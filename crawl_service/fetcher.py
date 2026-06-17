"""HTTP helpers that fetch morgue index entries and file text."""

from __future__ import annotations

import posixpath
import re
import urllib.parse
from dataclasses import dataclass

import requests
from bs4 import BeautifulSoup

DEFAULT_TIMEOUT = 20.0
DEFAULT_USER_AGENT = "dcss-arti-gallery-crawler/0.1"
MORGUE_FILE_RE = re.compile(
    r"^\.?morgue-(?P<player>.+?)-(?P<stamp>\d{8}-\d{6})\.(?P<ext>txt|lst)$"
)


@dataclass(frozen=True)
class MorgueUser:
    """A remote morgue user directory entry."""

    nickname: str
    url: str
    modified_at: str


@dataclass(frozen=True)
class MorgueFile:
    """A remote morgue txt/lst directory entry."""

    name: str
    url: str

    @property
    def extension(self) -> str:
        return self.name.rsplit(".", 1)[-1]


def _get(
    url: str,
) -> requests.Response:
    try:
        response = requests.get(
            url,
            headers={"User-Agent": DEFAULT_USER_AGENT},
            timeout=DEFAULT_TIMEOUT,
            verify=True,
        )
        response.raise_for_status()

        return response
    except requests.RequestException as exc:
        raise RuntimeError(f"failed to fetch {url}: {exc}") from exc


def fetch_morgue_file_text(
    url: str,
) -> str:
    """Fetch the text body for one remote morgue txt/lst file URL."""

    return _get(url).text


def fetch_morgue_files(
    morgue_url: str,
) -> list[MorgueFile]:
    """Fetch a remote remote morgue directory HTML page and return txt/lst file entries."""

    html = _get(morgue_url).text
    return _parse_morgue_index(html, base_url=morgue_url)


def fetch_morgue_users(
    morgue_root_url: str,
) -> list[MorgueUser]:
    """Fetch the root remote remote morgue directory and return player directory entries."""

    html = _get(morgue_root_url).text
    return _parse_morgue_user_index(html, base_url=morgue_root_url)


def _parse_morgue_user_index(html: str, base_url: str) -> list[MorgueUser]:
    """Extract player directory links and their index Date column."""

    soup = BeautifulSoup(html, "html.parser")
    base_url = base_url.rstrip("/") + "/"
    users: list[MorgueUser] = []
    for row in soup.find_all("tr"):
        cells = row.find_all("td")
        if len(cells) < 3:
            continue
        anchor = cells[0].find("a", href=True)
        if anchor is None:
            continue
        href = anchor.get("href")
        if not isinstance(href, str):
            continue
        text = anchor.get_text(strip=True).removesuffix("/")
        if href.startswith("?") or href in {"../", "/"} or not href.endswith("/"):
            continue
        modified_at = cells[2].get_text(strip=True)
        if not text or modified_at == "-":
            continue
        users.append(
            MorgueUser(
                nickname=urllib.parse.unquote(text),
                url=urllib.parse.urljoin(base_url, href),
                modified_at=modified_at,
            )
        )
    return sorted(users, key=lambda user: user.nickname.lower())


def _parse_morgue_index(html: str, base_url: str) -> list[MorgueFile]:
    """Extract txt/lst morgue file links from a directory index HTML document."""

    soup = BeautifulSoup(html, "html.parser")
    entries: list[MorgueFile] = []
    for anchor in soup.find_all("a", href=True):
        href = anchor.get("href")
        if not isinstance(href, str):
            continue
        text = anchor.get_text(strip=True)
        if href.startswith("?") or href in {"../", "/"} or text.endswith("/"):
            continue

        parsed_name = posixpath.basename(urllib.parse.urlparse(href).path)
        file_name = urllib.parse.unquote(parsed_name or text or href)
        if not MORGUE_FILE_RE.match(file_name):
            continue

        entries.append(
            MorgueFile(name=file_name, url=urllib.parse.urljoin(base_url, href))
        )
    return sorted(entries, key=lambda entry: entry.name)
