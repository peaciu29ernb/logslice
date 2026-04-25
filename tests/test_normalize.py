"""Tests for logslice.normalize."""

import pytest
from logslice.normalize import (
    normalize_lowercase,
    normalize_strip,
    normalize_replace,
    normalize_field,
    normalize_record,
    normalize_records,
)


# ---------------------------------------------------------------------------
# normalize_lowercase
# ---------------------------------------------------------------------------

def test_lowercase_string():
    assert normalize_lowercase("Hello World") == "hello world"


def test_lowercase_non_string_passthrough():
    assert normalize_lowercase(42) == 42
    assert normalize_lowercase(None) is None


# ---------------------------------------------------------------------------
# normalize_strip
# ---------------------------------------------------------------------------

def test_strip_removes_whitespace():
    assert normalize_strip("  hello  ") == "hello"


def test_strip_non_string_passthrough():
    assert normalize_strip(3.14) == 3.14


# ---------------------------------------------------------------------------
# normalize_replace
# ---------------------------------------------------------------------------

def test_replace_substitutes_pattern():
    assert normalize_replace("foo-bar", r"-", "_") == "foo_bar"


def test_replace_invalid_pattern_returns_original():
    assert normalize_replace("hello", r"[", "x") == "hello"


def test_replace_non_string_passthrough():
    assert normalize_replace(99, r"\d", "x") == 99


# ---------------------------------------------------------------------------
# normalize_field
# ---------------------------------------------------------------------------

def test_normalize_field_strip_and_lower():
    result = normalize_field("  FOO  ", lowercase=True, strip=True)
    assert result == "foo"


def test_normalize_field_with_replacements():
    result = normalize_field("user@example.com", replacements=[(r"@.*", "")])
    assert result == "user"


def test_normalize_field_no_ops_unchanged():
    assert normalize_field("Hello") == "Hello"


# ---------------------------------------------------------------------------
# normalize_record
# ---------------------------------------------------------------------------

def test_normalize_record_specific_fields():
    rec = {"level": "  ERROR  ", "msg": "  Hello  ", "_raw": "original"}
    result = normalize_record(rec, fields=["level"], strip=True)
    assert result["level"] == "ERROR"
    assert result["msg"] == "  Hello  "  # untouched
    assert result["_raw"] == "original"  # always untouched


def test_normalize_record_all_fields_excludes_raw():
    rec = {"a": "  X  ", "b": "  Y  ", "_raw": "keep"}
    result = normalize_record(rec, strip=True)
    assert result["a"] == "X"
    assert result["b"] == "Y"
    assert result["_raw"] == "keep"


def test_normalize_record_does_not_mutate_original():
    rec = {"level": "INFO"}
    normalize_record(rec, lowercase=True)
    assert rec["level"] == "INFO"


def test_normalize_record_lowercase_all():
    rec = {"level": "WARN", "env": "PROD"}
    result = normalize_record(rec, lowercase=True)
    assert result["level"] == "warn"
    assert result["env"] == "prod"


# ---------------------------------------------------------------------------
# normalize_records
# ---------------------------------------------------------------------------

def test_normalize_records_yields_all():
    recs = [{"msg": "  HI  "}, {"msg": "  BYE  "}]
    result = list(normalize_records(recs, strip=True))
    assert result[0]["msg"] == "HI"
    assert result[1]["msg"] == "BYE"


def test_normalize_records_empty():
    assert list(normalize_records([])) == []
