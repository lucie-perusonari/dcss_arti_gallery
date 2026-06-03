"""Morgue domain data types."""

from __future__ import annotations

from dataclasses import dataclass


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


@dataclass(frozen=True)
class MorgueRawText:
    """A remote morgue txt/lst file as raw text."""

    name: str
    url: str
    extension: str
    text: str
