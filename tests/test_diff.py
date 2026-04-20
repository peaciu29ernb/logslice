"""Tests for logslice.diff module."""

import pytest
from logslice.diff import index_records, diff_records, format_diff_table


def make_rec(key_val, **fields):
    rec = {"id": key_val, **fields}
    return rec


LEFT = [
    make_rec("a", level="info", msg="hello"),
    make_rec("b", level="warn", msg="world"),
    make_rec("c", level="error", msg="boom"),
]

RIGHT = [
    make_rec("a", level="info", msg="hello"),
    make_rec("b", level="error", msg="world"),  # level changed
    make_rec("d", level="debug", msg="new"),    # added
]


def test_index_records_basic():
    idx = index_records(LEFT, "id")
    assert set(idx.keys()) == {"a", "b", "c"}
    assert idx["a"]["msg"] == "hello"


def test_index_records_missing_key_skipped():
    records = [{"id": "x"}, {"no_id": "y"}]
    idx = index_records(records, "id")
    assert "x" in idx
    assert len(idx) == 1


def test_diff_detects_added():
    entries = list(diff_records(LEFT, RIGHT, key="id"))
    added = [e for e in entries if e["status"] == "added"]
    assert len(added) == 1
    assert added[0]["key"] == "d"
    assert added[0]["left"] is None
    assert added[0]["right"]["msg"] == "new"


def test_diff_detects_removed():
    entries = list(diff_records(LEFT, RIGHT, key="id"))
    removed = [e for e in entries if e["status"] == "removed"]
    assert len(removed) == 1
    assert removed[0]["key"] == "c"
    assert removed[0]["right"] is None


def test_diff_detects_changed():
    entries = list(diff_records(LEFT, RIGHT, key="id"))
    changed = [e for e in entries if e["status"] == "changed"]
    assert len(changed) == 1
    assert changed[0]["key"] == "b"
    assert "level" in changed[0]["changed_fields"]


def test_diff_detects_unchanged():
    entries = list(diff_records(LEFT, RIGHT, key="id"))
    unchanged = [e for e in entries if e["status"] == "unchanged"]
    assert len(unchanged) == 1
    assert unchanged[0]["key"] == "a"


def test_diff_ignore_fields():
    left = [make_rec("x", level="info", ts="2024-01-01")]
    right = [make_rec("x", level="info", ts="2024-06-01")]
    entries = list(diff_records(left, right, key="id", ignore_fields=["ts"]))
    assert entries[0]["status"] == "unchanged"


def test_diff_ignore_raw_always():
    left = [{"id": "x", "msg": "hi", "_raw": "raw1"}]
    right = [{"id": "x", "msg": "hi", "_raw": "raw2"}]
    entries = list(diff_records(left, right, key="id"))
    assert entries[0]["status"] == "unchanged"


def test_diff_empty_inputs():
    assert list(diff_records([], [], key="id")) == []


def test_diff_left_only():
    entries = list(diff_records(LEFT, [], key="id"))
    assert all(e["status"] == "removed" for e in entries)


def test_diff_right_only():
    entries = list(diff_records([], RIGHT, key="id"))
    assert all(e["status"] == "added" for e in entries)


def test_format_diff_table_symbols():
    entries = list(diff_records(LEFT, RIGHT, key="id"))
    table = format_diff_table(entries)
    lines = table.splitlines()
    assert any(line.startswith("+") for line in lines)
    assert any(line.startswith("-") for line in lines)
    assert any(line.startswith("~") for line in lines)
    assert any(line.startswith(" ") for line in lines)


def test_format_diff_table_changed_shows_fields():
    entries = list(diff_records(LEFT, RIGHT, key="id"))
    table = format_diff_table(entries)
    assert "level" in table
