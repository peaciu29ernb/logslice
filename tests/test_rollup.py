"""Tests for logslice/rollup.py."""
from __future__ import annotations

from datetime import datetime, timezone

import pytest

from logslice.rollup import _floor_to_interval, _to_float, format_rollup_table, rollup_records


def ts(iso: str) -> str:
    return iso


def make_record(timestamp: str, value, group=None) -> dict:
    rec = {"timestamp": timestamp, "latency": value}
    if group is not None:
        rec["service"] = group
    return rec


# ---------------------------------------------------------------------------
# _to_float
# ---------------------------------------------------------------------------

def test_to_float_numeric_string():
    assert _to_float("3.14") == pytest.approx(3.14)


def test_to_float_int():
    assert _to_float(42) == pytest.approx(42.0)


def test_to_float_none_returns_none():
    assert _to_float(None) is None


def test_to_float_non_numeric_returns_none():
    assert _to_float("abc") is None


# ---------------------------------------------------------------------------
# _floor_to_interval
# ---------------------------------------------------------------------------

def test_floor_to_interval_aligns_to_60s():
    dt = datetime(2024, 1, 1, 12, 1, 45, tzinfo=timezone.utc)
    result = _floor_to_interval(dt, 60)
    assert result == datetime(2024, 1, 1, 12, 1, 0, tzinfo=timezone.utc)


def test_floor_to_interval_already_aligned():
    dt = datetime(2024, 1, 1, 12, 0, 0, tzinfo=timezone.utc)
    result = _floor_to_interval(dt, 60)
    assert result == dt


# ---------------------------------------------------------------------------
# rollup_records
# ---------------------------------------------------------------------------

def test_rollup_single_bucket_sum():
    records = [
        make_record("2024-01-01T12:00:10Z", 100),
        make_record("2024-01-01T12:00:20Z", 200),
    ]
    rows = rollup_records(records, value_field="latency", ops=("sum",))
    assert len(rows) == 1
    assert rows[0]["sum"] == pytest.approx(300.0)


def test_rollup_two_buckets():
    records = [
        make_record("2024-01-01T12:00:10Z", 10),
        make_record("2024-01-01T12:01:10Z", 20),
    ]
    rows = rollup_records(records, value_field="latency", ops=("sum",))
    assert len(rows) == 2


def test_rollup_count():
    records = [make_record("2024-01-01T12:00:05Z", i) for i in range(5)]
    rows = rollup_records(records, value_field="latency", ops=("count",))
    assert rows[0]["count"] == 5


def test_rollup_min_max_avg():
    records = [
        make_record("2024-01-01T12:00:05Z", 10),
        make_record("2024-01-01T12:00:15Z", 30),
    ]
    rows = rollup_records(records, value_field="latency", ops=("min", "max", "avg"))
    assert rows[0]["min"] == pytest.approx(10.0)
    assert rows[0]["max"] == pytest.approx(30.0)
    assert rows[0]["avg"] == pytest.approx(20.0)


def test_rollup_group_field():
    records = [
        make_record("2024-01-01T12:00:05Z", 10, group="api"),
        make_record("2024-01-01T12:00:05Z", 20, group="db"),
    ]
    rows = rollup_records(records, value_field="latency", group_field="service", ops=("sum",))
    services = {r["service"] for r in rows}
    assert services == {"api", "db"}


def test_rollup_skips_non_numeric():
    records = [
        make_record("2024-01-01T12:00:05Z", "n/a"),
        make_record("2024-01-01T12:00:06Z", 50),
    ]
    rows = rollup_records(records, value_field="latency", ops=("sum",))
    assert rows[0]["sum"] == pytest.approx(50.0)


def test_rollup_empty_input():
    rows = rollup_records([], value_field="latency")
    assert rows == []


# ---------------------------------------------------------------------------
# format_rollup_table
# ---------------------------------------------------------------------------

def test_format_rollup_table_has_header():
    rows = [{"bucket": "2024-01-01T12:00:00+00:00", "count": 3, "sum": 90.0}]
    table = format_rollup_table(rows)
    assert "bucket" in table
    assert "sum" in table


def test_format_rollup_table_empty():
    assert format_rollup_table([]) == "(no data)"
