"""Tests for logslice/patch.py."""

import pytest
from logslice.patch import (
    DELETE,
    DEFAULT,
    SET,
    parse_patch_arg,
    patch_record,
    patch_records,
)


# ---------------------------------------------------------------------------
# parse_patch_arg
# ---------------------------------------------------------------------------

def test_parse_patch_arg_set_basic():
    assert parse_patch_arg("env=prod") == (SET, "env", "prod")


def test_parse_patch_arg_set_empty_value():
    assert parse_patch_arg("env=") == (SET, "env", "")


def test_parse_patch_arg_delete():
    assert parse_patch_arg("~secret") == (DELETE, "secret", None)


def test_parse_patch_arg_default():
    assert parse_patch_arg("?region=us-east-1") == (DEFAULT, "region", "us-east-1")


def test_parse_patch_arg_no_equals_returns_none():
    assert parse_patch_arg("justfield") is None


def test_parse_patch_arg_empty_string_returns_none():
    assert parse_patch_arg("") is None


def test_parse_patch_arg_tilde_no_field_returns_none():
    assert parse_patch_arg("~") is None


def test_parse_patch_arg_empty_field_returns_none():
    assert parse_patch_arg("=value") is None


# ---------------------------------------------------------------------------
# patch_record
# ---------------------------------------------------------------------------

def test_patch_record_set_new_field():
    rec = {"level": "info", "_raw": "x"}
    result = patch_record(rec, [(SET, "env", "prod")])
    assert result["env"] == "prod"


def test_patch_record_set_overwrites_existing():
    rec = {"level": "info"}
    result = patch_record(rec, [(SET, "level", "warn")])
    assert result["level"] == "warn"


def test_patch_record_delete_removes_field():
    rec = {"level": "info", "secret": "abc"}
    result = patch_record(rec, [(DELETE, "secret", None)])
    assert "secret" not in result


def test_patch_record_delete_missing_field_is_noop():
    rec = {"level": "info"}
    result = patch_record(rec, [(DELETE, "nope", None)])
    assert result == {"level": "info"}


def test_patch_record_default_fills_absent_field():
    rec = {"level": "info"}
    result = patch_record(rec, [(DEFAULT, "region", "us-east-1")])
    assert result["region"] == "us-east-1"


def test_patch_record_default_does_not_overwrite_existing():
    rec = {"region": "eu-west-1"}
    result = patch_record(rec, [(DEFAULT, "region", "us-east-1")])
    assert result["region"] == "eu-west-1"


def test_patch_record_default_replaces_none():
    rec = {"region": None}
    result = patch_record(rec, [(DEFAULT, "region", "us-east-1")])
    assert result["region"] == "us-east-1"


def test_patch_record_skips_raw_field():
    rec = {"_raw": "original"}
    result = patch_record(rec, [(SET, "_raw", "changed")])
    assert result["_raw"] == "original"


def test_patch_record_does_not_mutate_original():
    rec = {"level": "info"}
    patch_record(rec, [(SET, "level", "warn")])
    assert rec["level"] == "info"


# ---------------------------------------------------------------------------
# patch_records
# ---------------------------------------------------------------------------

def test_patch_records_applies_to_all():
    records = [{"level": "info"}, {"level": "debug"}]
    ops = [(SET, "env", "staging")]
    result = list(patch_records(records, ops))
    assert all(r["env"] == "staging" for r in result)


def test_patch_records_empty_input():
    assert list(patch_records([], [(SET, "x", "1")])) == []


def test_patch_records_empty_ops():
    records = [{"a": "1"}]
    result = list(patch_records(records, []))
    assert result == [{"a": "1"}]
