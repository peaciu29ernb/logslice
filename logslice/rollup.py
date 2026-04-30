"""rollup.py — aggregate numeric fields over time buckets or groups."""
from __future__ import annotations

from collections import defaultdict
from datetime import datetime, timezone
from typing import Any, Dict, Iterable, Iterator, List, Optional, Tuple

from logslice.filter import parse_timestamp


def _to_float(value: Any) -> Optional[float]:
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def _floor_to_interval(dt: datetime, seconds: int) -> datetime:
    ts = int(dt.timestamp())
    floored = ts - (ts % seconds)
    return datetime.fromtimestamp(floored, tz=timezone.utc)


def rollup_records(
    records: Iterable[dict],
    value_field: str,
    group_field: Optional[str] = None,
    time_field: str = "timestamp",
    interval_seconds: int = 60,
    ops: Tuple[str, ...] = ("sum", "count", "min", "max", "avg"),
) -> List[dict]:
    """Aggregate *value_field* per time bucket (and optional group)."""
    # bucket_key -> list of floats
    buckets: Dict[Tuple, List[float]] = defaultdict(list)

    for rec in records:
        raw_ts = rec.get(time_field)
        dt = parse_timestamp(str(raw_ts)) if raw_ts is not None else None
        bucket_ts = _floor_to_interval(dt, interval_seconds) if dt else None
        bucket_label = bucket_ts.isoformat() if bucket_ts else "unknown"

        group_val = rec.get(group_field, "_all") if group_field else "_all"
        val = _to_float(rec.get(value_field))
        if val is None:
            continue
        buckets[(bucket_label, str(group_val))].append(val)

    results: List[dict] = []
    for (bucket_label, group_val), values in sorted(buckets.items()):
        row: dict = {"bucket": bucket_label, "count": len(values)}
        if group_field:
            row[group_field] = group_val
        if "sum" in ops:
            row["sum"] = sum(values)
        if "min" in ops:
            row["min"] = min(values)
        if "max" in ops:
            row["max"] = max(values)
        if "avg" in ops:
            row["avg"] = sum(values) / len(values)
        results.append(row)
    return results


def format_rollup_table(rows: List[dict], group_field: Optional[str] = None) -> str:
    if not rows:
        return "(no data)"
    cols = ["bucket"]
    if group_field:
        cols.append(group_field)
    cols += [k for k in rows[0] if k not in cols]
    header = "  ".join(f"{c:<20}" for c in cols)
    sep = "-" * len(header)
    lines = [header, sep]
    for row in rows:
        lines.append("  ".join(f"{str(row.get(c, '')):<20}" for c in cols))
    return "\n".join(lines)
