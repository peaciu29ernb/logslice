"""Time-based pivoting: group records by a time field and a category field."""

from datetime import datetime, timezone, timedelta
from collections import defaultdict
from typing import Iterable, Iterator, Dict, List, Optional, Tuple


def floor_to_interval(dt: datetime, interval_seconds: int) -> datetime:
    """Floor a datetime to the nearest interval boundary."""
    epoch = datetime(1970, 1, 1, tzinfo=timezone.utc)
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    total_seconds = int((dt - epoch).total_seconds())
    floored = (total_seconds // interval_seconds) * interval_seconds
    return epoch + timedelta(seconds=floored)


def pivot_time_records(
    records: Iterable[dict],
    time_field: str,
    category_field: str,
    value_field: str,
    interval_seconds: int = 60,
    agg: str = "count",
) -> Dict[datetime, Dict[str, float]]:
    """Group records by time bucket and category, aggregating a value field.

    Returns a dict mapping bucket -> category -> aggregated value.
    """
    buckets: Dict[datetime, Dict[str, List[float]]] = defaultdict(lambda: defaultdict(list))

    for record in records:
        raw_time = record.get(time_field)
        if not isinstance(raw_time, datetime):
            continue
        category = str(record.get(category_field, "unknown"))
        raw_val = record.get(value_field, 1)
        try:
            val = float(raw_val)
        except (TypeError, ValueError):
            val = 1.0
        bucket = floor_to_interval(raw_time, interval_seconds)
        buckets[bucket][category].append(val)

    result: Dict[datetime, Dict[str, float]] = {}
    for bucket, cats in sorted(buckets.items()):
        result[bucket] = {}
        for cat, vals in cats.items():
            if agg == "sum":
                result[bucket][cat] = sum(vals)
            elif agg == "min":
                result[bucket][cat] = min(vals)
            elif agg == "max":
                result[bucket][cat] = max(vals)
            elif agg == "mean":
                result[bucket][cat] = sum(vals) / len(vals)
            else:  # count
                result[bucket][cat] = float(len(vals))
    return result


def all_categories(table: Dict[datetime, Dict[str, float]]) -> List[str]:
    """Return sorted list of all category values seen across all buckets."""
    cats: set = set()
    for cats_dict in table.values():
        cats.update(cats_dict.keys())
    return sorted(cats)


def format_pivot_time_table(
    table: Dict[datetime, Dict[str, float]],
    fill: float = 0.0,
) -> str:
    """Format the pivot table as a plain-text grid."""
    if not table:
        return "(no data)"
    categories = all_categories(table)
    col_w = max(10, *(len(c) for c in categories))
    time_w = 20
    header = f"{'time':<{time_w}}" + "".join(f"  {c:>{col_w}}" for c in categories)
    rows = [header, "-" * len(header)]
    for bucket, cats in sorted(table.items()):
        ts = bucket.strftime("%Y-%m-%dT%H:%M:%SZ")
        row = f"{ts:<{time_w}}"
        for cat in categories:
            val = cats.get(cat, fill)
            row += f"  {val:>{col_w}.1f}"
        rows.append(row)
    return "\n".join(rows)
