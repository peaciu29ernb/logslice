"""Tests for logslice.output module."""

import io
import pytest
from logslice.output import format_as_json, format_as_logfmt, format_record, write_records


SMPLE = {"level": "info", "msg": "hello world", "ts": "2024-01-01T00:00:00Z", "_raw": "orig"}


def test_format_as_json_basic():
    result = format_as_json({"a": 1, "b": "x"})
    assert result == '{"a": 1, "b": "x"}'


def test_format_as_json_excludes_nothing():
    # _raw is included in json output
    result = format_as_json({"_raw": "orig", "k": "v"})
    assert '"_raw"' in result


def test_format_as_logfmt_simple():
    result = format_as_logfmt({"level": "info", "code": "200"})
    assert "level=info" in result
    assert "code=200" in result


def test_format_as_logfmt_quotes_spaces():
    result = format_as_logfmt({"msg": "hello world"})
    assert 'msg="hello world"' in result


def test_format_as_logfmt_skips_raw():
    result = format_as_logfmt({"_raw": "original line", "level": "warn"})
    assert "_raw" not in result
    assert "level=warn" in result


def test_format_record_json():
    result = format_record({"a": 1}, "json")
    assert result == '{"a": 1}'


def test_format_record_raw_returns_raw_field():
    result = format_record(SAMPLE, "raw")
    assert result == "orig"


def test_format_record_raw_falls_back_to_json():
    record = {"level": "debug"}
    result = format_record(record, "raw")
    assert "level" in result


def test_format_record_logfmt():
    result = format_record({"k": "v"}, "logfmt")
    assert result == "k=v"


def test_write_records_returns_count():
    buf = io.StringIO()
    records = [{"a": 1}, {"b": 2}, {"c": 3}]
    count = write_records(records, fmt="json", out=buf)
    assert count == 3


def test_write_records_output_lines():
    buf = io.StringIO()
    write_records([{"x": 1}, {"x": 2}], fmt="json", out=buf)
    lines = buf.getvalue().strip().split("\n")
    assert len(lines) == 2


def test_write_records_empty():
    buf = io.StringIO()
    count = write_records([], out=buf)
    assert count == 0
    assert buf.getvalue() == ""
