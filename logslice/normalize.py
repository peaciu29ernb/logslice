"""Field value normalization: lowercase, strip whitespace, cast types, apply regex substitutions."""

import re
from typing import Any, Dict, List, Optional, Tuple


def normalize_lowercase(value: Any) -> Any:
    """Lowercase a string value; pass through non-strings unchanged."""
    if isinstance(value, str):
        return value.lower()
    return value


def normalize_strip(value: Any) -> Any:
    """Strip leading/trailing whitespace from string values."""
    if isinstance(value, str):
        return value.strip()
    return value


def normalize_replace(value: Any, pattern: str, replacement: str) -> Any:
    """Apply a regex substitution to a string value."""
    if isinstance(value, str):
        try:
            return re.sub(pattern, replacement, value)
        except re.error:
            return value
    return value


def normalize_field(
    value: Any,
    lowercase: bool = False,
    strip: bool = False,
    replacements: Optional[List[Tuple[str, str]]] = None,
) -> Any:
    """Apply a sequence of normalizations to a single field value."""
    if strip:
        value = normalize_strip(value)
    if lowercase:
        value = normalize_lowercase(value)
    for pattern, replacement in (replacements or []):
        value = normalize_replace(value, pattern, replacement)
    return value


def normalize_record(
    record: Dict[str, Any],
    fields: Optional[List[str]] = None,
    lowercase: bool = False,
    strip: bool = False,
    replacements: Optional[List[Tuple[str, str]]] = None,
) -> Dict[str, Any]:
    """Return a new record with normalizations applied to specified fields.

    If *fields* is None or empty, all fields except ``_raw`` are normalized.
    The original record is never mutated.
    """
    result = dict(record)
    target_keys = fields if fields else [k for k in result if k != "_raw"]
    for key in target_keys:
        if key in result and key != "_raw":
            result[key] = normalize_field(
                result[key],
                lowercase=lowercase,
                strip=strip,
                replacements=replacements,
            )
    return result


def normalize_records(
    records,
    fields: Optional[List[str]] = None,
    lowercase: bool = False,
    strip: bool = False,
    replacements: Optional[List[Tuple[str, str]]] = None,
):
    """Yield normalized records from an iterable."""
    for record in records:
        yield normalize_record(
            record,
            fields=fields,
            lowercase=lowercase,
            strip=strip,
            replacements=replacements,
        )
