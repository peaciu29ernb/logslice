"""Filter or flag records where a numeric field exceeds a threshold."""

from typing import Iterator, Optional


def _to_float(value) -> Optional[float]:
    """Attempt to convert a value to float, returning None on failure."""
    if value is None:
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def check_threshold(record: dict, field: str, op: str, value: float) -> Optional[bool]:
    """Return True/False if field satisfies the threshold condition, None if field missing/non-numeric."""
    raw = record.get(field)
    num = _to_float(raw)
    if num is None:
        return None
    ops = {
        "gt": num > value,
        "gte": num >= value,
        "lt": num < value,
        "lte": num <= value,
        "eq": num == value,
        "ne": num != value,
    }
    return ops.get(op)


def filter_by_threshold(
    records: Iterator[dict],
    field: str,
    op: str,
    value: float,
    invert: bool = False,
) -> Iterator[dict]:
    """Yield records where the field satisfies (or does not satisfy) the threshold."""
    for record in records:
        result = check_threshold(record, field, op, value)
        if result is None:
            continue
        if invert:
            result = not result
        if result:
            yield record


def flag_by_threshold(
    records: Iterator[dict],
    field: str,
    op: str,
    value: float,
    flag_field: str = "threshold_exceeded",
) -> Iterator[dict]:
    """Yield all records, annotating each with a boolean flag field."""
    for record in records:
        result = check_threshold(record, field, op, value)
        annotated = dict(record)
        annotated[flag_field] = bool(result) if result is not None else False
        if "_raw" in record:
            annotated["_raw"] = record["_raw"]
        yield annotated


OPS = ("gt", "gte", "lt", "lte", "eq", "ne")


def parse_threshold_arg(arg: str):
    """Parse 'field:op:value' string into (field, op, value) tuple or None."""
    parts = arg.split(":")
    if len(parts) != 3:
        return None
    field, op, raw_value = parts
    if not field or op not in OPS:
        return None
    try:
        value = float(raw_value)
    except ValueError:
        return None
    return field, op, value
