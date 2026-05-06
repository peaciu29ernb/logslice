"""Resample time-series log records into fixed-size time buckets with aggregation."""

from datetime import datetime, timezone, timedelta
from typing import Iterator, Dict, Any, Optional, List
from collections import defaultdict


def _to_float(value: Any) -> Optional[float]:
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def floor_to_interval(dt: datetime, interval_seconds: int) -> datetime:
    """Floor a datetime to the nearest interval boundary."""
    epoch = datetime(1970, 1, 1, tzinfo=timezone.utc)
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    total_seconds = int((dt - epoch).total_seconds())
    floored = (total_seconds // interval_seconds) * interval_seconds
    return epoch + timedelta(seconds=floored)


def resample_records(
    records: Iterator[Dict[str, Any]],
    time_field: str,
    value_field: str,
    interval_seconds: int = 60,
    agg: str = "mean",
    group_field: Optional[str] = None,
) -> List[Dict[str, Any]]:
    """Aggregate records into time buckets.

    agg: one of 'mean', 'sum', 'min', 'max', 'count'
    """
    buckets: Dict[Any, Dict[str, Any]] = defaultdict(lambda: {"values": [], "count": 0})

    for record in records:
        raw_time = record.get(time_field)
        if not isinstance(raw_time, datetime):
            continue
        value = _to_float(record.get(value_field))
        bucket_dt = floor_to_interval(raw_time, interval_seconds)
        group = record.get(group_field) if group_field else None
        key = (bucket_dt, group)
        buckets[key]["values"].append(value) if value is not None else None
        buckets[key]["count"] += 1
        buckets[key].setdefault("bucket", bucket_dt)
        buckets[key].setdefault("group", group)

    results = []
    for key in sorted(buckets):
        entry = buckets[key]
        values = entry["values"]
        if agg == "sum":
            agg_value = sum(values) if values else None
        elif agg == "min":
            agg_value = min(values) if values else None
        elif agg == "max":
            agg_value = max(values) if values else None
        elif agg == "count":
            agg_value = entry["count"]
        else:
            agg_value = (sum(values) / len(values)) if values else None

        row: Dict[str, Any] = {
            time_field: entry["bucket"].isoformat(),
            value_field: agg_value,
            "count": entry["count"],
        }
        if group_field:
            row[group_field] = entry["group"]
        results.append(row)

    return results


def format_resample_table(rows: List[Dict[str, Any]], time_field: str, value_field: str) -> str:
    """Format resampled rows as a plain-text table."""
    if not rows:
        return "(no data)"
    lines = [f"{'bucket':<30} {'value':>12} {'count':>8}"]
    lines.append("-" * 52)
    for row in rows:
        ts = str(row.get(time_field, ""))
        val = row.get(value_field)
        val_str = f"{val:.4f}" if isinstance(val, float) else str(val) if val is not None else "N/A"
        count = row.get("count", "")
        lines.append(f"{ts:<30} {val_str:>12} {count:>8}")
    return "\n".join(lines)
