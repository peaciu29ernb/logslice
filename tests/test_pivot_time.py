"""Tests for logslice.pivot_time."""

from datetime import datetime, timezone
import pytest
from logslice.pivot_time import (
    floor_to_interval,
    pivot_time_records,
    all_categories,
    format_pivot_time_table,
)


def dt(h: int, m: int, s: int = 0) -> datetime:
    return datetime(2024, 1, 1, h, m, s, tzinfo=timezone.utc)


def make_record(ts, category, value=1.0):
    return {"ts": ts, "svc": category, "latency": value, "_raw": ""}


# --- floor_to_interval ---

def test_floor_to_interval_aligns_to_60s():
    result = floor_to_interval(dt(10, 1, 45), 60)
    assert result == dt(10, 1, 0)


def test_floor_to_interval_already_aligned():
    result = floor_to_interval(dt(10, 5, 0), 60)
    assert result == dt(10, 5, 0)


def test_floor_to_interval_300s():
    result = floor_to_interval(dt(10, 7, 30), 300)
    assert result == dt(10, 5, 0)


def test_floor_to_interval_naive_datetime():
    naive = datetime(2024, 1, 1, 10, 1, 45)
    result = floor_to_interval(naive, 60)
    assert result.second == 0
    assert result.minute == 1


# --- pivot_time_records ---

def test_pivot_groups_by_bucket():
    records = [
        make_record(dt(10, 0, 10), "web"),
        make_record(dt(10, 0, 20), "db"),
        make_record(dt(10, 1, 5), "web"),
    ]
    table = pivot_time_records(records, "ts", "svc", "latency", interval_seconds=60)
    assert dt(10, 0, 0) in table
    assert dt(10, 1, 0) in table
    assert table[dt(10, 0, 0)]["web"] == 1.0
    assert table[dt(10, 0, 0)]["db"] == 1.0


def test_pivot_sum_aggregation():
    records = [
        make_record(dt(10, 0, 5), "web", 100.0),
        make_record(dt(10, 0, 15), "web", 200.0),
    ]
    table = pivot_time_records(records, "ts", "svc", "latency", agg="sum")
    assert table[dt(10, 0, 0)]["web"] == 300.0


def test_pivot_mean_aggregation():
    records = [
        make_record(dt(10, 0, 5), "web", 100.0),
        make_record(dt(10, 0, 15), "web", 200.0),
    ]
    table = pivot_time_records(records, "ts", "svc", "latency", agg="mean")
    assert table[dt(10, 0, 0)]["web"] == 150.0


def test_pivot_skips_missing_time_field():
    records = [{"svc": "web", "latency": 1.0, "_raw": ""}]
    table = pivot_time_records(records, "ts", "svc", "latency")
    assert len(table) == 0


def test_pivot_skips_non_datetime_time_field():
    records = [{"ts": "not-a-datetime", "svc": "web", "latency": 1.0, "_raw": ""}]
    table = pivot_time_records(records, "ts", "svc", "latency")
    assert len(table) == 0


def test_pivot_unknown_category_for_missing_field():
    records = [make_record(dt(10, 0, 0), "web")]
    records[0].pop("svc")
    table = pivot_time_records(records, "ts", "svc", "latency")
    assert "unknown" in table[dt(10, 0, 0)]


# --- all_categories ---

def test_all_categories_sorted():
    table = {
        dt(10, 0): {"web": 1.0, "db": 2.0},
        dt(10, 1): {"cache": 3.0},
    }
    assert all_categories(table) == ["cache", "db", "web"]


def test_all_categories_empty_table():
    assert all_categories({}) == []


# --- format_pivot_time_table ---

def test_format_returns_string():
    records = [make_record(dt(10, 0, 5), "web", 1.0)]
    table = pivot_time_records(records, "ts", "svc", "latency")
    output = format_pivot_time_table(table)
    assert isinstance(output, str)
    assert "web" in output


def test_format_empty_table():
    assert format_pivot_time_table({}) == "(no data)"


def test_format_fills_missing_cells():
    table = {
        dt(10, 0): {"web": 5.0},
        dt(10, 1): {"db": 3.0},
    }
    output = format_pivot_time_table(table, fill=0.0)
    assert "0.0" in output
