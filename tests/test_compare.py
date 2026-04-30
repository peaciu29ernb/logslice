"""Tests for logslice.compare."""

import pytest
from logslice.compare import compare_records, format_compare_table


def rec(id_, **kw):
    return {"id": id_, **kw}


# ---------------------------------------------------------------------------
# compare_records
# ---------------------------------------------------------------------------

def test_no_differences_yields_nothing():
    left = [rec("a", level="info"), rec("b", level="warn")]
    right = [rec("a", level="info"), rec("b", level="warn")]
    rows = list(compare_records(left, right, key_field="id"))
    assert rows == []


def test_detects_field_change():
    left = [rec("a", level="info")]
    right = [rec("a", level="error")]
    rows = list(compare_records(left, right, key_field="id"))
    assert len(rows) == 1
    assert rows[0]["field"] == "level"
    assert rows[0]["left"] == "info"
    assert rows[0]["right"] == "error"


def test_missing_in_right():
    left = [rec("a", level="info"), rec("b", level="warn")]
    right = [rec("a", level="info")]
    rows = list(compare_records(left, right, key_field="id"))
    assert any(r["id"] == "b" and "missing in right" in r.get("value", "") for r in rows)


def test_missing_in_left():
    left = [rec("a", level="info")]
    right = [rec("a", level="info"), rec("z", level="debug")]
    rows = list(compare_records(left, right, key_field="id"))
    assert any(r["id"] == "z" and "missing in left" in r.get("value", "") for r in rows)


def test_restrict_to_fields():
    left = [rec("a", level="info", msg="hello")]
    right = [rec("a", level="error", msg="world")]
    rows = list(compare_records(left, right, key_field="id", fields=["msg"]))
    assert len(rows) == 1
    assert rows[0]["field"] == "msg"


def test_custom_labels():
    left = [rec("a", level="info")]
    right = [rec("a", level="debug")]
    rows = list(compare_records(left, right, key_field="id", label_left="before", label_right="after"))
    assert "before" in rows[0]
    assert "after" in rows[0]


def test_raw_field_ignored():
    left = [{"id": "a", "level": "info", "_raw": "raw1"}]
    right = [{"id": "a", "level": "info", "_raw": "raw2"}]
    rows = list(compare_records(left, right, key_field="id"))
    assert rows == []


def test_missing_key_field_skipped():
    left = [{"level": "info"}]  # no 'id'
    right = [rec("a", level="info")]
    rows = list(compare_records(left, right, key_field="id"))
    # left record has no key, so 'a' is only in right -> missing in left
    assert any("missing in left" in r.get("value", "") for r in rows)


# ---------------------------------------------------------------------------
# format_compare_table
# ---------------------------------------------------------------------------

def test_format_empty_returns_no_differences():
    assert format_compare_table([]) == "(no differences)"


def test_format_table_contains_headers():
    rows = [{"id": "a", "field": "level", "left": "info", "right": "error"}]
    table = format_compare_table(rows)
    assert "LEFT" in table
    assert "RIGHT" in table
    assert "FIELD" in table


def test_format_table_contains_values():
    rows = [{"id": "a", "field": "level", "left": "info", "right": "error"}]
    table = format_compare_table(rows)
    assert "info" in table
    assert "error" in table
