"""Tests for logslice.aggregate."""
from collections import Counter
from logslice.aggregate import group_by, count_by, format_count_table


RECORDS = [
    {"level": "info", "msg": "a"},
    {"level": "info", "msg": "b"},
    {"level": "warn", "msg": "c"},
    {"level": "error", "msg": "d"},
]


def test_group_by_keys():
    groups = group_by(RECORDS, "level")
    assert set(groups.keys()) == {"info", "warn", "error"}


def test_group_by_counts():
    groups = group_by(RECORDS, "level")
    assert len(groups["info"]) == 2
    assert len(groups["warn"]) == 1


def test_group_by_missing_field():
    records = [{"msg": "hello"}, {"level": "info", "msg": "world"}]
    groups = group_by(records, "level")
    assert "<missing>" in groups
    assert len(groups["<missing>"]) == 1


def test_count_by_returns_counter():
    counter = count_by(RECORDS, "level")
    assert isinstance(counter, Counter)
    assert counter["info"] == 2
    assert counter["warn"] == 1
    assert counter["error"] == 1


def test_count_by_missing():
    records = [{"msg": "x"}]
    counter = count_by(records, "level")
    assert counter["<missing>"] == 1


def test_format_count_table_basic():
    counter = Counter({"info": 5, "warn": 2})
    table = format_count_table(counter)
    assert "info" in table
    assert "5" in table
    assert "warn" in table


def test_format_count_table_with_title():
    counter = Counter({"error": 3})
    table = format_count_table(counter, title="level")
    assert table.startswith("level")
    assert "---" in table


def test_format_count_table_empty():
    table = format_count_table(Counter())
    assert table == ""
