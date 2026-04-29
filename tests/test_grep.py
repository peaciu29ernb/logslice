"""Tests for logslice.grep and logslice.cli_grep."""

import argparse
import pytest

from logslice.grep import _compile, grep_record, grep_records
from logslice.cli_grep import (
    register_grep_args,
    is_grep_active,
    extract_grep_kwargs,
)


# ---------------------------------------------------------------------------
# _compile
# ---------------------------------------------------------------------------

def test_compile_valid_pattern():
    assert _compile(r"\d+") is not None


def test_compile_invalid_pattern_returns_none():
    assert _compile(r"[") is None


def test_compile_ignore_case_flag():
    pat = _compile("hello", ignore_case=True)
    assert pat.search("HELLO") is not None


# ---------------------------------------------------------------------------
# grep_record
# ---------------------------------------------------------------------------

def test_grep_record_matches_any_field():
    rec = {"level": "error", "msg": "disk full", "_raw": "..."}
    assert grep_record(rec, "disk") is True


def test_grep_record_no_match_returns_false():
    rec = {"level": "info", "msg": "all good"}
    assert grep_record(rec, "error") is False


def test_grep_record_specific_field_match():
    rec = {"level": "error", "msg": "timeout"}
    assert grep_record(rec, "error", fields=["level"]) is True


def test_grep_record_specific_field_no_match():
    rec = {"level": "error", "msg": "timeout"}
    assert grep_record(rec, "error", fields=["msg"]) is False


def test_grep_record_skips_raw_field():
    rec = {"_raw": "error in raw", "level": "info"}
    assert grep_record(rec, "error") is False


def test_grep_record_ignore_case():
    rec = {"msg": "Connection Refused"}
    assert grep_record(rec, "connection refused", ignore_case=True) is True


def test_grep_record_invert_match():
    rec = {"msg": "all good"}
    assert grep_record(rec, "error", invert=True) is True


def test_grep_record_invert_no_match():
    rec = {"msg": "fatal error"}
    assert grep_record(rec, "error", invert=True) is False


def test_grep_record_invalid_pattern_returns_false():
    rec = {"msg": "hello"}
    assert grep_record(rec, "[") is False


# ---------------------------------------------------------------------------
# grep_records
# ---------------------------------------------------------------------------

def test_grep_records_filters_correctly():
    records = [
        {"msg": "started"},
        {"msg": "error occurred"},
        {"msg": "finished"},
    ]
    result = list(grep_records(records, "error"))
    assert len(result) == 1
    assert result[0]["msg"] == "error occurred"


def test_grep_records_empty_input():
    assert list(grep_records([], "pattern")) == []


def test_grep_records_invert_all_non_matching():
    records = [{"msg": "ok"}, {"msg": "error"}]
    result = list(grep_records(records, "error", invert=True))
    assert result == [{"msg": "ok"}]


# ---------------------------------------------------------------------------
# CLI helpers
# ---------------------------------------------------------------------------

def make_parser():
    p = argparse.ArgumentParser()
    register_grep_args(p)
    return p


def test_register_adds_grep_arg():
    p = make_parser()
    args = p.parse_args(["--grep", "foo"])
    assert args.grep == "foo"


def test_register_adds_grep_fields():
    p = make_parser()
    args = p.parse_args(["--grep", "x", "--grep-fields", "level", "msg"])
    assert args.grep_fields == ["level", "msg"]


def test_is_grep_active_true():
    p = make_parser()
    args = p.parse_args(["--grep", "pattern"])
    assert is_grep_active(args) is True


def test_is_grep_active_false():
    p = make_parser()
    args = p.parse_args([])
    assert is_grep_active(args) is False


def test_extract_grep_kwargs_defaults():
    p = make_parser()
    args = p.parse_args(["--grep", "hello"])
    kwargs = extract_grep_kwargs(args)
    assert kwargs["pattern"] == "hello"
    assert kwargs["fields"] is None
    assert kwargs["ignore_case"] is False
    assert kwargs["invert"] is False


def test_extract_grep_kwargs_all_flags():
    p = make_parser()
    args = p.parse_args(
        ["--grep", "err", "--grep-fields", "msg", "--grep-ignore-case", "--grep-invert"]
    )
    kwargs = extract_grep_kwargs(args)
    assert kwargs["fields"] == ["msg"]
    assert kwargs["ignore_case"] is True
    assert kwargs["invert"] is True
