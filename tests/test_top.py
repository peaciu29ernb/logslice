"""Tests for logslice.top and logslice.cli_top."""

from __future__ import annotations

import argparse
import pytest

from logslice.top import _to_float, top_records, top_records_iter, format_top_table
from logslice.cli_top import (
    register_top_args,
    is_top_active,
    extract_top_kwargs,
    validate_top_args,
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
    assert _to_float("high") is None


# ---------------------------------------------------------------------------
# top_records
# ---------------------------------------------------------------------------

def make_records():
    return [
        {"msg": "a", "score": "10"},
        {"msg": "b", "score": "50"},
        {"msg": "c", "score": "30"},
        {"msg": "d", "score": "20"},
        {"msg": "e"},  # missing field
        {"msg": "f", "score": "bad"},  # non-numeric
    ]


def test_top_returns_highest_by_default():
    result = top_records(make_records(), field="score", n=2)
    assert [r["msg"] for r in result] == ["b", "c"]


def test_top_ascending_returns_lowest():
    result = top_records(make_records(), field="score", n=2, ascending=True)
    assert [r["msg"] for r in result] == ["a", "d"]


def test_top_skips_missing_field():
    result = top_records(make_records(), field="score", n=10)
    assert all("score" in r for r in result)


def test_top_n_zero_returns_empty():
    assert top_records(make_records(), field="score", n=0) == []


def test_top_n_larger_than_available():
    result = top_records(make_records(), field="score", n=100)
    assert len(result) == 4  # only 4 valid numeric records


def test_top_empty_input():
    assert top_records([], field="score", n=5) == []


def test_top_records_iter_yields_same_as_list():
    expected = top_records(make_records(), field="score", n=3)
    result = list(top_records_iter(make_records(), field="score", n=3))
    assert result == expected


# ---------------------------------------------------------------------------
# format_top_table
# ---------------------------------------------------------------------------

def test_format_top_table_contains_rank():
    recs = top_records(make_records(), field="score", n=2)
    table = format_top_table(recs, field="score")
    assert "Rank" in table
    assert "1" in table


def test_format_top_table_empty():
    table = format_top_table([], field="score")
    assert "no records" in table


# ---------------------------------------------------------------------------
# cli_top
# ---------------------------------------------------------------------------

def make_parser():
    p = argparse.ArgumentParser()
    register_top_args(p)
    return p


def test_register_adds_top_field():
    p = make_parser()
    args = p.parse_args(["--top-field", "latency"])
    assert args.top_field == "latency"


def test_register_default_n_is_10():
    p = make_parser()
    args = p.parse_args([])
    assert args.top_n == 10


def test_register_top_asc_default_false():
    p = make_parser()
    args = p.parse_args([])
    assert args.top_asc is False


def test_is_top_active_true():
    p = make_parser()
    args = p.parse_args(["--top-field", "score"])
    assert is_top_active(args) is True


def test_is_top_active_false():
    p = make_parser()
    args = p.parse_args([])
    assert is_top_active(args) is False


def test_extract_top_kwargs():
    p = make_parser()
    args = p.parse_args(["--top-field", "score", "--top-n", "5", "--top-asc"])
    kwargs = extract_top_kwargs(args)
    assert kwargs == {"field": "score", "n": 5, "ascending": True}


def test_validate_top_args_invalid_n():
    p = make_parser()
    args = p.parse_args(["--top-field", "score", "--top-n", "0"])
    errors = validate_top_args(args)
    assert any("positive" in e for e in errors)


def test_validate_top_args_valid():
    p = make_parser()
    args = p.parse_args(["--top-field", "score", "--top-n", "3"])
    assert validate_top_args(args) == []
