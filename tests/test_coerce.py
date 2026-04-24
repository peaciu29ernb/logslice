"""Tests for logslice.coerce."""

import pytest
from logslice.coerce import (
    coerce_int,
    coerce_float,
    coerce_bool,
    coerce_field,
    coerce_record,
    coerce_records,
)


def test_coerce_int_numeric_string():
    assert coerce_int("42") == 42


def test_coerce_int_already_int():
    assert coerce_int(7) == 7


def test_coerce_int_invalid_returns_none():
    assert coerce_int("abc") is None


def test_coerce_int_none_returns_none():
    assert coerce_int(None) is None


def test_coerce_float_numeric_string():
    assert coerce_float("3.14") == pytest.approx(3.14)


def test_coerce_float_invalid_returns_none():
    assert coerce_float("nope") is None


def test_coerce_bool_true_variants():
    for val in ("true", "True", "1", "yes", "on"):
        assert coerce_bool(val) is True, f"Expected True for {val!r}"


def test_coerce_bool_false_variants():
    for val in ("false", "False", "0", "no", "off"):
        assert coerce_bool(val) is False, f"Expected False for {val!r}"


def test_coerce_bool_already_bool():
    assert coerce_bool(True) is True
    assert coerce_bool(False) is False


def test_coerce_bool_unknown_returns_none():
    assert coerce_bool("maybe") is None


def test_coerce_field_int_success():
    assert coerce_field("10", "int") == 10


def test_coerce_field_int_failure_returns_original():
    assert coerce_field("bad", "int") == "bad"


def test_coerce_field_str_converts():
    assert coerce_field(99, "str") == "99"


def test_coerce_field_unknown_type_passthrough():
    assert coerce_field("hello", "uuid") == "hello"


def test_coerce_record_applies_coercions():
    record = {"count": "5", "ratio": "0.9", "_raw": "count=5 ratio=0.9"}
    result = coerce_record(record, [("count", "int"), ("ratio", "float")])
    assert result["count"] == 5
    assert result["ratio"] == pytest.approx(0.9)
    assert result["_raw"] == "count=5 ratio=0.9"


def test_coerce_record_does_not_mutate_original():
    record = {"count": "3"}
    coerce_record(record, [("count", "int")])
    assert record["count"] == "3"


def test_coerce_record_skips_missing_field():
    record = {"level": "info"}
    result = coerce_record(record, [("count", "int")])
    assert "count" not in result


def test_coerce_record_skips_raw_key():
    record = {"_raw": "42"}
    result = coerce_record(record, [("_raw", "int")])
    assert result["_raw"] == "42"


def test_coerce_records_yields_all():
    records = [
        {"n": "1", "_raw": "n=1"},
        {"n": "2", "_raw": "n=2"},
    ]
    results = list(coerce_records(records, [("n", "int")]))
    assert len(results) == 2
    assert results[0]["n"] == 1
    assert results[1]["n"] == 2
