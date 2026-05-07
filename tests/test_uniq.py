"""Tests for logslice.uniq."""

import pytest
from logslice.uniq import _make_key, uniq_records


def rec(**kw):
    return dict(_raw="raw", **kw)


# --- _make_key ---

def test_make_key_single_field():
    assert _make_key({"level": "info", "msg": "hi"}, ["level"]) == ("info",)


def test_make_key_multiple_fields():
    r = {"level": "error", "svc": "api"}
    assert _make_key(r, ["level", "svc"]) == ("error", "api")


def test_make_key_missing_field_is_none():
    assert _make_key({"level": "warn"}, ["level", "svc"]) == ("warn", None)


# --- uniq_records ---

def test_uniq_removes_consecutive_duplicates():
    records = [
        rec(level="info"),
        rec(level="info"),
        rec(level="error"),
    ]
    result = list(uniq_records(records, fields=["level"]))
    assert len(result) == 2
    assert result[0]["level"] == "info"
    assert result[1]["level"] == "error"


def test_uniq_keeps_non_consecutive_duplicates():
    records = [
        rec(level="info"),
        rec(level="error"),
        rec(level="info"),
    ]
    result = list(uniq_records(records, fields=["level"]))
    assert len(result) == 3


def test_uniq_empty_input():
    assert list(uniq_records([], fields=["level"])) == []


def test_uniq_single_record():
    records = [rec(level="debug")]
    result = list(uniq_records(records, fields=["level"]))
    assert len(result) == 1


def test_uniq_all_same():
    records = [rec(level="info")] * 5
    result = list(uniq_records(records, fields=["level"]))
    assert len(result) == 1


def test_uniq_preserves_raw():
    records = [rec(level="info"), rec(level="error")]
    result = list(uniq_records(records, fields=["level"]))
    assert all("_raw" in r for r in result)


def test_uniq_count_adds_field():
    records = [
        rec(level="info"),
        rec(level="info"),
        rec(level="info"),
        rec(level="error"),
    ]
    result = list(uniq_records(records, fields=["level"], count=True))
    assert result[0]["_count"] == 3
    assert result[1]["_count"] == 1


def test_uniq_count_custom_field():
    records = [rec(level="warn"), rec(level="warn")]
    result = list(uniq_records(records, fields=["level"], count=True, count_field="n"))
    assert result[0]["n"] == 2
    assert "_count" not in result[0]


def test_uniq_no_count_no_extra_field():
    records = [rec(level="info"), rec(level="info")]
    result = list(uniq_records(records, fields=["level"], count=False))
    assert "_count" not in result[0]


def test_uniq_multi_field_key():
    records = [
        rec(level="info", svc="api"),
        rec(level="info", svc="api"),
        rec(level="info", svc="web"),
    ]
    result = list(uniq_records(records, fields=["level", "svc"]))
    assert len(result) == 2
    assert result[1]["svc"] == "web"
