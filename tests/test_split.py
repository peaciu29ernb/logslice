"""Tests for logslice.split."""

import os
import json
import pytest

from logslice.split import split_records, make_filename, write_split


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def make_record(level="info", msg="hello", **extra):
    rec = {"level": level, "msg": msg}
    rec.update(extra)
    return rec


# ---------------------------------------------------------------------------
# split_records
# ---------------------------------------------------------------------------

def test_split_basic_partition():
    records = [
        make_record(level="info"),
        make_record(level="error"),
        make_record(level="info"),
    ]
    result = split_records(records, field="level")
    assert set(result.keys()) == {"info", "error"}
    assert len(result["info"]) == 2
    assert len(result["error"]) == 1


def test_split_missing_field_goes_to_unknown():
    records = [make_record(), {"msg": "no level"}]
    result = split_records(records, field="level")
    assert "info" in result
    assert "__unknown__" in result
    assert result["__unknown__"][0]["msg"] == "no level"


def test_split_custom_missing_key():
    records = [{"msg": "orphan"}]
    result = split_records(records, field="level", missing="other")
    assert "other" in result


def test_split_empty_input():
    result = split_records([], field="level")
    assert result == {}


def test_split_non_string_value_coerced():
    records = [{"code": 200, "msg": "ok"}, {"code": 404, "msg": "not found"}]
    result = split_records(records, field="code")
    assert "200" in result
    assert "404" in result


# ---------------------------------------------------------------------------
# make_filename
# ---------------------------------------------------------------------------

def test_make_filename_basic():
    path = make_filename("/tmp", "out_", "info")
    assert path == "/tmp/out_info.log"


def test_make_filename_sanitises_special_chars():
    path = make_filename("/tmp", "", "prod/us-east-1")
    assert "/" not in os.path.basename(path)


def test_make_filename_custom_ext():
    path = make_filename("/logs", "app-", "warn", ext=".jsonl")
    assert path.endswith(".jsonl")


# ---------------------------------------------------------------------------
# write_split
# ---------------------------------------------------------------------------

def test_write_split_creates_files(tmp_path):
    buckets = {
        "info": [make_record(level="info")],
        "error": [make_record(level="error"), make_record(level="error")],
    }
    summary = write_split(buckets, str(tmp_path))
    assert len(summary) == 2
    assert sum(summary.values()) == 3


def test_write_split_valid_json_lines(tmp_path):
    buckets = {"info": [make_record(level="info", _raw="raw line")]}
    write_split(buckets, str(tmp_path))
    files = list(tmp_path.iterdir())
    assert len(files) == 1
    with open(files[0]) as fh:
        data = json.loads(fh.readline())
    assert "_raw" not in data
    assert data["level"] == "info"


def test_write_split_custom_formatter(tmp_path):
    buckets = {"warn": [make_record(level="warn")]}
    write_split(buckets, str(tmp_path), formatter=lambda r: r["level"].upper())
    files = list(tmp_path.iterdir())
    assert files[0].read_text().strip() == "WARN"


def test_write_split_creates_directory(tmp_path):
    target = str(tmp_path / "nested" / "output")
    buckets = {"debug": [make_record(level="debug")]}
    write_split(buckets, target)
    assert os.path.isdir(target)
