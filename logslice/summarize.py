"""Summarize records by computing aggregate statistics over a numeric field,
grouped by an optional key field."""

from __future__ import annotations

from collections import defaultdict
from typing import Dict, Iterable, List, Optional, Tuple


def _to_float(value) -> Optional[float]:
    """Attempt to coerce a value to float; return None on failure."""
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def summarize_records(
    records: Iterable[dict],
    value_field: str,
    group_field: Optional[str] = None,
) -> Dict[str, dict]:
    """Compute count, sum, min, max, and mean for *value_field*,
    optionally grouped by *group_field*.

    Returns a dict mapping group label -> stats dict.
    The special label "__all__" is used when no group_field is given.
    """
    buckets: Dict[str, List[float]] = defaultdict(list)

    for record in records:
        raw = record.get(value_field)
        num = _to_float(raw)
        if num is None:
            continue
        label = str(record.get(group_field, "__all__")) if group_field else "__all__"
        buckets[label].append(num)

    result: Dict[str, dict] = {}
    for label, values in sorted(buckets.items()):
        n = len(values)
        total = sum(values)
        result[label] = {
            "count": n,
            "sum": total,
            "min": min(values),
            "max": max(values),
            "mean": total / n,
        }
    return result


def format_summary_table(
    summary: Dict[str, dict],
    group_field: Optional[str] = None,
) -> str:
    """Render a summary dict as a plain-text table."""
    if not summary:
        return "(no data)"

    group_header = group_field or "group"
    header = f"{group_header:<20}  {'count':>7}  {'sum':>12}  {'min':>12}  {'max':>12}  {'mean':>12}"
    sep = "-" * len(header)
    rows: List[str] = [header, sep]

    for label, stats in summary.items():
        row = (
            f"{label:<20}  "
            f"{stats['count']:>7}  "
            f"{stats['sum']:>12.4g}  "
            f"{stats['min']:>12.4g}  "
            f"{stats['max']:>12.4g}  "
            f"{stats['mean']:>12.4g}"
        )
        rows.append(row)

    return "\n".join(rows)
