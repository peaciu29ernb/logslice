"""Tests for logslice.cli_fill."""

import argparse
import pytest
from logslice.cli_fill import register_fill_args, is_fill_active, extract_fill_kwargs


def make_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser()
    register_fill_args(p)
    return p


def test_register_adds_fill_flag():
    p = make_parser()
    args = p.parse_args(["--fill", "status"])
    assert args.fill_fields == ["status"]


def test_register_fill_repeatable():
    p = make_parser()
    args = p.parse_args(["--fill", "a", "--fill", "b"])
    assert args.fill_fields == ["a", "b"]


def test_register_fill_default_empty():
    p = make_parser()
    args = p.parse_args([])
    assert args.fill_fields == []


def test_register_fill_default_value_is_none():
    p = make_parser()
    args = p.parse_args([])
    assert args.fill_default is None


def test_register_fill_default_custom():
    p = make_parser()
    args = p.parse_args(["--fill", "x", "--fill-default", "N/A"])
    assert args.fill_default == "N/A"


def test_register_fill_forward_default_false():
    p = make_parser()
    args = p.parse_args([])
    assert args.fill_forward is False


def test_register_fill_forward_flag():
    p = make_parser()
    args = p.parse_args(["--fill", "v", "--fill-forward"])
    assert args.fill_forward is True


def test_is_fill_active_true():
    p = make_parser()
    args = p.parse_args(["--fill", "status"])
    assert is_fill_active(args) is True


def test_is_fill_active_false():
    p = make_parser()
    args = p.parse_args([])
    assert is_fill_active(args) is False


def test_extract_fill_kwargs_basic():
    p = make_parser()
    args = p.parse_args(["--fill", "a", "--fill", "b", "--fill-default", "0"])
    kwargs = extract_fill_kwargs(args)
    assert kwargs["fields"] == ["a", "b"]
    assert kwargs["default"] == "0"
    assert kwargs["forward"] is False


def test_extract_fill_kwargs_forward():
    p = make_parser()
    args = p.parse_args(["--fill", "v", "--fill-forward"])
    kwargs = extract_fill_kwargs(args)
    assert kwargs["forward"] is True
