"""Field annotation: add derived or computed fields to log records."""

import re
from typing import Any, Callable, Dict, Iterable, List, Optional


def annotate_with_value(record: dict, field: str, value: Any) -> dict:
    """Return a new record with a static value added under `field`."""
    out = dict(record)
    out[field] = value
    return out


def annotate_with_extract(
    record: dict,
    src_field: str,
    dest_field: str,
    pattern: str,
    group: int = 1,
) -> dict:
    """Extract a regex group from `src_field` and store it in `dest_field`.

    If the field is absent or the pattern does not match, `dest_field` is set
    to None.
    """
    out = dict(record)
    raw_value = record.get(src_field)
    if raw_value is None:
        out[dest_field] = None
        return out
    try:
        m = re.search(pattern, str(raw_value))
        out[dest_field] = m.group(group) if m else None
    except (re.error, IndexError):
        out[dest_field] = None
    return out


def annotate_with_template(
    record: dict,
    dest_field: str,
    template: str,
) -> dict:
    """Render `template` using record fields (Python str.format_map) and store
    the result in `dest_field`.  Missing keys produce an empty string.
    """
    out = dict(record)

    class _DefaultDict(dict):
        def __missing__(self, key: str) -> str:
            return ""

    try:
        out[dest_field] = template.format_map(_DefaultDict(record))
    except (ValueError, KeyError):
        out[dest_field] = ""
    return out


def apply_annotations(
    record: dict,
    annotations: List[Callable[[dict], dict]],
) -> dict:
    """Apply a list of annotation callables in order, threading the record."""
    for fn in annotations:
        record = fn(record)
    return record


def annotate_records(
    records: Iterable[dict],
    annotations: List[Callable[[dict], dict]],
) -> Iterable[dict]:
    """Yield each record after applying all annotation functions."""
    for record in records:
        yield apply_annotations(record, annotations)
