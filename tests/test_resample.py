"""Tests for logslice.resample."""

from datetime import datetime, timezone
import pytest
from logslice.resample import floor_to_interval, resample_records, format_resample_table


def ts(iso: str) -> datetime:
    return datetime.fromisoformat(iso).replace(tzinfo=timezone.utc)


def make_record(t: datetime, value, group=None):
    r = {"time": t, "value": value}
    if group is not None:
        r["group"] = group
    return r


# --- floor_to_interval ---

def test_floor_to_interval_aligns_to_60s():
    dt = ts("2024-01-01T00:01:45")
    result = floor_to_interval(dt, 60)
    assert result.second == 0
    assert result.minute == 1


def test_floor_to_interval_already_aligned():
    dt = ts("2024-01-01T00:02:00")
    result = floor_to_interval(dt, 60)
    assert result == dt


def test_floor_to_interval_300s():
    dt = ts("2024-01-01T00:07:30")
    result = floor_to_interval(dt, 300)
    assert result.minute == 5
    assert result.second == 0


# --- resample_records ---

def test_resample_mean():
    records = [
        make_record(ts("2024-01-01T00:00:10"), 10),
        make_record(ts("2024-01-01T00:00:50"), 20),
        make_record(ts("2024-01-01T00:01:10"), 30),
    ]
    rows = resample_records(iter(records), "time", "value", interval_seconds=60, agg="mean")
    assert len(rows) == 2
    assert rows[0]["value"] == pytest.approx(15.0)
    assert rows[1]["value"] == pytest.approx(30.0)


def test_resample_sum():
    records = [
        make_record(ts("2024-01-01T00:00:05"), 3),
        make_record(ts("2024-01-01T00:00:55"), 7),
    ]
    rows = resample_records(iter(records), "time", "value", interval_seconds=60, agg="sum")
    assert rows[0]["value"] == pytest.approx(10.0)


def test_resample_count():
    records = [make_record(ts("2024-01-01T00:00:01"), v) for v in range(5)]
    rows = resample_records(iter(records), "time", "value", interval_seconds=60, agg="count")
    assert rows[0]["value"] == 5


def test_resample_min_max():
    records = [
        make_record(ts("2024-01-01T00:00:01"), 1),
        make_record(ts("2024-01-01T00:00:02"), 9),
        make_record(ts("2024-01-01T00:00:03"), 5),
    ]
    min_rows = resample_records(iter(records), "time", "value", interval_seconds=60, agg="min")
    max_rows = resample_records(iter(records), "time", "value", interval_seconds=60, agg="max")
    assert min_rows[0]["value"] == pytest.approx(1.0)
    assert max_rows[0]["value"] == pytest.approx(9.0)


def test_resample_skips_non_datetime():
    records = [
        {"time": "not-a-datetime", "value": 5},
        make_record(ts("2024-01-01T00:00:01"), 10),
    ]
    rows = resample_records(iter(records), "time", "value", interval_seconds=60)
    assert len(rows) == 1
    assert rows[0]["count"] == 1


def test_resample_skips_non_numeric_value():
    records = [
        make_record(ts("2024-01-01T00:00:01"), "bad"),
        make_record(ts("2024-01-01T00:00:02"), 4.0),
    ]
    rows = resample_records(iter(records), "time", "value", interval_seconds=60, agg="mean")
    assert rows[0]["value"] == pytest.approx(4.0)
    assert rows[0]["count"] == 2


def test_resample_empty_input():
    rows = resample_records(iter([]), "time", "value")
    assert rows == []


def test_resample_group_field():
    records = [
        make_record(ts("2024-01-01T00:00:01"), 10, group="A"),
        make_record(ts("2024-01-01T00:00:02"), 20, group="B"),
        make_record(ts("2024-01-01T00:00:03"), 30, group="A"),
    ]
    rows = resample_records(
        iter(records), "time", "value", interval_seconds=60, agg="sum", group_field="group"
    )
    by_group = {r["group"]: r["value"] for r in rows}
    assert by_group["A"] == pytest.approx(40.0)
    assert by_group["B"] == pytest.approx(20.0)


# --- format_resample_table ---

def test_format_resample_table_empty():
    assert format_resample_table([], "time", "value") == "(no data)"


def test_format_resample_table_has_header():
    rows = resample_records(
        iter([make_record(ts("2024-01-01T00:00:00"), 5)]),
        "time", "value", interval_seconds=60,
    )
    table = format_resample_table(rows, "time", "value")
    assert "bucket" in table
    assert "value" in table
    assert "count" in table
