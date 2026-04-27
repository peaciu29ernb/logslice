"""Tests for logslice/cast.py and logslice/cli_cast.py."""

import argparse
import pytest

from logslice.cast import _cast_value, cast_fields, cast_records, parse_cast_args
from logslice.cli_cast import (
    extract_cast_kwargs,
    is_cast_active,
    register_cast_args,
)


# ---------------------------------------------------------------------------
# _cast_value
# ---------------------------------------------------------------------------

def test_cast_to_int_from_string():
    assert _cast_value("42", "int") == 42


def test_cast_to_int_from_float_string():
    assert _cast_value("3.9", "int") == 3


def test_cast_to_float():
    assert _cast_value("1.5", "float") == 1.5


def test_cast_to_str():
    assert _cast_value(99, "str") == "99"


def test_cast_bool_true_string():
    assert _cast_value("yes", "bool") is True


def test_cast_bool_false_string():
    assert _cast_value("false", "bool") is False


def test_cast_bool_zero_string():
    assert _cast_value("0", "bool") is False


def test_cast_bool_already_bool():
    assert _cast_value(True, "bool") is True


def test_cast_invalid_returns_original():
    assert _cast_value("abc", "int") == "abc"


def test_cast_unknown_type_returns_original():
    assert _cast_value("hello", "bytes") == "hello"


# ---------------------------------------------------------------------------
# cast_fields
# ---------------------------------------------------------------------------

def test_cast_fields_basic():
    rec = {"count": "5", "name": "alice", "_raw": "count=5 name=alice"}
    result = cast_fields(rec, {"count": "int"})
    assert result["count"] == 5
    assert result["name"] == "alice"


def test_cast_fields_preserves_raw():
    rec = {"x": "1", "_raw": "original"}
    result = cast_fields(rec, {"_raw": "int", "x": "int"})
    assert result["_raw"] == "original"
    assert result["x"] == 1


def test_cast_fields_unknown_field_unchanged():
    rec = {"a": "1"}
    result = cast_fields(rec, {"z": "int"})
    assert result == {"a": "1"}


def test_cast_fields_does_not_mutate_original():
    rec = {"n": "7"}
    cast_fields(rec, {"n": "int"})
    assert rec["n"] == "7"


# ---------------------------------------------------------------------------
# cast_records
# ---------------------------------------------------------------------------

def test_cast_records_yields_all():
    recs = [{"v": "1"}, {"v": "2"}, {"v": "3"}]
    result = list(cast_records(recs, {"v": "int"}))
    assert [r["v"] for r in result] == [1, 2, 3]


# ---------------------------------------------------------------------------
# parse_cast_args
# ---------------------------------------------------------------------------

def test_parse_cast_args_basic():
    assert parse_cast_args(["count:int", "ratio:float"]) == {
        "count": "int",
        "ratio": "float",
    }


def test_parse_cast_args_bad_format_raises():
    with pytest.raises(ValueError, match="Invalid cast spec"):
        parse_cast_args(["nodivider"])


def test_parse_cast_args_unsupported_type_raises():
    with pytest.raises(ValueError, match="Unsupported cast type"):
        parse_cast_args(["field:bytes"])


def test_parse_cast_args_empty_field_raises():
    with pytest.raises(ValueError, match="Empty field name"):
        parse_cast_args([":int"])


# ---------------------------------------------------------------------------
# CLI helpers
# ---------------------------------------------------------------------------

def make_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser()
    register_cast_args(p)
    return p


def test_register_adds_cast_flag():
    p = make_parser()
    args = p.parse_args(["--cast", "score:float"])
    assert args.cast == ["score:float"]


def test_extract_cast_kwargs_empty():
    p = make_parser()
    args = p.parse_args([])
    assert extract_cast_kwargs(args) == {}


def test_extract_cast_kwargs_populated():
    p = make_parser()
    args = p.parse_args(["--cast", "n:int"])
    result = extract_cast_kwargs(args)
    assert result == {"casts": {"n": "int"}}


def test_is_cast_active_false():
    p = make_parser()
    args = p.parse_args([])
    assert is_cast_active(args) is False


def test_is_cast_active_true():
    p = make_parser()
    args = p.parse_args(["--cast", "x:str"])
    assert is_cast_active(args) is True
