"""Tests for logslice.outlier module."""

import pytest
from logslice.outlier import (
    _to_float,
    compute_bounds,
    is_outlier,
    flag_outliers,
    filter_outliers,
)


def make_records(values, field="latency"):
    return [{field: v, "_raw": f"{field}={v}"} for v in values]


# --- _to_float ---

def test_to_float_numeric_string():
    assert _to_float("3.14") == pytest.approx(3.14)

def test_to_float_int():
    assert _to_float(42) == 42.0

def test_to_float_none_returns_none():
    assert _to_float(None) is None

def test_to_float_non_numeric_returns_none():
    assert _to_float("abc") is None


# --- compute_bounds ---

def test_compute_bounds_basic():
    records = make_records([1, 2, 3, 4, 5, 6, 7, 8, 100])
    lower, upper = compute_bounds(records, "latency")
    assert lower is not None
    assert upper is not None
    assert upper < 100  # 100 should be above upper bound

def test_compute_bounds_too_few_values_returns_none():
    records = make_records([1, 2, 3])
    lower, upper = compute_bounds(records, "latency")
    assert lower is None
    assert upper is None

def test_compute_bounds_skips_non_numeric():
    records = make_records([1, 2, "bad", 4, 5, 6, 7, 8])
    lower, upper = compute_bounds(records, "latency")
    assert lower is not None
    assert upper is not None

def test_compute_bounds_missing_field():
    records = [{"other": 1}, {"other": 2}, {"other": 3}]
    lower, upper = compute_bounds(records, "latency")
    assert lower is None
    assert upper is None


# --- is_outlier ---

def test_is_outlier_above_upper():
    assert is_outlier({"v": 999}, "v", lower=0.0, upper=10.0) is True

def test_is_outlier_below_lower():
    assert is_outlier({"v": -50}, "v", lower=0.0, upper=10.0) is True

def test_is_outlier_within_range():
    assert is_outlier({"v": 5}, "v", lower=0.0, upper=10.0) is False

def test_is_outlier_none_bounds_returns_false():
    assert is_outlier({"v": 999}, "v", None, None) is False

def test_is_outlier_non_numeric_field_returns_false():
    assert is_outlier({"v": "text"}, "v", lower=0.0, upper=10.0) is False


# --- flag_outliers ---

def test_flag_outliers_adds_field():
    records = make_records([1, 2, 3, 4, 5, 6, 7, 8, 200])
    result = list(flag_outliers(records, "latency"))
    assert all("outlier" in r for r in result)

def test_flag_outliers_marks_extreme_value():
    records = make_records([1, 2, 3, 4, 5, 6, 7, 8, 200])
    result = list(flag_outliers(records, "latency"))
    assert result[-1]["outlier"] is True

def test_flag_outliers_custom_dest():
    records = make_records([1, 2, 3, 4, 5, 6, 7, 8, 200])
    result = list(flag_outliers(records, "latency", dest="is_anomaly"))
    assert "is_anomaly" in result[0]

def test_flag_outliers_does_not_mutate_original():
    records = make_records([1, 2, 3, 4, 5, 6, 7, 8, 200])
    originals = [dict(r) for r in records]
    list(flag_outliers(records, "latency"))
    for orig, rec in zip(originals, records):
        assert orig == rec


# --- filter_outliers ---

def test_filter_outliers_returns_only_outliers():
    records = make_records([1, 2, 3, 4, 5, 6, 7, 8, 200])
    result = list(filter_outliers(records, "latency"))
    assert len(result) == 1
    assert result[0]["latency"] == 200

def test_filter_outliers_invert_returns_non_outliers():
    records = make_records([1, 2, 3, 4, 5, 6, 7, 8, 200])
    result = list(filter_outliers(records, "latency", invert=True))
    assert all(r["latency"] != 200 for r in result)
    assert len(result) == 8

def test_filter_outliers_empty_input():
    result = list(filter_outliers([], "latency"))
    assert result == []
