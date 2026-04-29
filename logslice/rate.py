"""Rate limiting and throttling for log record streams.

Provides functions to emit at most N records per time bucket,
useful for reducing noise from high-frequency log sources.
"""

from __future__ import annotations

from collections import defaultdict
from datetime import datetime, timezone
from typing import Iterator

from logslice.filter import parse_timestamp


def floor_to_second(dt: datetime, interval: int) -> datetime:
    """Floor a datetime to the nearest interval-second boundary."""
    ts = int(dt.replace(tzinfo=timezone.utc).timestamp())
    floored = (ts // interval) * interval
    return datetime.fromtimestamp(floored, tz=timezone.utc)


def rate_limit_records(
    records: Iterator[dict],
    max_per_bucket: int,
    interval: int = 1,
    time_field: str = "timestamp",
) -> Iterator[dict]:
    """Yield at most max_per_bucket records per interval-second window.

    Records without a parseable timestamp are always passed through.

    Args:
        records: Iterable of parsed log records.
        max_per_bucket: Maximum number of records to emit per time bucket.
        interval: Bucket size in seconds (default 1).
        time_field: Field name to parse the timestamp from.

    Yields:
        Records that fall within the rate limit.
    """
    if max_per_bucket <= 0:
        return

    counts: dict[datetime, int] = defaultdict(int)

    for record in records:
        raw_ts = record.get(time_field)
        if raw_ts is None:
            yield record
            continue

        dt = parse_timestamp(str(raw_ts))
        if dt is None:
            yield record
            continue

        bucket = floor_to_second(dt, interval)
        if counts[bucket] < max_per_bucket:
            counts[bucket] += 1
            yield record


def format_rate_summary(counts: dict[datetime, int]) -> str:
    """Format a summary of records-per-bucket counts as a table."""
    if not counts:
        return "(no data)"
    lines = ["bucket                     count"]
    lines.append("-" * 34)
    for bucket in sorted(counts):
        lines.append(f"{bucket.isoformat():<27} {counts[bucket]}")
    return "\n".join(lines)
