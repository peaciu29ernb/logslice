"""Tests for logslice.cli_annotate."""

import argparse
import pytest

from logslice.cli_annotate import (
    _parse_add_field,
    _parse_extract,
    _parse_template,
    extract_annotate_kwargs,
    register_annotate_args,
)


def make_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser()
    register_annotate_args(p)
    return p


# ---------------------------------------------------------------------------
# argument registration
# ---------------------------------------------------------------------------

def test_register_adds_add_field():
    p = make_parser()
    args = p.parse_args(["--add-field", "env=prod"])
    assert args.add_fields == ["env=prod"]


def test_register_adds_extract():
    p = make_parser()
    args = p.parse_args(["--extract", "url:uid:/users/(\\d+)"])
    assert args.extracts == ["url:uid:/users/(\\d+)"]


def test_register_adds_template():
    p = make_parser()
    args = p.parse_args(["--template", "summary:{level}: {msg}"])
    assert args.templates == ["summary:{level}: {msg}"]


# ---------------------------------------------------------------------------
# _parse_add_field
# ---------------------------------------------------------------------------

def test_parse_add_field_basic():
    assert _parse_add_field("env=prod") == ("env", "prod")


def test_parse_add_field_value_with_equals():
    key, value = _parse_add_field("expr=a=b")
    assert key == "expr"
    assert value == "a=b"


def test_parse_add_field_no_equals_raises():
    with pytest.raises(argparse.ArgumentTypeError):
        _parse_add_field("envprod")


# ---------------------------------------------------------------------------
# _parse_extract
# ---------------------------------------------------------------------------

def test_parse_extract_basic():
    assert _parse_extract("url:uid:/users/(\\d+)") == (
        "url",
        "uid",
        "/users/(\\d+)",
    )


def test_parse_extract_too_few_parts_raises():
    with pytest.raises(argparse.ArgumentTypeError):
        _parse_extract("url:uid")


# ---------------------------------------------------------------------------
# _parse_template
# ---------------------------------------------------------------------------

def test_parse_template_basic():
    dest, tmpl = _parse_template("summary:{level}: {msg}")
    assert dest == "summary"
    assert tmpl == "{level}: {msg}"


def test_parse_template_no_colon_raises():
    with pytest.raises(argparse.ArgumentTypeError):
        _parse_template("nodestination")


# ---------------------------------------------------------------------------
# extract_annotate_kwargs integration
# ---------------------------------------------------------------------------

def test_extract_returns_callables():
    p = make_parser()
    args = p.parse_args([
        "--add-field", "env=prod",
        "--template", "s:{level}",
    ])
    fns = extract_annotate_kwargs(args)
    assert len(fns) == 2
    rec = {"level": "info"}
    result = fns[0](rec)
    assert result["env"] == "prod"


def test_extract_empty_args_returns_empty_list():
    p = make_parser()
    args = p.parse_args([])
    fns = extract_annotate_kwargs(args)
    assert fns == []
