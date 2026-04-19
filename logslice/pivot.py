"""Pivot log records: count occurrences of field values over time buckets."""

from collections import defaultdict
from datetime import datetime, timezone, timedelta
from typing import Iterable, Dict, List, Tuple, Optional

from logslice.filter import parse_timestamp


def floor_to_bucket(dt: datetime, bucket_seconds: int) -> datetime:
    """Round a datetime down to the nearest bucket boundary."""
    epoch = datetime(1970, 1, 1, tzinfo=timezone.utc)
    total_seconds = int((dt - epoch).total_seconds())
    floored = (total_seconds // bucket_seconds) * bucket_seconds
    return epoch + timedelta(seconds=floored)


def pivot_records(
    records: Iterable[dict],
    field: str,
    time_field: str = "time",
    bucket_seconds: int = 60,
) -> Dict[datetime, Dict[str, int]]:
    """
    Group records by time bucket and count occurrences of each value of `field`.

    Returns a dict mapping bucket datetime -> {field_value: count}.
    """
    result: Dict[datetime, Dict[str, int]] = defaultdict(lambda: defaultdict(int))

    for record in records:
        raw_time = record.get(time_field)
        if not raw_time:
            continue
        dt = parse_timestamp(str(raw_time))
        if dt is None:
            continue
        bucket = floor_to_bucket(dt, bucket_seconds)
        value = record.get(field)
        if value is None:
            continue
        result[bucket][str(value)] += 1

    return {k: dict(v) for k, v in sorted(result.items())}


def format_pivot_table(
    pivot: Dict[datetime, Dict[str, int]],
    field: str,
) -> str:
    """Render pivot table as aligned text."""
    if not pivot:
        return "(no data)"

    all_values: List[str] = sorted(
        {v for counts in pivot.values() for v in counts}
    )
    time_col = 22
    val_col = max(len(v) for v in all_values) + 2 if all_values else 10

    header = f"{'time':<{time_col}}" + "".join(f"{v:>{val_col}}" for v in all_values)
    separator = "-" * len(header)
    lines = [f"pivot by: {field}", separator, header, separator]

    for bucket, counts in sorted(pivot.items()):
        ts = bucket.strftime("%Y-%m-%dT%H:%M:%SZ")
        row = f"{ts:<{time_col}}" + "".join(
            f"{counts.get(v, 0):>{val_col}}" for v in all_values
        )
        lines.append(row)

    lines.append(separator)
    return "\n".join(lines)
