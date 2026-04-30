"""Tests for logslice/threshold.py"""

import pytest
from logslice.threshold import (
    _to_float,
    check_threshold,
    filter_by_threshold,
    flag_by_threshold,
    parse_threshold_arg,
)


def make_record(field, value, raw="line"):
    return {field: value, "_raw": raw}


# --- _to_float ---

def test_to_float_numeric_string():
    assert _to_float("3.14") == pytest.approx(3.14)

def test_to_float_int():
    assert _to_float(42) == 42.0

def test_to_float_none_returns_none():
    assert _to_float(None) is None

def test_to_float_non_numeric_returns_none():
    assert _to_float("abc") is None


# --- check_threshold ---

def test_check_threshold_gt_true():
    assert check_threshold({"latency": 600}, "latency", "gt", 500) is True

def test_check_threshold_gt_false():
    assert check_threshold({"latency": 400}, "latency", "gt", 500) is False

def test_check_threshold_lte_true():
    assert check_threshold({"count": 10}, "count", "lte", 10) is True

def test_check_threshold_eq_true():
    assert check_threshold({"score": "7.5"}, "score", "eq", 7.5) is True

def test_check_threshold_missing_field_returns_none():
    assert check_threshold({}, "latency", "gt", 100) is None

def test_check_threshold_non_numeric_returns_none():
    assert check_threshold({"latency": "fast"}, "latency", "gt", 100) is None

def test_check_threshold_ne_true():
    assert check_threshold({"x": 5}, "x", "ne", 3) is True


# --- filter_by_threshold ---

def make_records():
    return [
        {"latency": 100},
        {"latency": 500},
        {"latency": 1000},
        {"latency": "bad"},
        {"other": 999},
    ]

def test_filter_gt_keeps_matching():
    result = list(filter_by_threshold(make_records(), "latency", "gt", 400))
    assert len(result) == 2
    assert all(r["latency"] > 400 for r in result)

def test_filter_skips_missing_and_non_numeric():
    result = list(filter_by_threshold(make_records(), "latency", "lt", 9999))
    assert all("latency" in r for r in result)
    assert all(r["latency"] != "bad" for r in result)

def test_filter_invert():
    result = list(filter_by_threshold(make_records(), "latency", "gt", 400, invert=True))
    assert len(result) == 1
    assert result[0]["latency"] == 100


# --- flag_by_threshold ---

def test_flag_adds_field():
    records = [{"latency": 600}, {"latency": 200}]
    result = list(flag_by_threshold(records, "latency", "gt", 500))
    assert result[0]["threshold_exceeded"] is True
    assert result[1]["threshold_exceeded"] is False

def test_flag_custom_field_name():
    records = [{"latency": 600}]
    result = list(flag_by_threshold(records, "latency", "gt", 500, flag_field="alert"))
    assert "alert" in result[0]

def test_flag_preserves_raw():
    records = [{"latency": 600, "_raw": "original line"}]
    result = list(flag_by_threshold(records, "latency", "gt", 500))
    assert result[0]["_raw"] == "original line"

def test_flag_missing_field_false():
    records = [{"other": 1}]
    result = list(flag_by_threshold(records, "latency", "gt", 500))
    assert result[0]["threshold_exceeded"] is False

def test_flag_does_not_mutate_original():
    original = {"latency": 600}
    list(flag_by_threshold([original], "latency", "gt", 500))
    assert "threshold_exceeded" not in original


# --- parse_threshold_arg ---

def test_parse_valid_arg():
    assert parse_threshold_arg("latency:gt:500") == ("latency", "gt", 500.0)

def test_parse_float_value():
    field, op, val = parse_threshold_arg("score:lte:9.5")
    assert val == pytest.approx(9.5)

def test_parse_missing_parts_returns_none():
    assert parse_threshold_arg("latency:gt") is None

def test_parse_invalid_op_returns_none():
    assert parse_threshold_arg("latency:bad:100") is None

def test_parse_non_numeric_value_returns_none():
    assert parse_threshold_arg("latency:gt:high") is None

def test_parse_empty_field_returns_none():
    assert parse_threshold_arg(":gt:100") is None
