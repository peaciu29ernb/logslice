"""Tests for logslice.window."""

import pytest
from datetime import datetime, timezone
from logslice.window import (
    floor_to_window,
    tumbling_window,
    sliding_window,
    format_window_table,
)


def ts(iso: str) -> str:
    return iso


def make_record(time_str: str, level: str = "info") -> dict:
    return {"time": time_str, "level": level, "_raw": f'time={time_str} level={level}'}


def test_floor_to_window_aligns_to_60s():
    dt = datetime(2024, 1, 1, 12, 1, 45, tzinfo=timezone.utc)
    result = floor_to_window(dt, 60)
    assert result == datetime(2024, 1, 1, 12, 1, 0, tzinfo=timezone.utc)


def test_floor_to_window_already_aligned():
    dt = datetime(2024, 1, 1, 12, 0, 0, tzinfo=timezone.utc)
    result = floor_to_window(dt, 60)
    assert result == dt


def test_floor_to_window_300s():
    dt = datetime(2024, 1, 1, 12, 7, 30, tzinfo=timezone.utc)
    result = floor_to_window(dt, 300)
    assert result == datetime(2024, 1, 1, 12, 5, 0, tzinfo=timezone.utc)


def test_tumbling_window_groups_correctly():
    records = [
        make_record("2024-01-01T00:00:10Z"),
        make_record("2024-01-01T00:00:50Z"),
        make_record("2024-01-01T00:01:10Z"),
    ]
    result = tumbling_window(records, window_seconds=60)
    assert len(result) == 2
    counts = [len(v) for v in result.values()]
    assert sorted(counts) == [1, 2]


def test_tumbling_window_skips_missing_time():
    records = [
        make_record("2024-01-01T00:00:05Z"),
        {"level": "error", "_raw": "no time field"},
    ]
    result = tumbling_window(records, window_seconds=60)
    total = sum(len(v) for v in result.values())
    assert total == 1


def test_tumbling_window_empty_input():
    result = tumbling_window([], window_seconds=60)
    assert result == {}


def test_sliding_window_yields_windows():
    records = [
        make_record("2024-01-01T00:00:10Z"),
        make_record("2024-01-01T00:00:40Z"),
        make_record("2024-01-01T00:01:10Z"),
    ]
    windows = list(sliding_window(records, window_seconds=60, step_seconds=30))
    assert len(windows) >= 2
    for start, recs in windows:
        assert isinstance(recs, list)


def test_sliding_window_empty_input():
    result = list(sliding_window([], window_seconds=60, step_seconds=30))
    assert result == []


def test_sliding_window_overlap():
    records = [
        make_record("2024-01-01T00:00:10Z"),
        make_record("2024-01-01T00:00:50Z"),
    ]
    windows = list(sliding_window(records, window_seconds=60, step_seconds=30))
    # The first record should appear in more than one window
    total = sum(len(r) for _, r in windows)
    assert total > len(records)


def test_format_window_table_contains_header():
    records = [make_record("2024-01-01T00:00:05Z")]
    windows = tumbling_window(records, window_seconds=60)
    table = format_window_table(windows)
    assert "window_start" in table
    assert "count" in table


def test_format_window_table_shows_count():
    records = [
        make_record("2024-01-01T00:00:05Z"),
        make_record("2024-01-01T00:00:55Z"),
    ]
    windows = tumbling_window(records, window_seconds=60)
    table = format_window_table(windows)
    assert "2" in table
