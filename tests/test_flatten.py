"""Tests for logslice.flatten."""

import pytest
from logslice.flatten import flatten_dict, flatten_record, flatten_records


# ---------------------------------------------------------------------------
# flatten_dict
# ---------------------------------------------------------------------------

def test_flatten_dict_simple():
    data = {"a": 1, "b": 2}
    assert flatten_dict(data) == {"a": 1, "b": 2}


def test_flatten_dict_nested_one_level():
    data = {"a": {"b": 1, "c": 2}}
    assert flatten_dict(data) == {"a.b": 1, "a.c": 2}


def test_flatten_dict_nested_two_levels():
    data = {"a": {"b": {"c": 42}}}
    assert flatten_dict(data) == {"a.b.c": 42}


def test_flatten_dict_custom_separator():
    data = {"a": {"b": 1}}
    assert flatten_dict(data, separator="_") == {"a_b": 1}


def test_flatten_dict_max_depth_zero():
    """max_depth=0 means no flattening at all."""
    data = {"a": {"b": 1}}
    result = flatten_dict(data, max_depth=0)
    assert result == {"a": {"b": 1}}


def test_flatten_dict_max_depth_one():
    data = {"a": {"b": {"c": 99}}}
    result = flatten_dict(data, max_depth=1)
    # Flattens one level: a.b -> {"c": 99} kept as dict
    assert result == {"a.b": {"c": 99}}


def test_flatten_dict_empty_nested_dict_kept():
    """An empty nested dict is not recursed into."""
    data = {"a": {}}
    assert flatten_dict(data) == {"a": {}}


def test_flatten_dict_non_dict_values_unchanged():
    data = {"a": [1, 2, 3], "b": None, "c": True}
    assert flatten_dict(data) == {"a": [1, 2, 3], "b": None, "c": True}


# ---------------------------------------------------------------------------
# flatten_record
# ---------------------------------------------------------------------------

def test_flatten_record_preserves_raw():
    record = {"_raw": "original line", "meta": {"host": "web1"}}
    result = flatten_record(record)
    assert result["_raw"] == "original line"
    assert result["meta.host"] == "web1"
    assert "meta" not in result


def test_flatten_record_no_raw_key():
    record = {"level": "info", "ctx": {"user": "alice"}}
    result = flatten_record(record)
    assert "_raw" not in result
    assert result["ctx.user"] == "alice"


def test_flatten_record_does_not_mutate_original():
    record = {"a": {"b": 1}, "_raw": "raw"}
    original_copy = {"a": {"b": 1}, "_raw": "raw"}
    flatten_record(record)
    assert record == original_copy


# ---------------------------------------------------------------------------
# flatten_records
# ---------------------------------------------------------------------------

def test_flatten_records_yields_all():
    records = [
        {"_raw": "l1", "data": {"x": 1}},
        {"_raw": "l2", "data": {"x": 2}},
    ]
    results = list(flatten_records(iter(records)))
    assert len(results) == 2
    assert results[0]["data.x"] == 1
    assert results[1]["data.x"] == 2


def test_flatten_records_empty_input():
    assert list(flatten_records(iter([]))) == []


def test_flatten_records_custom_separator():
    records = [{"a": {"b": 7}}]
    results = list(flatten_records(iter(records), separator="/"))
    assert results[0]["a/b"] == 7
