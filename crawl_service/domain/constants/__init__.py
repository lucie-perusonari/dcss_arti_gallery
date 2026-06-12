"""Shared crawl service domain constants and lookup tables.

This package keeps generated DCSS data, hand-maintained DCSS data, parser
rules, scoring tables, and tile mappings in separate modules while preserving
the existing ``crawl_service.domain.constants`` import boundary.
"""

from __future__ import annotations

from .dcss import *
from .generated_dcss_data import *
from .parser import *
from .scoring import *
from .tiles import *
