"""Tests for logslice.cli_compare."""

import argparse
import pytest
from logslice.cli_compare import (
    register_compare_args,
    is_compare_active,
    extract_compare_kwargs,
    validate_compare_args,
)


def make_parser():
    p = argparse.ArgumentParser()
    register_compare_args(p)
    return p


def test_register_adds_compare_file():
    p = make_parser()
    args = p.parse_args(["--compare-file", "other.log", "--compare-key", "id"])
    assert args.compare_file == "other.log"


def test_register_adds_compare_key():
    p = make_parser()
    args = p.parse_args(["--compare-file", "f.log", "--compare-key", "request_id"])
    assert args.compare_key == "request_id"


def test_register_default_labels():
    p = make_parser()
    args = p.parse_args([])
    assert args.compare_label_left == "left"
    assert args.compare_label_right == "right"


def test_register_custom_labels():
    p = make_parser()
    args = p.parse_args(["--compare-label-left", "before", "--compare-label-right", "after"])
    assert args.compare_label_left == "before"
    assert args.compare_label_right == "after"


def test_register_compare_fields_nargs():
    p = make_parser()
    args = p.parse_args(["--compare-fields", "level", "msg"])
    assert args.compare_fields == ["level", "msg"]


def test_is_compare_active_true():
    p = make_parser()
    args = p.parse_args(["--compare-file", "f.log", "--compare-key", "id"])
    assert is_compare_active(args) is True


def test_is_compare_active_false_no_file():
    p = make_parser()
    args = p.parse_args([])
    assert is_compare_active(args) is False


def test_is_compare_active_false_no_key():
    p = make_parser()
    args = p.parse_args(["--compare-file", "f.log"])
    assert is_compare_active(args) is False


def test_extract_compare_kwargs():
    p = make_parser()
    args = p.parse_args([
        "--compare-file", "f.log",
        "--compare-key", "id",
        "--compare-fields", "level",
        "--compare-label-left", "a",
        "--compare-label-right", "b",
    ])
    kw = extract_compare_kwargs(args)
    assert kw["key_field"] == "id"
    assert kw["fields"] == ["level"]
    assert kw["label_left"] == "a"
    assert kw["label_right"] == "b"


def test_validate_missing_key_returns_error():
    p = make_parser()
    args = p.parse_args(["--compare-file", "f.log"])
    err = validate_compare_args(args)
    assert err is not None
    assert "--compare-key" in err


def test_validate_missing_file_returns_error():
    p = make_parser()
    args = p.parse_args(["--compare-key", "id"])
    err = validate_compare_args(args)
    assert err is not None
    assert "--compare-file" in err


def test_validate_both_present_returns_none():
    p = make_parser()
    args = p.parse_args(["--compare-file", "f.log", "--compare-key", "id"])
    assert validate_compare_args(args) is None


def test_validate_neither_present_returns_none():
    p = make_parser()
    args = p.parse_args([])
    assert validate_compare_args(args) is None
