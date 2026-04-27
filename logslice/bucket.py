"""Bucket records into fixed-size numeric ranges for a given field."""

from __future__ import annotations

from collections import defaultdict
from typing import Dict, Iterable, Iterator, List, Optional, Tuple


def _to_float(value) -> Optional[float]:
    """Attempt to convert a value to float; return None on failure."""
    if value is None:
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def floor_to_bucket(value: float, width: float) -> float:
    """Return the lower bound of the bucket that *value* falls into."""
    if width <= 0:
        raise ValueError(f"Bucket width must be positive, got {width!r}")
    import math
    return math.floor(value / width) * width


def bucket_records(
    records: Iterable[dict],
    field: str,
    width: float,
) -> Dict[float, List[dict]]:
    """Group *records* into numeric buckets of *width* based on *field*.

    Records where *field* is missing or non-numeric are silently skipped.
    Returns an ordered dict mapping bucket lower-bound -> list of records.
    """
    buckets: Dict[float, List[dict]] = defaultdict(list)
    for record in records:
        raw = record.get(field)
        value = _to_float(raw)
        if value is None:
            continue
        key = floor_to_bucket(value, width)
        buckets[key].append(record)
    return dict(sorted(buckets.items()))


def format_bucket_table(
    buckets: Dict[float, List[dict]],
    width: float,
) -> str:
    """Render a simple text table summarising each bucket."""
    if not buckets:
        return "(no data)"

    lines: List[str] = []
    header = f"{'Bucket':<20} {'Count':>8}"
    lines.append(header)
    lines.append("-" * len(header))

    for lower, recs in sorted(buckets.items()):
        upper = lower + width
        label = f"[{lower:g}, {upper:g})"
        lines.append(f"{label:<20} {len(recs):>8}")

    return "\n".join(lines)


def iter_bucket_records(
    records: Iterable[dict],
    field: str,
    width: float,
) -> Iterator[Tuple[float, dict]]:
    """Yield (bucket_lower_bound, record) pairs, skipping non-numeric rows."""
    for record in records:
        raw = record.get(field)
        value = _to_float(raw)
        if value is None:
            continue
        yield floor_to_bucket(value, width), record
