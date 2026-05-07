"""Detect and filter outlier records based on numeric field values."""

from typing import Iterator, Optional


def _to_float(value) -> Optional[float]:
    if value is None:
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def compute_bounds(records: list, field: str, multiplier: float = 1.5):
    """Compute IQR-based lower and upper bounds for outlier detection."""
    values = []
    for rec in records:
        v = _to_float(rec.get(field))
        if v is not None:
            values.append(v)

    if len(values) < 4:
        return None, None

    values.sort()
    n = len(values)
    q1 = values[n // 4]
    q3 = values[(3 * n) // 4]
    iqr = q3 - q1
    lower = q1 - multiplier * iqr
    upper = q3 + multiplier * iqr
    return lower, upper


def is_outlier(record: dict, field: str, lower, upper) -> bool:
    """Return True if the record's field value falls outside [lower, upper]."""
    if lower is None and upper is None:
        return False
    v = _to_float(record.get(field))
    if v is None:
        return False
    if lower is not None and v < lower:
        return True
    if upper is not None and v > upper:
        return True
    return False


def flag_outliers(
    records: list,
    field: str,
    dest: str = "outlier",
    multiplier: float = 1.5,
) -> Iterator[dict]:
    """Yield records with an added boolean field indicating outlier status."""
    lower, upper = compute_bounds(records, field, multiplier)
    for rec in records:
        flagged = dict(rec)
        flagged[dest] = is_outlier(rec, field, lower, upper)
        yield flagged


def filter_outliers(
    records: list,
    field: str,
    multiplier: float = 1.5,
    invert: bool = False,
) -> Iterator[dict]:
    """Yield only outlier records (or non-outliers if invert=True)."""
    lower, upper = compute_bounds(records, field, multiplier)
    for rec in records:
        outlier = is_outlier(rec, field, lower, upper)
        if invert:
            if not outlier:
                yield rec
        else:
            if outlier:
                yield rec
