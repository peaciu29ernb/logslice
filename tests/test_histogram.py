"""Tests for logslice.histogram."""

import pytest
from logslice.histogram import (
    _to_float,
    compute_histogram,
    format_histogram_table,
    iter_histogram_records,
)


def make_records(values, field="val"):
    return [{field: v} for v in values]


# _to_float

def test_to_float_numeric_string():
    assert _to_float("3.14") == pytest.approx(3.14)

def test_to_float_int():
    assert _to_float(5) == 5.0

def test_to_float_none_returns_none():
    assert _to_float(None) is None

def test_to_float_non_numeric_returns_none():
    assert _to_float("abc") is None


# compute_histogram

def test_histogram_empty_records():
    assert compute_histogram([], "val") == []

def test_histogram_bin_count():
    records = make_records(range(10))
    buckets = compute_histogram(records, "val", bins=5)
    assert len(buckets) == 5

def test_histogram_total_count():
    records = make_records(range(20))
    buckets = compute_histogram(records, "val", bins=4)
    total = sum(c for _, _, c in buckets)
    assert total == 20

def test_histogram_all_same_value():
    records = make_records([5.0] * 8)
    buckets = compute_histogram(records, "val", bins=4)
    total = sum(c for _, _, c in buckets)
    assert total == 8

def test_histogram_skips_non_numeric():
    records = [{"val": "x"}, {"val": 1.0}, {"val": None}, {"val": 2.0}]
    buckets = compute_histogram(records, "val", bins=2)
    total = sum(c for _, _, c in buckets)
    assert total == 2

def test_histogram_respects_min_max():
    records = make_records([0, 5, 10, 15, 20])
    buckets = compute_histogram(records, "val", bins=2, min_val=0.0, max_val=20.0)
    assert len(buckets) == 2
    assert buckets[0][0] == pytest.approx(0.0)
    assert buckets[-1][1] == pytest.approx(20.0)

def test_histogram_missing_field_skipped():
    records = [{"other": 1}, {"val": 3.0}]
    buckets = compute_histogram(records, "val", bins=1)
    total = sum(c for _, _, c in buckets)
    assert total == 1


# format_histogram_table

def test_format_histogram_table_empty():
    assert format_histogram_table([]) == "(no data)"

def test_format_histogram_table_contains_hash():
    buckets = [(0.0, 1.0, 5), (1.0, 2.0, 3)]
    output = format_histogram_table(buckets)
    assert "#" in output

def test_format_histogram_table_line_count():
    buckets = [(float(i), float(i + 1), i + 1) for i in range(4)]
    lines = format_histogram_table(buckets).splitlines()
    assert len(lines) == 4


# iter_histogram_records

def test_iter_histogram_records_keys():
    buckets = [(0.0, 1.0, 3)]
    recs = list(iter_histogram_records(buckets))
    assert recs[0].keys() == {"bucket_start", "bucket_end", "count"}

def test_iter_histogram_records_values():
    buckets = [(0.0, 5.0, 7)]
    recs = list(iter_histogram_records(buckets))
    assert recs[0]["count"] == 7
    assert recs[0]["bucket_start"] == pytest.approx(0.0)
    assert recs[0]["bucket_end"] == pytest.approx(5.0)

def test_iter_histogram_records_count():
    buckets = [(float(i), float(i + 1), i) for i in range(6)]
    recs = list(iter_histogram_records(buckets))
    assert len(recs) == 6
