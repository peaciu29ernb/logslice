"""Tests for logslice.compute and logslice.cli_compute."""

import argparse
import pytest

from logslice.compute import (
    _resolve,
    evaluate_expr,
    parse_compute_arg,
    compute_fields,
    compute_records,
)
from logslice.cli_compute import (
    register_compute_args,
    extract_compute_kwargs,
    is_compute_active,
    describe_compute,
    _parse_compute_list,
)


# ---------------------------------------------------------------------------
# parse_compute_arg
# ---------------------------------------------------------------------------

def test_parse_compute_arg_valid():
    assert parse_compute_arg("rate=bytes/duration") == ("rate", "bytes/duration")


def test_parse_compute_arg_spaces():
    assert parse_compute_arg(" total = count + extra ") == ("total", "count + extra")


def test_parse_compute_arg_no_equals_returns_none():
    assert parse_compute_arg("nodestination") is None


def test_parse_compute_arg_empty_dest_returns_none():
    assert parse_compute_arg("=expr") is None


# ---------------------------------------------------------------------------
# _resolve
# ---------------------------------------------------------------------------

def test_resolve_literal():
    assert _resolve("3.5", {}) == 3.5


def test_resolve_field_from_record():
    assert _resolve("count", {"count": "7"}) == 7.0


def test_resolve_missing_field_returns_none():
    assert _resolve("missing", {}) is None


def test_resolve_non_numeric_field_returns_none():
    assert _resolve("name", {"name": "alice"}) is None


# ---------------------------------------------------------------------------
# evaluate_expr
# ---------------------------------------------------------------------------

def test_evaluate_addition():
    assert evaluate_expr("a + b", {"a": 3, "b": 4}) == 7.0


def test_evaluate_subtraction():
    assert evaluate_expr("total - used", {"total": 100, "used": 40}) == 60.0


def test_evaluate_multiplication():
    assert evaluate_expr("price * qty", {"price": 2.5, "qty": 4}) == 10.0


def test_evaluate_division():
    assert evaluate_expr("bytes / 1024", {"bytes": 2048}) == 2.0


def test_evaluate_modulo():
    assert evaluate_expr("n % 3", {"n": 10}) == 1.0


def test_evaluate_division_by_zero_returns_none():
    assert evaluate_expr("a / b", {"a": 5, "b": 0}) is None


def test_evaluate_missing_operand_returns_none():
    assert evaluate_expr("a + missing", {"a": 1}) is None


def test_evaluate_bad_expr_returns_none():
    assert evaluate_expr("not_an_expression", {}) is None


# ---------------------------------------------------------------------------
# compute_fields
# ---------------------------------------------------------------------------

def test_compute_fields_adds_new_field():
    rec = {"bytes": 1024, "duration": 2, "_raw": "x"}
    result = compute_fields(rec, [("rate", "bytes / duration")])
    assert result["rate"] == 512
    assert result["_raw"] == "x"


def test_compute_fields_integer_result():
    result = compute_fields({"a": 6, "b": 2}, [("c", "a / b")])
    assert result["c"] == 3
    assert isinstance(result["c"], int)


def test_compute_fields_does_not_mutate_original():
    rec = {"a": 1, "b": 2}
    compute_fields(rec, [("c", "a + b")])
    assert "c" not in rec


def test_compute_fields_skips_unresolvable():
    result = compute_fields({"a": 1}, [("c", "a + missing")])
    assert "c" not in result


# ---------------------------------------------------------------------------
# compute_records
# ---------------------------------------------------------------------------

def test_compute_records_yields_all():
    records = [{"x": 2, "y": 3}, {"x": 10, "y": 5}]
    out = list(compute_records(records, [("z", "x * y")]))
    assert len(out) == 2
    assert out[0]["z"] == 6
    assert out[1]["z"] == 50


# ---------------------------------------------------------------------------
# CLI helpers
# ---------------------------------------------------------------------------

def make_parser():
    p = argparse.ArgumentParser()
    register_compute_args(p)
    return p


def test_register_adds_compute_flag():
    p = make_parser()
    args = p.parse_args(["--compute", "r=a/b"])
    assert args.compute == ["r=a/b"]


def test_register_compute_default_empty():
    p = make_parser()
    args = p.parse_args([])
    assert args.compute == []


def test_extract_compute_kwargs_parses():
    p = make_parser()
    args = p.parse_args(["--compute", "rate=bytes/duration"])
    kwargs = extract_compute_kwargs(args)
    assert kwargs["assignments"] == [("rate", "bytes/duration")]


def test_is_compute_active_true():
    p = make_parser()
    args = p.parse_args(["--compute", "c=a+b"])
    assert is_compute_active(args) is True


def test_is_compute_active_false():
    p = make_parser()
    args = p.parse_args([])
    assert is_compute_active(args) is False


def test_describe_compute_none_when_empty():
    assert describe_compute([]) is None


def test_describe_compute_formats_assignments():
    result = describe_compute([("rate", "bytes/dur"), ("total", "a+b")])
    assert "rate=bytes/dur" in result
    assert "total=a+b" in result
