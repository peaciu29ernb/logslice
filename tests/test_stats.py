"""Tests for logslice.stats."""
import pytest
from logslice.stats import compute_stats, format_stats


RECORDS = [
    {"timestamp": "2024-01-01T10:00:00Z", "level": "info", "msg": "started", "_raw": "..."},
    {"timestamp": "2024-01-01T10:01:00Z", "level": "warn", "msg": "slow query"},
    {"timestamp": "2024-01-01T10:02:00Z", "level": "info", "msg": "done"},
]


def test_total_count():
    stats = compute_stats(iter(RECORDS))
    assert stats["total"] == 3


def test_earliest_latest():
    stats = compute_stats(iter(RECORDS))
    assert stats["earliest"] == "2024-01-01T10:00:00Z"
    assert stats["latest"] == "2024-01-01T10:02:00Z"


def test_field_counts():
    stats = compute_stats(iter(RECORDS))
    assert stats["fields"]["level"] == 3
    assert stats["fields"]["msg"] == 3
    assert "_raw" not in stats["fields"]


def test_top_values():
    stats = compute_stats(iter(RECORDS))
    level_top = dict(stats["top_values"]["level"])
    assert level_top["info"] == 2
    assert level_top["warn"] == 1


def test_empty_records():
    stats = compute_stats(iter([]))
    assert stats["total"] == 0
    assert stats["earliest"] is None
    assert stats["latest"] is None
    assert stats["fields"] == {}


def test_no_timestamp_field():
    records = [{"level": "info", "msg": "hello"}]
    stats = compute_stats(iter(records))
    assert stats["earliest"] is None
    assert stats["latest"] is None


def test_format_stats_contains_total():
    stats = compute_stats(iter(RECORDS))
    output = format_stats(stats)
    assert "Total records" in output
    assert "3" in output


def test_format_stats_lists_fields():
    stats = compute_stats(iter(RECORDS))
    output = format_stats(stats)
    assert "level" in output
    assert "msg" in output


def test_format_stats_no_raw_field():
    stats = compute_stats(iter(RECORDS))
    output = format_stats(stats)
    assert "_raw" not in output
