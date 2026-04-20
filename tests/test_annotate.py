"""Tests for logslice.annotate."""

import pytest

from logslice.annotate import (
    annotate_records,
    annotate_with_extract,
    annotate_with_template,
    annotate_with_value,
    apply_annotations,
)


# ---------------------------------------------------------------------------
# annotate_with_value
# ---------------------------------------------------------------------------

def test_annotate_with_value_adds_field():
    rec = {"msg": "hello", "_raw": "msg=hello"}
    result = annotate_with_value(rec, field="env", value="prod")
    assert result["env"] == "prod"


def test_annotate_with_value_preserves_existing():
    rec = {"msg": "hello"}
    result = annotate_with_value(rec, field="env", value="prod")
    assert result["msg"] == "hello"


def test_annotate_with_value_does_not_mutate():
    rec = {"msg": "hello"}
    annotate_with_value(rec, field="env", value="prod")
    assert "env" not in rec


# ---------------------------------------------------------------------------
# annotate_with_extract
# ---------------------------------------------------------------------------

def test_extract_basic_group():
    rec = {"url": "/api/users/42"}
    result = annotate_with_extract(rec, "url", "user_id", r"/users/(\d+)")
    assert result["user_id"] == "42"


def test_extract_no_match_gives_none():
    rec = {"url": "/api/items"}
    result = annotate_with_extract(rec, "url", "user_id", r"/users/(\d+)")
    assert result["user_id"] is None


def test_extract_missing_src_field_gives_none():
    rec = {"msg": "hello"}
    result = annotate_with_extract(rec, "url", "user_id", r"/users/(\d+)")
    assert result["user_id"] is None


def test_extract_invalid_pattern_gives_none():
    rec = {"url": "/api/users/42"}
    result = annotate_with_extract(rec, "url", "user_id", r"[invalid")
    assert result["user_id"] is None


def test_extract_does_not_mutate():
    rec = {"url": "/api/users/42"}
    annotate_with_extract(rec, "url", "user_id", r"/users/(\d+)")
    assert "user_id" not in rec


# ---------------------------------------------------------------------------
# annotate_with_template
# ---------------------------------------------------------------------------

def test_template_renders_fields():
    rec = {"level": "error", "message": "oops"}
    result = annotate_with_template(rec, "summary", "{level}: {message}")
    assert result["summary"] == "error: oops"


def test_template_missing_key_becomes_empty_string():
    rec = {"level": "warn"}
    result = annotate_with_template(rec, "summary", "{level}: {message}")
    assert result["summary"] == "warn: "


def test_template_does_not_mutate():
    rec = {"level": "info"}
    annotate_with_template(rec, "summary", "{level}")
    assert "summary" not in rec


# ---------------------------------------------------------------------------
# apply_annotations & annotate_records
# ---------------------------------------------------------------------------

def test_apply_annotations_chains():
    from functools import partial

    rec = {"msg": "hello"}
    fns = [
        partial(annotate_with_value, field="a", value="1"),
        partial(annotate_with_value, field="b", value="2"),
    ]
    result = apply_annotations(rec, fns)
    assert result["a"] == "1"
    assert result["b"] == "2"


def test_annotate_records_yields_all():
    from functools import partial

    records = [{"n": str(i)} for i in range(3)]
    fns = [partial(annotate_with_value, field="src", value="test")]
    results = list(annotate_records(records, fns))
    assert len(results) == 3
    assert all(r["src"] == "test" for r in results)


def test_annotate_records_empty_input():
    results = list(annotate_records([], []))
    assert results == []
