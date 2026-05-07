"""Tests for logslice.head."""

import pytest
from logslice.head import head_records, head_records_iter


def make_records(n: int) -> list[dict]:
    return [{"index": i, "msg": f"record {i}"} for i in range(n)]


# ---------------------------------------------------------------------------
# head_records
# ---------------------------------------------------------------------------

def test_head_returns_first_n():
    records = make_records(10)
    result = list(head_records(records, 3))
    assert len(result) == 3
    assert result[0]["index"] == 0
    assert result[2]["index"] == 2


def test_head_fewer_than_n_returns_all():
    records = make_records(4)
    result = list(head_records(records, 10))
    assert len(result) == 4


def test_head_empty_input_returns_empty():
    result = list(head_records([], 5))
    assert result == []


def test_head_zero_returns_empty():
    records = make_records(5)
    result = list(head_records(records, 0))
    assert result == []


def test_head_negative_returns_empty():
    records = make_records(5)
    result = list(head_records(records, -3))
    assert result == []


def test_head_exactly_n_records():
    records = make_records(5)
    result = list(head_records(records, 5))
    assert len(result) == 5


def test_head_preserves_record_content():
    records = [{"level": "info", "msg": "hello"}, {"level": "warn", "msg": "world"}]
    result = list(head_records(records, 1))
    assert result[0] == {"level": "info", "msg": "hello"}


def test_head_stops_consuming_iterator_early():
    """Generator should not consume more items than n."""
    consumed = []

    def gen():
        for i in range(20):
            consumed.append(i)
            yield {"index": i}

    list(head_records(gen(), 3))
    assert len(consumed) == 3


# ---------------------------------------------------------------------------
# head_records_iter
# ---------------------------------------------------------------------------

def test_head_records_iter_returns_list():
    records = make_records(6)
    result = head_records_iter(records, 4)
    assert isinstance(result, list)
    assert len(result) == 4


def test_head_records_iter_empty():
    result = head_records_iter([], 5)
    assert result == []


def test_head_records_iter_zero():
    result = head_records_iter(make_records(5), 0)
    assert result == []
