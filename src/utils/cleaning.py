"""Data cleaning helpers shared across transformations."""
from __future__ import annotations

import math
import re
from decimal import Decimal, InvalidOperation
from typing import Any, Iterable, Optional

_StrOrBytes = (str, bytes)

_NUMBER_WORDS = {
    "zero": 0,
    "one": 1,
    "two": 2,
    "three": 3,
    "four": 4,
    "five": 5,
    "six": 6,
    "seven": 7,
    "eight": 8,
    "nine": 9,
    "ten": 10,
    "eleven": 11,
    "twelve": 12,
}

_WHITESPACE_RE = re.compile(r"\s+")
_NON_DIGIT_RE = re.compile(r"[^0-9.-]")
_BOOLEAN_TRUE = {"y", "yes", "true", "1"}
_BOOLEAN_FALSE = {"n", "no", "false", "0"}
_NULL_TOKENS = {None, "", " ", "na", "n/a", "null", "none", "unknown"}


def normalize_string(value: Any) -> Optional[str]:
    """Standardize string values, stripping whitespace and empty tokens."""

    if value in _NULL_TOKENS:
        return None

    if isinstance(value, bytes):
        value = value.decode("utf-8", errors="ignore")

    if isinstance(value, str):
        text = value.strip()
        if not text:
            return None
        return _WHITESPACE_RE.sub(" ", text)

    return str(value)


def normalize_bool(value: Any) -> Optional[bool]:
    """Coerce loosely formatted boolean-like values into canonical booleans."""

    if value in _NULL_TOKENS:
        return None

    if isinstance(value, bool):
        return value

    if isinstance(value, (int, float)):
        if math.isnan(value):
            return None
        return bool(value)

    if isinstance(value, _StrOrBytes):
        text = normalize_string(value)
        if text is None:
            return None
        lowered = text.lower()
        if lowered in _BOOLEAN_TRUE:
            return True
        if lowered in _BOOLEAN_FALSE:
            return False

    return None


def _extract_number_from_string(value: str) -> str:
    """Remove non-numeric characters except sign and decimal point."""

    cleaned = _NON_DIGIT_RE.sub("", value)
    if cleaned.count("-") > 1:
        cleaned = cleaned.replace("-", "", cleaned.count("-") - 1)
    if cleaned.count(".") > 1:
        first, *rest = cleaned.split(".")
        cleaned = first + "." + "".join(rest)
    return cleaned


def normalize_decimal(value: Any) -> Optional[Decimal]:
    """Coerce numbers stored as messy strings into Decimal instances."""

    if value in _NULL_TOKENS:
        return None

    if isinstance(value, Decimal):
        return value

    if isinstance(value, (int, float)):
        if isinstance(value, float) and math.isnan(value):
            return None
        return Decimal(str(value))

    if isinstance(value, _StrOrBytes):
        text = normalize_string(value)
        if text is None:
            return None

        lowered = text.lower()
        if lowered in _NUMBER_WORDS:
            return Decimal(_NUMBER_WORDS[lowered])

        candidate = _extract_number_from_string(lowered)
        if not candidate:
            return None
        try:
            return Decimal(candidate)
        except InvalidOperation:
            return None

    return None


def normalize_int(value: Any) -> Optional[int]:
    """Int-specific convenience wrapper around :func:`normalize_decimal`."""

    decimal_value = normalize_decimal(value)
    if decimal_value is None:
        return None
    try:
        return int(decimal_value.to_integral_value(rounding="ROUND_HALF_UP"))
    except (InvalidOperation, ValueError):
        return None


def normalize_float(value: Any) -> Optional[float]:
    """Float-specific convenience wrapper around :func:`normalize_decimal`."""

    decimal_value = normalize_decimal(value)
    if decimal_value is None:
        return None
    return float(decimal_value)


def coalesce(*values: Any) -> Optional[Any]:
    """Return the first non-null value from the provided sequence."""

    for value in values:
        if value not in _NULL_TOKENS:
            return value
    return None


def ensure_sequence(value: Any) -> list[Any]:
    """Ensure the input is always represented as a list for iteration."""

    if value is None:
        return []
    if isinstance(value, _StrOrBytes):
        text = normalize_string(value)
        return [] if text is None else [text]
    if isinstance(value, dict):
        return [value]
    if isinstance(value, Iterable):
        return list(value)
    return [value]
