"""Tests for logslice/cli_rollup.py."""
from __future__ import annotations

import argparse

import pytest

from logslice.cli_rollup import (
    extract_rollup_kwargs,
    is_rollup_active,
    register_rollup_args,
    validate_rollup_args,
)


def make_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser()
    register_rollup_args(p)
    return p


def test_register_adds_rollup_field():
    p = make_parser()
    actions = {a.dest for a in p._actions}
    assert "rollup_field" in actions


def test_register_adds_rollup_group():
    p = make_parser()
    actions = {a.dest for a in p._actions}
    assert "rollup_group" in actions


def test_register_adds_rollup_interval():
    p = make_parser()
    actions = {a.dest for a in p._actions}
    assert "rollup_interval" in actions


def test_register_default_interval_is_60():
    p = make_parser()
    args = p.parse_args([])
    assert args.rollup_interval == 60


def test_register_default_time_field():
    p = make_parser()
    args = p.parse_args([])
    assert args.rollup_time_field == "timestamp"


def test_is_rollup_active_false_when_no_field():
    p = make_parser()
    args = p.parse_args([])
    assert is_rollup_active(args) is False


def test_is_rollup_active_true_when_field_set():
    p = make_parser()
    args = p.parse_args(["--rollup-field", "latency"])
    assert is_rollup_active(args) is True


def test_extract_rollup_kwargs_basic():
    p = make_parser()
    args = p.parse_args(["--rollup-field", "latency", "--rollup-interval", "300"])
    kwargs = extract_rollup_kwargs(args)
    assert kwargs["value_field"] == "latency"
    assert kwargs["interval_seconds"] == 300
    assert "sum" in kwargs["ops"]


def test_extract_rollup_kwargs_custom_ops():
    p = make_parser()
    args = p.parse_args(["--rollup-field", "bytes", "--rollup-ops", "sum,min"])
    kwargs = extract_rollup_kwargs(args)
    assert kwargs["ops"] == ("sum", "min")


def test_extract_rollup_kwargs_group_field():
    p = make_parser()
    args = p.parse_args(["--rollup-field", "latency", "--rollup-group", "service"])
    kwargs = extract_rollup_kwargs(args)
    assert kwargs["group_field"] == "service"


def test_validate_rollup_args_invalid_interval():
    p = make_parser()
    args = p.parse_args(["--rollup-field", "latency", "--rollup-interval", "0"])
    with pytest.raises(ValueError, match="positive"):
        validate_rollup_args(args)


def test_validate_rollup_args_invalid_op():
    p = make_parser()
    args = p.parse_args(["--rollup-field", "latency", "--rollup-ops", "median"])
    with pytest.raises(ValueError, match="median"):
        validate_rollup_args(args)


def test_validate_rollup_args_no_field_is_noop():
    p = make_parser()
    args = p.parse_args([])
    validate_rollup_args(args)  # should not raise
