"""Histogram: bucket numeric field values and count occurrences per bucket."""

from typing import Iterator, Optional
import math


def _to_float(value) -> Optional[float]:
    if value is None:
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def compute_histogram(records, field: str, bins: int = 10, min_val: Optional[float] = None, max_val: Optional[float] = None):
    """Collect values and compute histogram bucket counts.

    Returns a list of (bucket_start, bucket_end, count) tuples.
    """
    values = []
    for rec in records:
        v = _to_float(rec.get(field))
        if v is not None:
            values.append(v)

    if not values:
        return []

    lo = min_val if min_val is not None else min(values)
    hi = max_val if max_val is not None else max(values)

    if lo == hi:
        hi = lo + 1.0

    width = (hi - lo) / bins
    counts = [0] * bins

    for v in values:
        idx = int((v - lo) / width)
        if idx >= bins:
            idx = bins - 1
        if idx < 0:
            idx = 0
        counts[idx] += 1

    buckets = []
    for i in range(bins):
        start = lo + i * width
        end = lo + (i + 1) * width
        buckets.append((start, end, counts[i]))

    return buckets


def format_histogram_table(buckets, bar_width: int = 30) -> str:
    """Render histogram buckets as an ASCII bar chart."""
    if not buckets:
        return "(no data)"

    max_count = max(c for _, _, c in buckets)
    lines = []
    for start, end, count in buckets:
        bar_len = int(bar_width * count / max_count) if max_count > 0 else 0
        bar = "#" * bar_len
        lines.append(f"[{start:>10.3f}, {end:>10.3f}) | {bar:<{bar_width}} {count}")
    return "\n".join(lines)


def iter_histogram_records(buckets) -> Iterator[dict]:
    """Yield each bucket as a structured record."""
    for start, end, count in buckets:
        yield {"bucket_start": start, "bucket_end": end, "count": count}
