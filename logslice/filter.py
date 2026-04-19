"""Filter log records by time range or field patterns."""

from datetime import datetime
from typing import Any, Dict, Iterator, Optional


def parse_timestamp(value: str) -> Optional[datetime]:
    """Try to parse a timestamp string into a datetime object."""
    formats = [
        "%Y-%m-%dT%H:%M:%S.%fZ",
        "%Y-%m-%dT%H:%M:%SZ",
        "%Y-%m-%dT%H:%M:%S",
        "%Y-%m-%d %H:%M:%S",
        "%Y-%m-%d %H:%M:%S.%f",
    ]
    for fmt in formatsn

def record_time_range(
    record: Dict[str,
    time_field: str,
    start: Optional[datetime],
    end: Optional[datetime],
) -> bool:
    """Return True if the record's timestamp falls within [start, end]."""
    if start is None and end is None:
        return True
    raw = record.get(time_field)
    if raw is None:
        return False
    ts = parse_timestamp(str(raw))
    if ts is None:
        return False
    if start is not None and ts < start:
        return False
    if end is not None and ts > end:
        return False
    return True


def record_matches_pattern(record: Dict[str, Any], field: str, pattern: str) -> bool:
    """Return True if the field value contains the pattern (case-sensitive substring)."""
    value = record.get(field)
    if value is None:
        return False
    return pattern in str(value)


def filter_records(
    records: Iterator[Dict[str, Any]],
    time_field: str = "timestamp",
    start: Optional[datetime] = None,
    end: Optional[datetime] = None,
    field_patterns: Optional[Dict[str, str]] = None,
) -> Iterator[Dict[str, Any]]:
    """Yield records that match the time range and all field patterns."""
    for record in records:
        if not record_in_time_range(record, time_field, start, end):
            continue
        if field_patterns:
            if not all(
                record_matches_pattern(record, f, p)
                for f, p in field_patterns.items()
            ):
                continue
        yield record
