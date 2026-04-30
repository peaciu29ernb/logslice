"""Tests for logslice.distinct."""

import pytest
from logslice.distinct import _make_key, distinct_records, count_distinct


# ---------------------------------------------------------------------------
# helpers
# ---------------------------------------------------------------------------

def make_rec(**kwargs):
    return {"__raw__": "", **kwargs}


# ---------------------------------------------------------------------------
# _make_key
# ---------------------------------------------------------------------------

def test_make_key_single_field():
    rec = make_rec(level="info")
    assert _make_key(rec, ["level"]) == ("info",)


def test_make_key_multiple_fields():
    rec = make_rec(level="warn", host="web1")
    assert _make_key(rec, ["level", "host"]) == ("warn", "web1")


def test_make_key_missing_field_is_none():
    rec = make_rec(level="error")
    assert _make_key(rec, ["level", "host"]) == ("error", None)


# ---------------------------------------------------------------------------
# distinct_records — keep="first" (default)
# ---------------------------------------------------------------------------

def test_distinct_first_removes_duplicates():
    records = [
        make_rec(level="info"),
        make_rec(level="info"),
        make_rec(level="error"),
    ]
    result = list(distinct_records(records, ["level"]))
    assert len(result) == 2
    assert result[0]["level"] == "info"
    assert result[1]["level"] == "error"


def test_distinct_first_preserves_order():
    records = [
        make_rec(level="debug"),
        make_rec(level="info"),
        make_rec(level="debug"),
        make_rec(level="warn"),
    ]
    levels = [r["level"] for r in distinct_records(records, ["level"])]
    assert levels == ["debug", "info", "warn"]


def test_distinct_no_fields_yields_all():
    records = [make_rec(level="info")] * 5
    assert len(list(distinct_records(records, []))) == 5


def test_distinct_empty_input():
    assert list(distinct_records([], ["level"])) == []


def test_distinct_multi_field_key():
    records = [
        make_rec(level="info", host="a"),
        make_rec(level="info", host="b"),
        make_rec(level="info", host="a"),
    ]
    result = list(distinct_records(records, ["level", "host"]))
    assert len(result) == 2


# ---------------------------------------------------------------------------
# distinct_records — keep="last"
# ---------------------------------------------------------------------------

def test_distinct_last_keeps_final_occurrence():
    records = [
        make_rec(level="info", msg="first"),
        make_rec(level="info", msg="second"),
        make_rec(level="error", msg="only"),
    ]
    result = list(distinct_records(records, ["level"], keep="last"))
    assert len(result) == 2
    by_level = {r["level"]: r for r in result}
    assert by_level["info"]["msg"] == "second"
    assert by_level["error"]["msg"] == "only"


def test_distinct_last_preserves_insertion_order():
    records = [
        make_rec(level="info", msg="v1"),
        make_rec(level="warn", msg="w1"),
        make_rec(level="info", msg="v2"),
    ]
    levels = [r["level"] for r in distinct_records(records, ["level"], keep="last")]
    assert levels == ["info", "warn"]


def test_distinct_invalid_keep_raises():
    with pytest.raises(ValueError, match="keep must be"):
        list(distinct_records([make_rec(level="info")], ["level"], keep="middle"))


# ---------------------------------------------------------------------------
# count_distinct
# ---------------------------------------------------------------------------

def test_count_distinct_basic():
    records = [
        make_rec(level="info"),
        make_rec(level="info"),
        make_rec(level="error"),
    ]
    assert count_distinct(records, ["level"]) == 2


def test_count_distinct_empty():
    assert count_distinct([], ["level"]) == 0


def test_count_distinct_all_unique():
    records = [make_rec(level=str(i)) for i in range(10)]
    assert count_distinct(records, ["level"]) == 10
