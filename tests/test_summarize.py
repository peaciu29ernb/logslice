"""Tests for logslice.summarize."""

import pytest
from logslice.summarize import summarize_records, format_summary_table


def make_records(rows):
    return [{"val": v, "env": e} for v, e in rows]


# ---------------------------------------------------------------------------
# summarize_records
# ---------------------------------------------------------------------------

def test_no_group_single_bucket():
    records = [{"val": "10"}, {"val": "20"}, {"val": "30"}]
    result = summarize_records(records, value_field="val")
    assert list(result.keys()) == ["__all__"]
    s = result["__all__"]
    assert s["count"] == 3
    assert s["sum"] == pytest.approx(60.0)
    assert s["min"] == pytest.approx(10.0)
    assert s["max"] == pytest.approx(30.0)
    assert s["mean"] == pytest.approx(20.0)


def test_group_by_field():
    records = make_records([("1", "prod"), ("3", "prod"), ("2", "staging")])
    result = summarize_records(records, value_field="val", group_field="env")
    assert set(result.keys()) == {"prod", "staging"}
    assert result["prod"]["count"] == 2
    assert result["prod"]["sum"] == pytest.approx(4.0)
    assert result["staging"]["count"] == 1
    assert result["staging"]["mean"] == pytest.approx(2.0)


def test_non_numeric_values_skipped():
    records = [{"val": "abc"}, {"val": "5"}, {"val": None}]
    result = summarize_records(records, value_field="val")
    assert result["__all__"]["count"] == 1
    assert result["__all__"]["sum"] == pytest.approx(5.0)


def test_missing_value_field_skipped():
    records = [{"other": "1"}, {"val": "7"}]
    result = summarize_records(records, value_field="val")
    assert result["__all__"]["count"] == 1


def test_empty_records_returns_empty_dict():
    result = summarize_records([], value_field="val")
    assert result == {}


def test_all_non_numeric_returns_empty_dict():
    records = [{"val": "n/a"}, {"val": ""}]
    result = summarize_records(records, value_field="val")
    assert result == {}


def test_float_values_accepted():
    records = [{"val": 1.5}, {"val": 2.5}]
    result = summarize_records(records, value_field="val")
    assert result["__all__"]["mean"] == pytest.approx(2.0)


# ---------------------------------------------------------------------------
# format_summary_table
# ---------------------------------------------------------------------------

def test_format_empty_returns_no_data():
    assert format_summary_table({}) == "(no data)"


def test_format_contains_group_label():
    records = [{"val": "10", "env": "prod"}]
    summary = summarize_records(records, value_field="val", group_field="env")
    table = format_summary_table(summary, group_field="env")
    assert "prod" in table
    assert "env" in table


def test_format_contains_stats_columns():
    records = [{"val": "42"}]
    summary = summarize_records(records, value_field="val")
    table = format_summary_table(summary)
    for col in ("count", "sum", "min", "max", "mean"):
        assert col in table


def test_format_multiple_groups_sorted():
    records = make_records([("1", "z-env"), ("2", "a-env")])
    summary = summarize_records(records, value_field="val", group_field="env")
    table = format_summary_table(summary, group_field="env")
    lines = table.splitlines()
    # header + sep + 2 data rows
    assert len(lines) == 4
    assert lines[2].startswith("a-env")
    assert lines[3].startswith("z-env")
