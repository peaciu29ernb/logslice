"""Tests for logslice.redact."""

import pytest
from logslice.redact import (
    REDACTED_PLACEHOLDER,
    redact_fields,
    mask_field_pattern,
    apply_redactions,
    redact_records,
)


def make_record(**kwargs):
    return {"_raw": "original line", **kwargs}


def test_redact_fields_replaces_value():
    rec = make_record(email="user@example.com", level="info")
    result = redact_fields(rec, ["email"])
    assert result["email"] == REDACTED_PLACEHOLDER
    assert result["level"] == "info"


def test_redact_fields_preserves_raw():
    rec = make_record(token="secret")
    result = redact_fields(rec, ["token", "_raw"])
    assert result["_raw"] == "original line"
    assert result["token"] == REDACTED_PLACEHOLDER


def test_redact_fields_unknown_field_unchanged():
    rec = make_record(level="warn")
    result = redact_fields(rec, ["nonexistent"])
    assert result == rec


def test_redact_fields_does_not_mutate_original():
    rec = make_record(password="hunter2")
    redact_fields(rec, ["password"])
    assert rec["password"] == "hunter2"


def test_mask_field_pattern_replaces_match():
    rec = make_record(msg="token=abc123 received")
    result = mask_field_pattern(rec, "msg", r"token=\w+")
    assert result["msg"] == f"{REDACTED_PLACEHOLDER} received"


def test_mask_field_pattern_no_match_unchanged():
    rec = make_record(msg="hello world")
    result = mask_field_pattern(rec, "msg", r"token=\w+")
    assert result["msg"] == "hello world"


def test_mask_field_pattern_invalid_regex_unchanged():
    rec = make_record(msg="some value")
    result = mask_field_pattern(rec, "msg", r"[invalid")
    assert result["msg"] == "some value"


def test_mask_field_pattern_missing_field_unchanged():
    rec = make_record(level="info")
    result = mask_field_pattern(rec, "msg", r"\w+")
    assert "msg" not in result


def test_mask_field_pattern_skips_raw():
    rec = make_record()
    result = mask_field_pattern(rec, "_raw", r".*")
    assert result["_raw"] == "original line"


def test_apply_redactions_both_operations():
    rec = make_record(email="a@b.com", msg="ssn=123-45-6789 here")
    result = apply_redactions(
        rec,
        redact=["email"],
        mask_field="msg",
        mask_pattern=r"ssn=\S+",
    )
    assert result["email"] == REDACTED_PLACEHOLDER
    assert result["msg"] == f"{REDACTED_PLACEHOLDER} here"


def test_apply_redactions_none_options_unchanged():
    rec = make_record(level="debug")
    result = apply_redactions(rec)
    assert result["level"] == "debug"


def test_redact_records_iterator():
    records = [
        make_record(password="secret1", level="info"),
        make_record(password="secret2", level="error"),
    ]
    results = list(redact_records(records, redact=["password"]))
    assert all(r["password"] == REDACTED_PLACEHOLDER for r in results)
    assert results[0]["level"] == "info"
    assert results[1]["level"] == "error"


def test_redact_records_empty():
    assert list(redact_records([], redact=["x"])) == []
