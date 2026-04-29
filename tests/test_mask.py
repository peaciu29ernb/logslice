"""Tests for logslice.mask."""

import pytest
from logslice.mask import (
    _mask_string,
    mask_field,
    mask_fields,
    mask_pattern,
    mask_records,
)


# --- _mask_string ---

def test_mask_string_fully_hidden():
    assert _mask_string("secret", 0, 0, "*") == "******"


def test_mask_string_show_first():
    assert _mask_string("secret", 2, 0, "*") == "se****"


def test_mask_string_show_last():
    assert _mask_string("secret", 0, 2, "*") == "****et"


def test_mask_string_show_both():
    assert _mask_string("secret", 1, 1, "*") == "s****t"


def test_mask_string_visible_exceeds_length_returns_original():
    assert _mask_string("hi", 2, 1, "*") == "hi"


def test_mask_string_custom_char():
    assert _mask_string("abcde", 1, 1, "#") == "a###e"


# --- mask_field ---

def test_mask_field_basic():
    rec = {"token": "abc123", "level": "info"}
    result = mask_field(rec, "token")
    assert result["token"] == "******"
    assert result["level"] == "info"


def test_mask_field_does_not_mutate_original():
    rec = {"token": "abc123"}
    mask_field(rec, "token")
    assert rec["token"] == "abc123"


def test_mask_field_unknown_field_unchanged():
    rec = {"level": "warn"}
    result = mask_field(rec, "token")
    assert result == rec


def test_mask_field_skips_raw():
    rec = {"__raw__": "raw line", "token": "xyz"}
    result = mask_field(rec, "__raw__")
    assert result["__raw__"] == "raw line"


def test_mask_field_non_string_coerced():
    rec = {"code": 12345}
    result = mask_field(rec, "code", show_first=1, show_last=1)
    assert result["code"] == "1***5"


# --- mask_fields ---

def test_mask_fields_multiple():
    rec = {"email": "user@example.com", "token": "abcdef", "level": "info"}
    result = mask_fields(rec, ["email", "token"], show_first=2)
    assert result["email"].startswith("us")
    assert result["token"].startswith("ab")
    assert result["level"] == "info"


# --- mask_pattern ---

def test_mask_pattern_replaces_in_string_fields():
    rec = {"msg": "token=abc123 other", "level": "info"}
    result = mask_pattern(rec, r"token=\w+")
    assert result["msg"] == "[MASKED] other"
    assert result["level"] == "info"


def test_mask_pattern_custom_replacement():
    rec = {"msg": "password=secret"}
    result = mask_pattern(rec, r"password=\S+", replacement="password=***")
    assert result["msg"] == "password=***"


def test_mask_pattern_skips_non_string_values():
    rec = {"count": 42, "msg": "hello"}
    result = mask_pattern(rec, r"hello")
    assert result["count"] == 42
    assert result["msg"] == "[MASKED]"


def test_mask_pattern_preserves_raw():
    rec = {"__raw__": "original line", "msg": "hello"}
    result = mask_pattern(rec, r"hello")
    assert result["__raw__"] == "original line"


def test_mask_pattern_invalid_regex_returns_original():
    rec = {"msg": "hello"}
    result = mask_pattern(rec, r"[invalid")
    assert result == rec


# --- mask_records ---

def test_mask_records_applies_field_masking():
    records = [{"token": "abc123", "level": "info"}]
    result = list(mask_records(records, fields=["token"], show_first=1))
    assert result[0]["token"] == "a*****"


def test_mask_records_applies_pattern_masking():
    records = [{"msg": "ssn=123-45-6789"}]
    result = list(mask_records(records, pattern=r"\d{3}-\d{2}-\d{4}"))
    assert "[MASKED]" in result[0]["msg"]


def test_mask_records_both_field_and_pattern():
    records = [{"token": "abcdef", "msg": "key=secret"}]
    result = list(mask_records(records, fields=["token"], pattern=r"key=\w+"))
    assert result[0]["token"] == "******"
    assert "[MASKED]" in result[0]["msg"]


def test_mask_records_empty_input():
    assert list(mask_records([], fields=["token"])) == []
