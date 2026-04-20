"""Tests for logslice.validate."""

import pytest
from logslice.validate import (
    check_required_fields,
    check_field_pattern,
    validate_record,
    filter_valid_records,
)


def make_record(**kwargs):
    return dict(kwargs)


# --- check_required_fields ---

def test_required_fields_all_present():
    rec = make_record(level="info", msg="hello")
    assert check_required_fields(rec, ["level", "msg"]) == []


def test_required_fields_some_missing():
    rec = make_record(level="info")
    missing = check_required_fields(rec, ["level", "msg", "ts"])
    assert set(missing) == {"msg", "ts"}


def test_required_fields_empty_list():
    rec = make_record(level="info")
    assert check_required_fields(rec, []) == []


# --- check_field_pattern ---

def test_field_pattern_matches():
    rec = make_record(level="error")
    assert check_field_pattern(rec, "level", r"^error$") is True


def test_field_pattern_no_match():
    rec = make_record(level="info")
    assert check_field_pattern(rec, "level", r"^error$") is False


def test_field_pattern_missing_field():
    rec = make_record(msg="hello")
    assert check_field_pattern(rec, "level", r".*") is False


def test_field_pattern_invalid_regex_returns_false():
    rec = make_record(level="info")
    assert check_field_pattern(rec, "level", r"[invalid") is False


# --- validate_record ---

def test_validate_record_passes():
    rec = make_record(level="info", msg="ok", ts="2024-01-01T00:00:00Z")
    is_valid, errors = validate_record(rec, required=["level", "msg"])
    assert is_valid is True
    assert errors == []


def test_validate_record_missing_required():
    rec = make_record(level="info")
    is_valid, errors = validate_record(rec, required=["level", "ts"])
    assert is_valid is False
    assert any("ts" in e for e in errors)


def test_validate_record_pattern_fails():
    rec = make_record(level="debug")
    is_valid, errors = validate_record(rec, field_patterns={"level": r"^(info|error)$"})
    assert is_valid is False
    assert any("level" in e for e in errors)


def test_validate_record_pattern_passes():
    rec = make_record(level="info")
    is_valid, errors = validate_record(rec, field_patterns={"level": r"^(info|error)$"})
    assert is_valid is True


def test_validate_record_no_constraints():
    rec = make_record(x=1)
    is_valid, errors = validate_record(rec)
    assert is_valid is True
    assert errors == []


# --- filter_valid_records ---

def test_filter_valid_keeps_valid():
    records = [
        make_record(level="info", msg="a"),
        make_record(msg="b"),  # missing level
        make_record(level="error", msg="c"),
    ]
    result = list(filter_valid_records(records, required=["level", "msg"]))
    assert len(result) == 2
    assert all("level" in r for r in result)


def test_filter_valid_invert_yields_invalid():
    records = [
        make_record(level="info", msg="a"),
        make_record(msg="b"),
    ]
    result = list(filter_valid_records(records, required=["level", "msg"], invert=True))
    assert len(result) == 1
    assert result[0]["msg"] == "b"


def test_filter_valid_empty_input():
    result = list(filter_valid_records([], required=["level"]))
    assert result == []
