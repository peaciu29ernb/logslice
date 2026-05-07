"""Z-score anomaly detection for numeric fields in log records."""

import math
from typing import Iterator, List, Optional


def _to_float(value) -> Optional[float]:
    """Attempt to coerce a value to float, return None on failure."""
    if value is None:
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def compute_mean_stddev(values: List[float]):
    """Return (mean, stddev) for a list of floats. Returns (0.0, 0.0) if empty."""
    n = len(values)
    if n == 0:
        return 0.0, 0.0
    mean = sum(values) / n
    variance = sum((v - mean) ** 2 for v in values) / n
    return mean, math.sqrt(variance)


def zscore_records(
    records: List[dict],
    field: str,
    dest: str = "zscore",
    threshold: Optional[float] = None,
    flag_field: Optional[str] = None,
) -> Iterator[dict]:
    """Annotate records with a z-score for the given numeric field.

    Args:
        records: List of parsed log records.
        field: Name of the numeric field to score.
        dest: Output field name for the computed z-score.
        threshold: If set, records with abs(zscore) >= threshold are flagged.
        flag_field: Field name to write the anomaly flag (default: "anomaly").

    Yields:
        Records with z-score (and optional flag) added.
    """
    if flag_field is None:
        flag_field = "anomaly"

    values = []
    for rec in records:
        v = _to_float(rec.get(field))
        values.append(v)

    numeric = [v for v in values if v is not None]
    mean, stddev = compute_mean_stddev(numeric)

    for rec, raw_v in zip(records, values):
        out = dict(rec)
        if raw_v is None or stddev == 0.0:
            out[dest] = None
        else:
            z = (raw_v - mean) / stddev
            out[dest] = round(z, 6)

        if threshold is not None:
            z_val = out[dest]
            if z_val is None:
                out[flag_field] = False
            else:
                out[flag_field] = abs(z_val) >= threshold

        yield out
