"""Morgue fetch and file-name constants."""

from __future__ import annotations

import re

DEFAULT_TIMEOUT = 20.0
DEFAULT_USER_AGENT = "dcss-arti-gallery-crawler/0.1"
MORGUE_FILE_RE = re.compile(
    r"^\.?morgue-(?P<player>.+?)-(?P<stamp>\d{8}-\d{6})\.(?P<ext>txt|lst)$"
)
