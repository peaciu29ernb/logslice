"""Clamp numeric field values to a specified [min, max] range."""

from typing import Any, Dict, Generator, Iterable, Optional


def _to_float(value: Any) -> Optional[float]:
    """Try to convert value to float; return None on failure."""
    if value is None:
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def clamp_value(
    value: Any,
    lo: Optional[float],
    hi: Optional[float],
) -> Any:
    """Return value clamped to [lo, hi].  Non-numeric values pass through."""
    numeric = _to_float(value)
    if numeric is None:
        return value
    if lo is not None and numeric < lo:
        # Preserve the original type where possible
        return type(value)(lo) if isinstance(value, (int, float)) else lo
    if hi is not None and numeric > hi:
        return type(value)(hi) if isinstance(value, (int, float)) else hi
    return value


def clamp_record(
    record: Dict[str, Any],
    fields: Iterable[str],
    lo: Optional[float],
    hi: Optional[float],
) -> Dict[str, Any]:
    """Return a new record with the named fields clamped to [lo, hi]."""
    out = dict(record)
    for field in fields:
        if field in out and field != "_raw":
            out[field] = clamp_value(out[field], lo, hi)
    return out


def clamp_records(
    records: Iterable[Dict[str, Any]],
    fields: Iterable[str],
    lo: Optional[float] = None,
    hi: Optional[float] = None,
) -> Generator[Dict[str, Any], None, None]:
    """Yield records with numeric fields clamped to [lo, hi]."""
    field_list = list(fields)
    for record in records:
        yield clamp_record(record, field_list, lo, hi)
