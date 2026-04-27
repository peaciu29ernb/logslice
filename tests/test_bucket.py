"""Tests for logslice.bucket."""

import pytest

from logslice.bucket import (
    _to_float,
    floor_to_bucket,
    bucket_records,
    format_bucket_table,
    iter_bucket_records,
)


# ---------------------------------------------------------------------------
# _to_float
# ---------------------------------------------------------------------------

def test_to_float_numeric_string():
    assert _to_float("3.14") == pytest.approx(3.14)


def test_to_float_int():
    assert _to_float(42) == 42.0


def test_to_float_none_returns_none():
    assert _to_float(None) is None


def test_to_float_non_numeric_returns_none():
    assert _to_float("abc") is None


# ---------------------------------------------------------------------------
# floor_to_bucket
# ---------------------------------------------------------------------------

def test_floor_to_bucket_basic():
    assert floor_to_bucket(7.3, 5.0) == pytest.approx(5.0)


def test_floor_to_bucket_already_aligned():
    assert floor_to_bucket(10.0, 5.0) == pytest.approx(10.0)


def test_floor_to_bucket_negative_value():
    assert floor_to_bucket(-3.0, 5.0) == pytest.approx(-5.0)


def test_floor_to_bucket_width_one():
    assert floor_to_bucket(9.9, 1.0) == pytest.approx(9.0)


def test_floor_to_bucket_invalid_width_raises():
    with pytest.raises(ValueError):
        floor_to_bucket(5.0, 0)


# ---------------------------------------------------------------------------
# bucket_records
# ---------------------------------------------------------------------------

def make_records():
    return [
        {"latency": "12", "_raw": "a"},
        {"latency": "7", "_raw": "b"},
        {"latency": "23", "_raw": "c"},
        {"latency": "8", "_raw": "d"},
        {"latency": "bad", "_raw": "e"},
        {"other": "x", "_raw": "f"},
    ]


def test_bucket_records_groups_correctly():
    result = bucket_records(make_records(), "latency", 10.0)
    assert set(result.keys()) == {0.0, 10.0, 20.0}
    assert len(result[0.0]) == 2   # 7, 8
    assert len(result[10.0]) == 1  # 12
    assert len(result[20.0]) == 1  # 23


def test_bucket_records_skips_non_numeric():
    result = bucket_records(make_records(), "latency", 10.0)
    total = sum(len(v) for v in result.values())
    assert total == 4  # "bad" and missing field are excluded


def test_bucket_records_empty_input():
    assert bucket_records([], "latency", 5.0) == {}


def test_bucket_records_sorted_keys():
    result = bucket_records(make_records(), "latency", 10.0)
    keys = list(result.keys())
    assert keys == sorted(keys)


# ---------------------------------------------------------------------------
# format_bucket_table
# ---------------------------------------------------------------------------

def test_format_bucket_table_contains_bucket_label():
    buckets = {0.0: [{}, {}], 10.0: [{}]}
    table = format_bucket_table(buckets, 10.0)
    assert "[0, 10)" in table
    assert "[10, 20)" in table


def test_format_bucket_table_contains_counts():
    buckets = {0.0: [{}, {}], 10.0: [{}]}
    table = format_bucket_table(buckets, 10.0)
    assert "2" in table
    assert "1" in table


def test_format_bucket_table_empty():
    assert format_bucket_table({}, 10.0) == "(no data)"


# ---------------------------------------------------------------------------
# iter_bucket_records
# ---------------------------------------------------------------------------

def test_iter_bucket_records_yields_pairs():
    records = [{"v": "5"}, {"v": "15"}, {"v": "nope"}]
    pairs = list(iter_bucket_records(records, "v", 10.0))
    assert len(pairs) == 2
    assert pairs[0] == (0.0, {"v": "5"})
    assert pairs[1] == (10.0, {"v": "15"})


def test_iter_bucket_records_skips_missing_field():
    records = [{"x": 1}, {"v": "5"}]
    pairs = list(iter_bucket_records(records, "v", 10.0))
    assert len(pairs) == 1
