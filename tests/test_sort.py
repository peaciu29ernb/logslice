"""Tests for logslice.sort and logslice.cli_sort."""

import argparse
import pytest

from logslice.sort import _coerce_for_comparison, sort_records, sort_records_iter
from logslice.cli_sort import (
    extract_sort_kwargs,
    is_sort_active,
    register_sort_args,
)


# ---------------------------------------------------------------------------
# _coerce_for_comparison
# ---------------------------------------------------------------------------

def test_coerce_none_sorts_first():
    assert _coerce_for_comparison(None) < _coerce_for_comparison(0)


def test_coerce_numbers_before_strings():
    assert _coerce_for_comparison(1) < _coerce_for_comparison("a")


def test_coerce_bool_treated_as_number():
    assert _coerce_for_comparison(False) < _coerce_for_comparison(True)


# ---------------------------------------------------------------------------
# sort_records
# ---------------------------------------------------------------------------

RECORDS = [
    {"level": "warn",  "ts": "2024-01-03", "code": 3},
    {"level": "error", "ts": "2024-01-01", "code": 1},
    {"level": "info",  "ts": "2024-01-02", "code": 2},
]


def test_sort_single_field_ascending():
    result = sort_records(RECORDS, fields=["ts"])
    assert [r["ts"] for r in result] == ["2024-01-01", "2024-01-02", "2024-01-03"]


def test_sort_single_field_descending():
    result = sort_records(RECORDS, fields=["ts"], reverse=True)
    assert [r["ts"] for r in result] == ["2024-01-03", "2024-01-02", "2024-01-01"]


def test_sort_numeric_field():
    result = sort_records(RECORDS, fields=["code"])
    assert [r["code"] for r in result] == [1, 2, 3]


def test_sort_missing_field_sorts_first():
    recs = [{"x": 2}, {"x": None}, {"x": 1}]
    result = sort_records(recs, fields=["x"])
    assert result[0]["x"] is None


def test_sort_no_fields_returns_original_order():
    result = sort_records(RECORDS, fields=[])
    assert result == RECORDS


def test_sort_multi_field():
    recs = [
        {"level": "info",  "code": 2},
        {"level": "info",  "code": 1},
        {"level": "error", "code": 5},
    ]
    result = sort_records(recs, fields=["level", "code"])
    assert [(r["level"], r["code"]) for r in result] == [
        ("error", 5),
        ("info", 1),
        ("info", 2),
    ]


def test_sort_does_not_mutate_input():
    original = list(RECORDS)
    sort_records(RECORDS, fields=["ts"])
    assert RECORDS == original


def test_sort_records_iter_yields_sorted():
    result = list(sort_records_iter(RECORDS, fields=["code"]))
    assert [r["code"] for r in result] == [1, 2, 3]


# ---------------------------------------------------------------------------
# cli_sort helpers
# ---------------------------------------------------------------------------

def make_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser()
    register_sort_args(p)
    return p


def test_register_adds_sort_by():
    p = make_parser()
    args = p.parse_args(["--sort-by", "ts"])
    assert args.sort_by == ["ts"]


def test_register_sort_by_repeatable():
    p = make_parser()
    args = p.parse_args(["--sort-by", "level", "--sort-by", "ts"])
    assert args.sort_by == ["level", "ts"]


def test_register_sort_desc_default_false():
    p = make_parser()
    args = p.parse_args([])
    assert args.sort_desc is False


def test_register_sort_desc_flag():
    p = make_parser()
    args = p.parse_args(["--sort-desc"])
    assert args.sort_desc is True


def test_extract_sort_kwargs():
    p = make_parser()
    args = p.parse_args(["--sort-by", "ts", "--sort-desc"])
    kwargs = extract_sort_kwargs(args)
    assert kwargs == {"fields": ["ts"], "reverse": True}


def test_is_sort_active_true():
    p = make_parser()
    args = p.parse_args(["--sort-by", "ts"])
    assert is_sort_active(args) is True


def test_is_sort_active_false():
    p = make_parser()
    args = p.parse_args([])
    assert is_sort_active(args) is False
