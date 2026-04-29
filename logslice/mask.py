"""Field masking: partially obscure field values while preserving structure."""

import re
from typing import Any, Dict, Iterable, Iterator, List, Optional


def _mask_string(value: str, show_first: int, show_last: int, char: str) -> str:
    """Mask the middle of a string, optionally showing prefix/suffix characters."""
    length = len(value)
    visible = show_first + show_last
    if visible >= length:
        return value
    hidden = length - visible
    prefix = value[:show_first]
    suffix = value[length - show_last:] if show_last > 0 else ""
    return prefix + (char * hidden) + suffix


def mask_field(
    record: Dict[str, Any],
    field: str,
    show_first: int = 0,
    show_last: int = 0,
    char: str = "*",
) -> Dict[str, Any]:
    """Return a new record with the specified field partially masked."""
    if field not in record or field == "__raw__":
        return record
    value = record[field]
    if not isinstance(value, str):
        value = str(value)
    masked = _mask_string(value, show_first, show_last, char)
    result = dict(record)
    result[field] = masked
    return result


def mask_fields(
    record: Dict[str, Any],
    fields: List[str],
    show_first: int = 0,
    show_last: int = 0,
    char: str = "*",
) -> Dict[str, Any]:
    """Return a new record with multiple fields masked."""
    result = dict(record)
    for field in fields:
        result = mask_field(result, field, show_first=show_first, show_last=show_last, char=char)
    return result


def mask_pattern(
    record: Dict[str, Any],
    pattern: str,
    replacement: str = "[MASKED]",
) -> Dict[str, Any]:
    """Return a new record with regex pattern replaced in all string fields."""
    result = {}
    try:
        compiled = re.compile(pattern)
    except re.error:
        return record
    for key, value in record.items():
        if key == "__raw__":
            result[key] = value
        elif isinstance(value, str):
            result[key] = compiled.sub(replacement, value)
        else:
            result[key] = value
    return result


def mask_records(
    records: Iterable[Dict[str, Any]],
    fields: Optional[List[str]] = None,
    pattern: Optional[str] = None,
    show_first: int = 0,
    show_last: int = 0,
    char: str = "*",
    replacement: str = "[MASKED]",
) -> Iterator[Dict[str, Any]]:
    """Apply field masking and/or pattern masking to an iterable of records."""
    for record in records:
        if fields:
            record = mask_fields(record, fields, show_first=show_first, show_last=show_last, char=char)
        if pattern:
            record = mask_pattern(record, pattern, replacement=replacement)
        yield record
