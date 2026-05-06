"""Tests for logslice.clamp and logslice.cli_clamp."""

import argparse
import pytest

from logslice.clamp import _to_float, clamp_value, clamp_record, clamp_records
from logslice.cli_clamp import (
    register_clamp_args,
    is_clamp_active,
    validate_clamp_args,
    extract_clamp_kwargs,
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
# clamp_value
# ---------------------------------------------------------------------------

def test_clamp_value_below_min():
    assert clamp_value(-5, lo=0.0, hi=10.0) == 0

def test_clamp_value_above_max():
    assert clamp_value(20, lo=0.0, hi=10.0) == 10

def test_clamp_value_within_range():
    assert clamp_value(5, lo=0.0, hi=10.0) == 5

def test_clamp_value_no_bounds():
    assert clamp_value(999, lo=None, hi=None) == 999

def test_clamp_value_non_numeric_passthrough():
    assert clamp_value("hello", lo=0.0, hi=10.0) == "hello"

def test_clamp_value_preserves_int_type():
    result = clamp_value(-3, lo=0.0, hi=100.0)
    assert isinstance(result, int)
    assert result == 0


# ---------------------------------------------------------------------------
# clamp_record
# ---------------------------------------------------------------------------

def test_clamp_record_clamps_named_field():
    rec = {"latency": 200, "status": "ok", "_raw": "..."}    
    out = clamp_record(rec, ["latency"], lo=None, hi=100.0)
    assert out["latency"] == 100

def test_clamp_record_ignores_raw():
    rec = {"_raw": "original"}
    out = clamp_record(rec, ["_raw"], lo=0.0, hi=10.0)
    assert out["_raw"] == "original"

def test_clamp_record_does_not_mutate():
    rec = {"val": 50}
    clamp_record(rec, ["val"], lo=0.0, hi=10.0)
    assert rec["val"] == 50

def test_clamp_record_unknown_field_unchanged():
    rec = {"a": 5}
    out = clamp_record(rec, ["b"], lo=0.0, hi=3.0)
    assert out == {"a": 5}


# ---------------------------------------------------------------------------
# clamp_records
# ---------------------------------------------------------------------------

def test_clamp_records_yields_all():
    recs = [{"x": i} for i in range(5)]
    out = list(clamp_records(recs, ["x"], lo=1.0, hi=3.0))
    assert len(out) == 5
    assert out[0]["x"] == 1
    assert out[4]["x"] == 3

def test_clamp_records_empty_input():
    assert list(clamp_records([], ["x"], lo=0.0, hi=1.0)) == []


# ---------------------------------------------------------------------------
# CLI helpers
# ---------------------------------------------------------------------------

def make_parser():
    p = argparse.ArgumentParser()
    register_clamp_args(p)
    return p

def test_register_adds_clamp_field():
    p = make_parser()
    args = p.parse_args(["--clamp-field", "latency"])
    assert args.clamp_fields == ["latency"]

def test_register_repeatable():
    p = make_parser()
    args = p.parse_args(["--clamp-field", "a", "--clamp-field", "b"])
    assert args.clamp_fields == ["a", "b"]

def test_is_clamp_active_true():
    p = make_parser()
    args = p.parse_args(["--clamp-field", "x", "--clamp-min", "0"])
    assert is_clamp_active(args) is True

def test_is_clamp_active_false():
    p = make_parser()
    args = p.parse_args([])
    assert is_clamp_active(args) is False

def test_validate_min_gt_max_returns_error():
    p = make_parser()
    args = p.parse_args(["--clamp-field", "x", "--clamp-min", "10", "--clamp-max", "5"])
    assert validate_clamp_args(args) is not None

def test_validate_no_bounds_returns_error():
    p = make_parser()
    args = p.parse_args(["--clamp-field", "x"])
    assert validate_clamp_args(args) is not None

def test_validate_valid_args_returns_none():
    p = make_parser()
    args = p.parse_args(["--clamp-field", "x", "--clamp-max", "100"])
    assert validate_clamp_args(args) is None

def test_extract_clamp_kwargs():
    p = make_parser()
    args = p.parse_args(["--clamp-field", "latency", "--clamp-min", "0", "--clamp-max", "500"])
    kwargs = extract_clamp_kwargs(args)
    assert kwargs["fields"] == ["latency"]
    assert kwargs["lo"] == 0.0
    assert kwargs["hi"] == 500.0
