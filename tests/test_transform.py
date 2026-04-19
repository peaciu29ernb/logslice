"""Tests for logslice.transform module."""

import pytest
from logslice.transform import (
    rename_fields,
    drop_fields,
    keep_fields,
    add_field,
    apply_transforms,
)


SAMPLE = {"level": "info", "msg": "hello", "ts": "2024-01-01", "_raw": "raw line"}


def test_rename_fields_basic():
    result = rename_fields(SAMPLE, {"msg": "message", "ts": "timestamp"})
    assert "message" in result
    assert "timestamp" in result
    assert "msg" not in result
    assert "ts" not in result


def test_rename_fields_preserves_raw():
    result = rename_fields(SAMPLE, {"_raw": "original"})
    assert "_raw" in result
    assert result["_raw"] == "raw line"


def test_rename_fields_unknown_key_unchanged():
    result = rename_fields(SAMPLE, {"nonexistent": "other"})
    assert "level" in result
    assert "msg" in result


def test_drop_fields_removes():
    result = drop_fields(SAMPLE, ["level", "ts"])
    assert "level" not in result
    assert "ts" not in result
    assert "msg" in result


def test_drop_fields_preserves_raw():
    result = drop_fields(SAMPLE, ["_raw"])
    assert "_raw" in result


def test_keep_fields_only_keeps():
    result = keep_fields(SAMPLE, ["level", "msg"])
    assert set(result.keys()) == {"level", "msg", "_raw"}


def test_keep_fields_missing_field():
    result = keep_fields(SAMPLE, ["level", "nonexistent"])
    assert "nonexistent" not in result
    assert "level" in result


def test_add_field():
    result = add_field(SAMPLE, "env", "production")
    assert result["env"] == "production"
    assert result["level"] == "info"


def test_add_field_does_not_mutate():
    add_field(SAMPLE, "env", "production")
    assert "env" not in SAMPLE


def test_apply_transforms_rename_and_drop():
    records = [{"level": "warn", "msg": "oops", "_raw": "r"}]
    result = list(apply_transforms(records, rename={"msg": "message"}, drop=["level"]))
    assert result[0].get("message") == "oops"
    assert "level" not in result[0]


def test_apply_transforms_keep():
    records = [{"a": 1, "b": 2, "c": 3, "_raw": "r"}]
    result = list(apply_transforms(records, keep=["a"]))
    assert set(result[0].keys()) == {"a", "_raw"}


def test_apply_transforms_empty():
    assert list(apply_transforms([], rename={"x": "y"})) == []
