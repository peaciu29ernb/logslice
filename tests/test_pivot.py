"""Tests for logslice.pivot."""

from datetime import datetime, timezone

import pytest

from logslice.pivot import floor_to_bucket, pivot_records, format_pivot_table


UTC = timezone.utc


def dt(s: str) -> datetime:
    return datetime.fromisoformat(s.replace("Z", "+00:00"))


def test_floor_to_bucket_aligns_to_minute():
    d = dt("2024-01-01T12:01:45Z")
    result = floor_to_bucket(d, 60)
    assert result == datetime(2024, 1, 1, 12, 1, 0, tzinfo=UTC)


def test_floor_to_bucket_already_aligned():
    d = dt("2024-01-01T12:00:00Z")
    assert floor_to_bucket(d, 60) == d


def test_floor_to_bucket_five_minutes():
    d = dt("2024-01-01T12:07:30Z")
    result = floor_to_bucket(d, 300)
    assert result == datetime(2024, 1, 1, 12, 5, 0, tzinfo=UTC)


RECORDS = [
    {"time": "2024-01-01T00:00:10Z", "level": "info"},
    {"time": "2024-01-01T00:00:20Z", "level": "error"},
    {"time": "2024-01-01T00:00:50Z", "level": "info"},
    {"time": "2024-01-01T00:01:05Z", "level": "warn"},
    {"time": "2024-01-01T00:01:55Z", "level": "error"},
]


def test_pivot_groups_by_bucket():
    result = pivot_records(RECORDS, field="level", bucket_seconds=60)
    assert len(result) == 2


def test_pivot_counts_values():
    result = pivot_records(RECORDS, field="level", bucket_seconds=60)
    bucket0 = datetime(2024, 1, 1, 0, 0, 0, tzinfo=UTC)
    assert result[bucket0]["info"] == 2
    assert result[bucket0]["error"] == 1


def test_pivot_skips_missing_time():
    records = [{"level": "info"}, {"time": "2024-01-01T00:00:00Z", "level": "info"}]
    result = pivot_records(records, field="level", bucket_seconds=60)
    assert len(result) == 1


def test_pivot_skips_missing_field():
    records = [{"time": "2024-01-01T00:00:00Z"}]
    result = pivot_records(records, field="level", bucket_seconds=60)
    assert result == {}


def test_pivot_skips_invalid_time():
    records = [{"time": "not-a-time", "level": "info"}]
    result = pivot_records(records, field="level", bucket_seconds=60)
    assert result == {}


def test_format_pivot_table_contains_field():
    result = pivot_records(RECORDS, field="level", bucket_seconds=60)
    table = format_pivot_table(result, field="level")
    assert "level" in table
    assert "info" in table
    assert "error" in table


def test_format_pivot_table_empty():
    assert format_pivot_table({}, field="level") == "(no data)"


def test_format_pivot_table_has_timestamp():
    result = pivot_records(RECORDS, field="level", bucket_seconds=60)
    table = format_pivot_table(result, field="level")
    assert "2024-01-01T00:00:00Z" in table
