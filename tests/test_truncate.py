"""Tests for logslice.truncate."""

import pytest
from logslice.truncate import (
    truncate_value,
    truncate_fields,
    truncate_records,
    DEFAULT_MAX_LENGTH,
    DEFAULT_SUFFIX,
)


# --- truncate_value ---

def test_truncate_value_short_string_unchanged():
    assert truncate_value("hello", 10) == "hello"


def test_truncate_value_exact_length_unchanged():
    assert truncate_value("hello", 5) == "hello"


def test_truncate_value_long_string_truncated():
    result = truncate_value("abcdefghij", 7)
    assert result == "abcd..."
    assert len(result) == 7


def test_truncate_value_custom_suffix():
    result = truncate_value("abcdefghij", 6, suffix="!")
    assert result == "abcde!"


def test_truncate_value_non_string_passthrough():
    assert truncate_value(42, 5) == 42
    assert truncate_value(None, 5) is None


def test_truncate_value_very_short_max():
    result = truncate_value("hello world", 3)
    assert result == "..."


def test_truncate_value_max_shorter_than_suffix():
    result = truncate_value("hello world", 1, suffix="...")
    assert result == "..."
    assert len(result) == 3


# --- truncate_fields ---

def test_truncate_fields_all_string_fields():
    record = {"msg": "a" * 300, "level": "info", "_raw": "original"}
    result = truncate_fields(record, fields=None, max_length=10)
    assert len(result["msg"]) == 10
    assert result["msg"].endswith(DEFAULT_SUFFIX)
    assert result["level"] == "info"
    assert result["_raw"] == "original"


def test_truncate_fields_specific_fields_only():
    record = {"msg": "a" * 300, "detail": "b" * 300}
    result = truncate_fields(record, fields=["msg"], max_length=20)
    assert len(result["msg"]) == 20
    assert len(result["detail"]) == 300


def test_truncate_fields_does_not_mutate_original():
    original = {"msg": "a" * 300}
    truncate_fields(original, fields=None, max_length=10)
    assert len(original["msg"]) == 300


def test_truncate_fields_preserves_raw():
    record = {"_raw": "x" * 500, "msg": "short"}
    result = truncate_fields(record, fields=None, max_length=10)
    assert result["_raw"] == "x" * 500


def test_truncate_fields_no_change_when_short():
    record = {"msg": "hello", "code": "ok"}
    result = truncate_fields(record, fields=None, max_length=100)
    assert result == record


# --- truncate_records ---

def test_truncate_records_yields_all():
    records = [
        {"msg": "a" * 50},
        {"msg": "b" * 50},
    ]
    results = list(truncate_records(records, max_length=20))
    assert len(results) == 2
    for r in results:
        assert len(r["msg"]) == 20


def test_truncate_records_empty():
    assert list(truncate_records([])) == []


def test_truncate_records_default_max_length():
    record = {"msg": "x" * (DEFAULT_MAX_LENGTH + 50)}
    result = list(truncate_records([record]))[0]
    assert len(result["msg"]) == DEFAULT_MAX_LENGTH
