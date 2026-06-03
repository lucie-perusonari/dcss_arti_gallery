"""HTTP helpers that fetch morgue index entries and file text."""

from __future__ import annotations

import posixpath
import re
import time
import urllib.parse
from collections.abc import Callable, Iterable

import requests
from bs4 import BeautifulSoup

from crawl_service.morgue.types import MorgueFile, MorgueRawText, MorgueUser


DEFAULT_TIMEOUT = 20.0
DEFAULT_USER_AGENT = "dcss-best-arti-crawler/0.1"
MORGUE_FILE_RE = re.compile(
    r"^\.?morgue-(?P<player>.+?)-(?P<stamp>\d{8}-\d{6})\.(?P<ext>txt|lst)$"
)


def _normalized_morgue_file_name(name: str) -> str:
    """Normalize local/remote morgue names so hidden fixture files match archive entries."""

    file_name = posixpath.basename(urllib.parse.urlparse(name).path)
    return urllib.parse.unquote(file_name).lstrip(".")


def _get(
    url: str,
    timeout: float = DEFAULT_TIMEOUT,
    verify_tls: bool = True,
    user_agent: str = DEFAULT_USER_AGENT,
) -> requests.Response:
    try:
        response = requests.get(
            url,
            headers={"User-Agent": user_agent},
            timeout=timeout,
            verify=verify_tls,
        )
        response.raise_for_status()

        


        return response
    except requests.RequestException as exc:
        raise RuntimeError(f"failed to fetch {url}: {exc}") from exc


def fetch_morgue_file_text(
    url: str,
    timeout: float = DEFAULT_TIMEOUT,
    verify_tls: bool = True,
    user_agent: str = DEFAULT_USER_AGENT,
) -> str:
    """Fetch the text body for one remote morgue txt/lst file URL."""

    return _get(
        url,
        timeout=timeout,
        verify_tls=verify_tls,
        user_agent=user_agent,
    ).text


def fetch_morgue_files(
    morgue_url: str,
    timeout: float = DEFAULT_TIMEOUT,
    verify_tls: bool = True,
    user_agent: str = DEFAULT_USER_AGENT,
) -> list[MorgueFile]:
    """Fetch a morgue directory HTML page and return txt/lst file entries."""

    html = _get(
        morgue_url,
        timeout=timeout,
        verify_tls=verify_tls,
        user_agent=user_agent,
    ).text
    return _parse_morgue_index(html, base_url=morgue_url)


def fetch_morgue_users(
    morgue_root_url: str,
    timeout: float = DEFAULT_TIMEOUT,
    verify_tls: bool = True,
    user_agent: str = DEFAULT_USER_AGENT,
) -> list[MorgueUser]:
    """Fetch the root morgue directory and return player directory entries."""

    html = _get(
        morgue_root_url,
        timeout=timeout,
        verify_tls=verify_tls,
        user_agent=user_agent,
    ).text
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


def select_morgue_files_by_name(
    files: Iterable[MorgueFile],
    names: Iterable[str],
    require_all: bool = True,
) -> list[MorgueFile]:
    """Select remote morgue files whose names match the requested local/remote names."""

    requested = [_normalized_morgue_file_name(name) for name in names]
    by_name = {_normalized_morgue_file_name(file.name): file for file in files}
    selected: list[MorgueFile] = []
    missing: list[str] = []
    for name in requested:
        file = by_name.get(name)
        if file is None:
            missing.append(name)
            continue
        selected.append(file)

    if require_all and missing:
        raise RuntimeError(f"missing morgue files: {', '.join(missing)}")
    return selected


def select_recent_morgue_files(
    files: Iterable[MorgueFile],
    file_limit: int | None,
) -> list[MorgueFile]:
    """Return the most recent morgue entries while preserving fetch order."""

    entries = list(files)
    if file_limit is None:
        return entries
    if file_limit < 1:
        raise ValueError("file_limit must be greater than 0")
    return entries[-file_limit:]


def build_morgue_raw_texts(
    files: list[MorgueFile],
    fetch_file: Callable[..., str] = fetch_morgue_file_text,
    timeout: float = DEFAULT_TIMEOUT,
    verify_tls: bool = True,
    user_agent: str = DEFAULT_USER_AGENT,
    delay: float = 0.2,
) -> list[MorgueRawText]:
    """Convert remote morgue file entries into parser-ready raw text values."""

    raw_texts: list[MorgueRawText] = []
    for index, file in enumerate(files):
        if index:
            time.sleep(delay)
        raw_texts.append(
            MorgueRawText(
                name=file.name,
                url=file.url,
                extension=file.extension,
                text=fetch_file(
                    file.url,
                    timeout=timeout,
                    verify_tls=verify_tls,
                    user_agent=user_agent,
                ),
            )
        )
    return raw_texts
