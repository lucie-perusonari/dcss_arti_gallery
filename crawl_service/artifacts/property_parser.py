"""Shared randart property token parsing."""

from __future__ import annotations

from crawl_service.artifacts.constants import SIGNED_PROPERTY_RE

RESISTANCE_STEP_KEYS = {"rF", "rC", "rN", "Will", "rElec", "rPois", "rCorr"}
NUMERIC_STEP_KEYS = {"Stlth"}
BOOLEAN_PLUS_KEYS = {"RegenMP", "Regen"}


def parse_property_token(token: str) -> tuple[str, int | bool | None]:
    """Return a normalized property key and value for a visible randart token."""

    signed_match = SIGNED_PROPERTY_RE.match(token)
    if signed_match:
        return signed_match.group("key"), int(signed_match.group("value"))

    for key in sorted((*RESISTANCE_STEP_KEYS, *NUMERIC_STEP_KEYS), key=len, reverse=True):
        if token.startswith(key) and set(token[len(key) :]) <= {"+", "-"}:
            suffix = token[len(key) :]
            if suffix:
                sign = -1 if suffix[0] == "-" else 1
                return key, sign * len(suffix)

    for key in BOOLEAN_PLUS_KEYS:
        if token == f"{key}+":
            return key, True

    return token, True
