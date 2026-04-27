"""Tests for logslice.template and logslice.cli_template."""

import argparse
import pytest

from logslice.template import (
    render_template,
    validate_template,
    apply_template,
    format_records_as_template,
)
from logslice.cli_template import (
    register_template_args,
    extract_template_kwargs,
    is_template_active,
    validate_template_arg,
)


# ---------------------------------------------------------------------------
# render_template
# ---------------------------------------------------------------------------

def test_render_template_basic():
    record = {"level": "INFO", "message": "hello"}
    result = render_template("{level} {message}", record)
    assert result == "INFO hello"


def test_render_template_missing_field_left_as_is():
    record = {"level": "WARN"}
    result = render_template("{level} {message}", record)
    assert result == "WARN {message}"


def test_render_template_ignores_raw_key():
    record = {"level": "DEBUG", "_raw": "original line", "msg": "ok"}
    result = render_template("{level} {msg}", record)
    assert result == "DEBUG ok"


def test_render_template_numeric_value():
    record = {"latency": 42, "status": 200}
    result = render_template("status={status} latency={latency}ms", record)
    assert result == "status=200 latency=42ms"


def test_render_template_empty_template():
    record = {"level": "INFO"}
    assert render_template("", record) == ""


def test_render_template_no_placeholders():
    record = {"level": "INFO"}
    assert render_template("static text", record) == "static text"


# ---------------------------------------------------------------------------
# validate_template
# ---------------------------------------------------------------------------

def test_validate_template_valid_returns_none():
    assert validate_template("{level} {message}") is None


def test_validate_template_invalid_returns_error():
    # Single '{' is a syntax error in format strings
    error = validate_template("bad { template")
    assert error is not None
    assert isinstance(error, str)


def test_validate_template_empty_is_valid():
    assert validate_template("") is None


# ---------------------------------------------------------------------------
# apply_template
# ---------------------------------------------------------------------------

def test_apply_template_adds_dest_field():
    records = [{"level": "INFO", "msg": "hi"}]
    out = list(apply_template(records, "{level}: {msg}"))
    assert out[0]["_rendered"] == "INFO: hi"


def test_apply_template_custom_dest_field():
    records = [{"level": "ERROR", "msg": "oops"}]
    out = list(apply_template(records, "{level}", dest_field="line"))
    assert "line" in out[0]
    assert out[0]["line"] == "ERROR"


def test_apply_template_preserves_original_fields():
    records = [{"level": "INFO", "msg": "ok", "_raw": "raw"}]
    out = list(apply_template(records, "{level}"))
    assert out[0]["level"] == "INFO"
    assert out[0]["_raw"] == "raw"


def test_apply_template_multiple_records():
    records = [{"n": i} for i in range(3)]
    out = list(apply_template(records, "n={n}"))
    assert [r["_rendered"] for r in out] == ["n=0", "n=1", "n=2"]


# ---------------------------------------------------------------------------
# format_records_as_template
# ---------------------------------------------------------------------------

def test_format_records_as_template_yields_strings():
    records = [{"level": "INFO", "msg": "a"}, {"level": "WARN", "msg": "b"}]
    out = list(format_records_as_template(records, "{level} {msg}"))
    assert out == ["INFO a", "WARN b"]


def test_format_records_as_template_empty():
    out = list(format_records_as_template([], "{level}"))
    assert out == []


# ---------------------------------------------------------------------------
# CLI helpers
# ---------------------------------------------------------------------------

def make_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser()
    register_template_args(p)
    return p


def test_register_adds_template_arg():
    p = make_parser()
    args = p.parse_args(["--template", "{level}"])
    assert args.template == "{level}"


def test_register_template_field_default():
    p = make_parser()
    args = p.parse_args([])
    assert args.template_field == "_rendered"


def test_is_template_active_true():
    p = make_parser()
    args = p.parse_args(["--template", "{msg}"])
    assert is_template_active(args) is True


def test_is_template_active_false():
    p = make_parser()
    args = p.parse_args([])
    assert is_template_active(args) is False


def test_extract_template_kwargs():
    p = make_parser()
    args = p.parse_args(["--template", "{x}", "--template-field", "out"])
    kwargs = extract_template_kwargs(args)
    assert kwargs["template"] == "{x}"
    assert kwargs["dest_field"] == "out"


def test_validate_template_arg_valid():
    p = make_parser()
    args = p.parse_args(["--template", "{level}"])
    assert validate_template_arg(args) is None


def test_validate_template_arg_not_set():
    p = make_parser()
    args = p.parse_args([])
    assert validate_template_arg(args) is None
