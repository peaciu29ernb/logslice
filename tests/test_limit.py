"""Tests for logslice.limit."""

import pytest

from logslice.limit import skip_records, limit_records, limit_offset_records


def make_records(n: int) -> list[dict]:
    return [{"i": i, "_raw": str(i)} for i in range(n)]


# ---------------------------------------------------------------------------
# skip_records
# ---------------------------------------------------------------------------

def test_skip_zero_returns_all():
    records = make_records(5)
    assert list(skip_records(records, 0)) == records


def test_skip_some():
    records = make_records(5)
    result = list(skip_records(records, 2))
    assert [r["i"] for r in result] == [2, 3, 4]


def test_skip_more_than_available_returns_empty():
    records = make_records(3)
    assert list(skip_records(records, 10)) == []


def test_skip_exact_count_returns_empty():
    records = make_records(4)
    assert list(skip_records(records, 4)) == []


def test_skip_negative_raises():
    with pytest.raises(ValueError, match="non-negative"):
        list(skip_records(make_records(3), -1))


# ---------------------------------------------------------------------------
# limit_records
# ---------------------------------------------------------------------------

def test_limit_zero_returns_empty():
    assert list(limit_records(make_records(5), 0)) == []


def test_limit_fewer_than_available():
    records = make_records(10)
    result = list(limit_records(records, 3))
    assert [r["i"] for r in result] == [0, 1, 2]


def test_limit_more_than_available_returns_all():
    records = make_records(4)
    assert list(limit_records(records, 100)) == records


def test_limit_exact_count():
    records = make_records(5)
    assert list(limit_records(records, 5)) == records


def test_limit_negative_raises():
    with pytest.raises(ValueError, match="non-negative"):
        list(limit_records(make_records(3), -1))


# ---------------------------------------------------------------------------
# limit_offset_records
# ---------------------------------------------------------------------------

def test_limit_offset_no_args_returns_all():
    records = make_records(5)
    assert list(limit_offset_records(records)) == records


def test_limit_offset_only_limit():
    records = make_records(8)
    result = list(limit_offset_records(records, count=3))
    assert [r["i"] for r in result] == [0, 1, 2]


def test_limit_offset_only_offset():
    records = make_records(6)
    result = list(limit_offset_records(records, offset=4))
    assert [r["i"] for r in result] == [4, 5]


def test_limit_offset_both():
    records = make_records(10)
    result = list(limit_offset_records(records, count=3, offset=2))
    assert [r["i"] for r in result] == [2, 3, 4]


def test_limit_offset_empty_input():
    assert list(limit_offset_records([], count=5, offset=2)) == []
