"""Sliding and tumbling window aggregations over log records."""

from datetime import datetime, timedelta
from typing import Iterator, List, Dict, Any, Optional
from collections import defaultdict

from logslice.filter import parse_timestamp


def floor_to_window(dt: datetime, seconds: int) -> datetime:
    """Floor a datetime to the nearest window boundary."""
    epoch = datetime(1970, 1, 1, tzinfo=dt.tzinfo)
    delta = (dt - epoch).total_seconds()
    floored = (delta // seconds) * seconds
    return epoch + timedelta(seconds=floored)


def tumbling_window(
    records: List[Dict[str, Any]],
    window_seconds: int,
    time_field: str = "time",
) -> Dict[datetime, List[Dict[str, Any]]]:
    """Group records into non-overlapping tumbling windows."""
    buckets: Dict[datetime, List[Dict[str, Any]]] = defaultdict(list)
    for record in records:
        raw_ts = record.get(time_field)
        if raw_ts is None:
            continue
        ts = parse_timestamp(str(raw_ts))
        if ts is None:
            continue
        bucket = floor_to_window(ts, window_seconds)
        buckets[bucket].append(record)
    return dict(sorted(buckets.items()))


def sliding_window(
    records: List[Dict[str, Any]],
    window_seconds: int,
    step_seconds: int,
    time_field: str = "time",
) -> Iterator[tuple]:
    """Yield (window_start, window_records) for overlapping sliding windows."""
    timed: List[tuple] = []
    for record in records:
        raw_ts = record.get(time_field)
        if raw_ts is None:
            continue
        ts = parse_timestamp(str(raw_ts))
        if ts is None:
            continue
        timed.append((ts, record))

    if not timed:
        return

    timed.sort(key=lambda x: x[0])
    start_ts = floor_to_window(timed[0][0], step_seconds)
    end_ts = timed[-1][0]

    current = start_ts
    window_delta = timedelta(seconds=window_seconds)
    step_delta = timedelta(seconds=step_seconds)

    while current <= end_ts:
        window_end = current + window_delta
        bucket = [r for ts, r in timed if current <= ts < window_end]
        yield current, bucket
        current += step_delta


def format_window_table(
    windows: Dict[datetime, List[Dict[str, Any]]],
    count_only: bool = True,
) -> str:
    """Format tumbling window results as a text table."""
    lines = [f"{'window_start':<28} {'count':>8}"]
    lines.append("-" * 38)
    for bucket, recs in windows.items():
        lines.append(f"{bucket.isoformat():<28} {len(recs):>8}")
    return "\n".join(lines)
