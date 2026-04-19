"""Tests for logslice.export."""

import pytest
from logslice.export import collect_fieldnames, format_as_csv, write_export


RECORDS = [
    {"level": "info", "msg": "started", "ts": "2024-01-01T00:00:00Z", "_raw": "..."},
    {"level": "error", "msg": "failed", "ts": "2024-01-01T00:01:00Z", "_raw": "..."},
]


def test_collect_fieldnames_excludes_raw():
    fields = collect_fieldnames(RECORDS)
    assert "_raw" not in fields


def test_collect_fieldnames_order():
    fields = collect_fieldnames(RECORDS)
    assert fields == ["level", "msg", "ts"]


def test_collect_fieldnames_custom_exclude():
    fields = collect_fieldnames(RECORDS, exclude=["_raw", "ts"])
    assert "ts" not in fields


def test_collect_fieldnames_empty():
    assert collect_fieldnames([]) == []


def test_format_as_csv_header():
    result = format_as_csv(RECORDS)
    first_line = result.splitlines()[0]
    assert first_line == "level,msg,ts"


def test_format_as_csv_rows():
    result = format_as_csv(RECORDS)
    lines = result.splitlines()
    assert len(lines) == 3  # header + 2 rows
    assert "info" in lines[1]
    assert "error" in lines[2]


def test_format_as_csv_empty():
    assert format_as_csv([]) == ""


def test_format_as_csv_missing_field():
    records = [{"a": "1"}, {"a": "2", "b": "x"}]
    result = format_as_csv(records)
    lines = result.splitlines()
    assert lines[0] == "a,b"
    assert lines[1] == "1,"


def test_format_as_tsv_delimiter():
    result = format_as_csv(RECORDS, delimiter="\t")
    first_line = result.splitlines()[0]
    assert "\t" in first_line


def test_write_export_csv():
    result = write_export(iter(RECORDS), fmt="csv")
    assert result.startswith("level,msg,ts")


def test_write_export_tsv():
    result = write_export(iter(RECORDS), fmt="tsv")
    assert "\t" in result.splitlines()[0]


def test_write_export_with_fieldnames():
    result = write_export(iter(RECORDS), fmt="csv", fieldnames=["msg", "level"])
    assert result.splitlines()[0] == "msg,level"
