"""Tests for logslice/percentile.py"""

import pytest
from logslice.percentile import (
    compute_percentile,
    percentile_records,
    format_percentile_table,
)


# --- compute_percentile ---

def test_compute_percentile_median_odd():
    assert compute_percentile([1.0, 2.0, 3.0], 50) == 2.0


def test_compute_percentile_median_even():
    result = compute_percentile([1.0, 2.0, 3.0, 4.0], 50)
    assert result == pytest.approx(2.5)


def test_compute_percentile_min():
    assert compute_percentile([10.0, 20.0, 30.0], 0) == 10.0


def test_compute_percentile_max():
    assert compute_percentile([10.0, 20.0, 30.0], 100) == 30.0


def test_compute_percentile_single_value():
    assert compute_percentile([42.0], 99) == 42.0


def test_compute_percentile_empty_returns_none():
    assert compute_percentile([], 50) is None


def test_compute_percentile_invalid_raises():
    with pytest.raises(ValueError):
        compute_percentile([1.0, 2.0], 101)


# --- percentile_records ---

def make_records():
    return [
        {"latency": "10", "service": "web"},
        {"latency": "20", "service": "web"},
        {"latency": "30", "service": "api"},
        {"latency": "40", "service": "api"},
        {"latency": "bad", "service": "web"},
        {"service": "web"},
    ]


def test_percentile_records_no_group():
    recs = [{"v": "1"}, {"v": "2"}, {"v": "3"}]
    result = percentile_records(recs, field="v", percentiles=[50.0])
    assert "_all" in result
    assert result["_all"]["p50"] == pytest.approx(2.0)
    assert result["_all"]["count"] == 3


def test_percentile_records_with_group():
    result = percentile_records(make_records(), field="latency", percentiles=[50.0], group_by="service")
    assert "web" in result
    assert "api" in result
    assert result["web"]["count"] == 2
    assert result["api"]["count"] == 2


def test_percentile_records_skips_non_numeric():
    recs = [{"v": "abc"}, {"v": "10"}, {"v": None}]
    result = percentile_records(recs, field="v", percentiles=[50.0])
    assert result["_all"]["count"] == 1


def test_percentile_records_empty_input():
    result = percentile_records([], field="v", percentiles=[50.0])
    assert result == {}


# --- format_percentile_table ---

def test_format_percentile_table_contains_headers():
    data = {"_all": {"p50": 2.0, "p99": 3.0, "count": 5}}
    table = format_percentile_table(data, percentiles=[50.0, 99.0])
    assert "p50" in table
    assert "p99" in table
    assert "count" in table


def test_format_percentile_table_empty_data():
    table = format_percentile_table({}, percentiles=[50.0])
    assert table == "(no data)"


def test_format_percentile_table_with_group():
    data = {
        "web": {"p50": 15.0, "count": 2},
        "api": {"p50": 35.0, "count": 2},
    }
    table = format_percentile_table(data, percentiles=[50.0], group_by="service")
    assert "web" in table
    assert "api" in table
    assert "group" in table
