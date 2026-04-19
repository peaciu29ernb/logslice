"""Tests for logslice.sample."""

import pytest
from logslice.sample import reservoir_sample, rate_sample, nth_sample


def make_records(n):
    return [{"id": str(i), "_raw": f"id={i}"} for i in range(n)]


# --- reservoir_sample ---

def test_reservoir_returns_at_most_n():
    records = make_records(100)
    result = reservoir_sample(records, 10, seed=42)
    assert len(result) == 10


def test_reservoir_fewer_than_n():
    records = make_records(5)
    result = reservoir_sample(records, 20, seed=0)
    assert len(result) == 5


def test_reservoir_empty():
    assert reservoir_sample([], 10) == []


def test_reservoir_deterministic():
    records = make_records(50)
    r1 = reservoir_sample(records, 10, seed=7)
    r2 = reservoir_sample(records, 10, seed=7)
    assert r1 == r2


def test_reservoir_all_ids_valid():
    records = make_records(20)
    result = reservoir_sample(records, 5, seed=1)
    valid_ids = {r["id"] for r in records}
    for r in result:
        assert r["id"] in valid_ids


# --- rate_sample ---

def test_rate_sample_zero_yields_none():
    records = make_records(100)
    result = list(rate_sample(records, 0.0, seed=0))
    assert result == []


def test_rate_sample_one_yields_all():
    records = make_records(50)
    result = list(rate_sample(records, 1.0, seed=0))
    assert result == records


def test_rate_sample_invalid_rate():
    with pytest.raises(ValueError):
        list(rate_sample([], 1.5))
    with pytest.raises(ValueError):
        list(rate_sample([], -0.1))


def test_rate_sample_approximate():
    records = make_records(1000)
    result = list(rate_sample(records, 0.5, seed=99))
    assert 350 < len(result) < 650


# --- nth_sample ---

def test_nth_sample_every_one():
    records = make_records(10)
    assert list(nth_sample(records, 1)) == records


def test_nth_sample_every_other():
    records = make_records(6)
    result = list(nth_sample(records, 2))
    assert [r["id"] for r in result] == ["0", "2", "4"]


def test_nth_sample_invalid():
    with pytest.raises(ValueError):
        list(nth_sample([], 0))


def test_nth_sample_empty():
    assert list(nth_sample([], 3)) == []
