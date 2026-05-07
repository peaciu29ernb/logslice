"""Tests for logslice.fill."""

import pytest
from logslice.fill import fill_with_default, fill_forward, fill_records


# ---------------------------------------------------------------------------
# fill_with_default
# ---------------------------------------------------------------------------

def test_fill_with_default_missing_field():
    rec = {"a": 1}
    result = fill_with_default(rec, ["b"], default="x")
    assert result["b"] == "x"


def test_fill_with_default_present_field_unchanged():
    rec = {"a": 1, "b": 2}
    result = fill_with_default(rec, ["b"], default="x")
    assert result["b"] == 2


def test_fill_with_default_none_value_replaced():
    rec = {"a": None}
    result = fill_with_default(rec, ["a"], default=0)
    assert result["a"] == 0


def test_fill_with_default_does_not_mutate_original():
    rec = {"a": 1}
    fill_with_default(rec, ["b"], default=99)
    assert "b" not in rec


def test_fill_with_default_multiple_fields():
    rec = {"a": 1}
    result = fill_with_default(rec, ["b", "c"], default="z")
    assert result["b"] == "z"
    assert result["c"] == "z"


# ---------------------------------------------------------------------------
# fill_forward
# ---------------------------------------------------------------------------

def test_fill_forward_carries_previous_value():
    carry = {"status": "ok"}
    rec = {"msg": "hello"}
    result = fill_forward(rec, ["status"], carry)
    assert result["status"] == "ok"


def test_fill_forward_updates_carry_when_value_present():
    carry = {}
    rec = {"status": "error"}
    fill_forward(rec, ["status"], carry)
    assert carry["status"] == "error"


def test_fill_forward_no_carry_no_value_leaves_field_absent():
    carry = {}
    rec = {"msg": "hi"}
    result = fill_forward(rec, ["status"], carry)
    assert "status" not in result


def test_fill_forward_does_not_mutate_original():
    carry = {}
    rec = {"a": 1}
    fill_forward(rec, ["a"], carry)
    assert rec == {"a": 1}


# ---------------------------------------------------------------------------
# fill_records
# ---------------------------------------------------------------------------

def test_fill_records_default_strategy():
    records = [{"a": 1}, {"a": None}, {"b": 2}]
    result = list(fill_records(records, fields=["a"], default=0))
    assert result[0]["a"] == 1
    assert result[1]["a"] == 0
    assert result[2]["a"] == 0


def test_fill_records_forward_strategy():
    records = [{"v": 10}, {"v": None}, {"v": None}]
    result = list(fill_records(records, fields=["v"], forward=True))
    assert result[0]["v"] == 10
    assert result[1]["v"] == 10
    assert result[2]["v"] == 10


def test_fill_records_forward_no_prior_value():
    records = [{"v": None}, {"v": 5}]
    result = list(fill_records(records, fields=["v"], forward=True))
    assert result[0]["v"] is None
    assert result[1]["v"] == 5


def test_fill_records_empty_input():
    result = list(fill_records([], fields=["a"]))
    assert result == []
