"""Tests for logslice.frequency."""

import pytest
from logslice.frequency import (
    count_values,
    frequency_records,
    format_frequency_table,
)


def make_records(values):
    return [{"level": v} for v in values]


# --- count_values ---

def test_count_values_basic():
    records = make_records(["info", "error", "info", "warn", "info"])
    counts = count_values(records, "level")
    assert counts["info"] == 3
    assert counts["error"] == 1
    assert counts["warn"] == 1


def test_count_values_missing_field_skipped():
    records = [{"level": "info"}, {"msg": "no level here"}, {"level": "error"}]
    counts = count_values(records, "level")
    assert counts["info"] == 1
    assert counts["error"] == 1
    assert len(counts) == 2


def test_count_values_none_value_skipped():
    records = [{"level": None}, {"level": "info"}]
    counts = count_values(records, "level")
    assert "None" not in counts
    assert counts["info"] == 1


def test_count_values_empty_input():
    counts = count_values([], "level")
    assert len(counts) == 0


# --- frequency_records ---

def test_frequency_records_sorted_by_count():
    records = make_records(["info"] * 5 + ["error"] * 2 + ["warn"])
    rows = list(frequency_records(records, "level"))
    assert rows[0]["level"] == "info"
    assert rows[0]["count"] == 5
    assert rows[1]["level"] == "error"
    assert rows[2]["level"] == "warn"


def test_frequency_records_pct_sums_to_100():
    records = make_records(["a"] * 3 + ["b"] * 7)
    rows = list(frequency_records(records, "level"))
    total_pct = sum(r["pct"] for r in rows)
    assert abs(total_pct - 100.0) < 0.01


def test_frequency_records_top_n_limits_output():
    records = make_records(["a"] * 10 + ["b"] * 5 + ["c"] * 2)
    rows = list(frequency_records(records, "level", top_n=2))
    assert len(rows) == 2
    assert rows[0]["level"] == "a"
    assert rows[1]["level"] == "b"


def test_frequency_records_min_count_filters():
    records = make_records(["a"] * 10 + ["b"])
    rows = list(frequency_records(records, "level", min_count=2))
    assert all(r["count"] >= 2 for r in rows)
    assert not any(r["level"] == "b" for r in rows)


def test_frequency_records_empty_input():
    rows = list(frequency_records([], "level"))
    assert rows == []


def test_frequency_records_total_field():
    records = make_records(["x", "y", "z"])
    rows = list(frequency_records(records, "level"))
    for row in rows:
        assert row["total"] == 3


# --- format_frequency_table ---

def test_format_frequency_table_contains_header():
    rows = [{"level": "info", "count": 5, "total": 5, "pct": 100.0}]
    table = format_frequency_table(rows, "level")
    assert "VALUE" in table
    assert "COUNT" in table
    assert "PCT" in table


def test_format_frequency_table_contains_value():
    rows = [{"level": "error", "count": 3, "total": 10, "pct": 30.0}]
    table = format_frequency_table(rows, "level")
    assert "error" in table
    assert "30.00%" in table


def test_format_frequency_table_empty_returns_no_data():
    table = format_frequency_table([], "level")
    assert table == "(no data)"
