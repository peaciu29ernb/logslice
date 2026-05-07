"""Tests for logslice/cli_patch.py."""

import argparse
import pytest
from logslice.patch import SET, DELETE, DEFAULT
from logslice.cli_patch import (
    extract_patch_kwargs,
    is_patch_active,
    register_patch_args,
)


def make_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser()
    register_patch_args(p)
    return p


def test_register_adds_patch_flag():
    p = make_parser()
    args = p.parse_args(["--patch", "env=prod"])
    assert args.patch_set == ["env=prod"]


def test_register_adds_patch_delete_flag():
    p = make_parser()
    args = p.parse_args(["--patch-delete", "secret"])
    assert args.patch_delete == ["secret"]


def test_register_adds_patch_default_flag():
    p = make_parser()
    args = p.parse_args(["--patch-default", "region=us-east-1"])
    assert args.patch_default == ["region=us-east-1"]


def test_register_defaults_are_empty_lists():
    p = make_parser()
    args = p.parse_args([])
    assert args.patch_set == []
    assert args.patch_delete == []
    assert args.patch_default == []


def test_patch_flags_are_repeatable():
    p = make_parser()
    args = p.parse_args(["--patch", "a=1", "--patch", "b=2"])
    assert args.patch_set == ["a=1", "b=2"]


# ---------------------------------------------------------------------------
# is_patch_active
# ---------------------------------------------------------------------------

def test_is_patch_active_false_when_empty():
    p = make_parser()
    args = p.parse_args([])
    assert is_patch_active(args) is False


def test_is_patch_active_true_with_set():
    p = make_parser()
    args = p.parse_args(["--patch", "env=prod"])
    assert is_patch_active(args) is True


def test_is_patch_active_true_with_delete():
    p = make_parser()
    args = p.parse_args(["--patch-delete", "secret"])
    assert is_patch_active(args) is True


def test_is_patch_active_true_with_default():
    p = make_parser()
    args = p.parse_args(["--patch-default", "region=us-east-1"])
    assert is_patch_active(args) is True


# ---------------------------------------------------------------------------
# extract_patch_kwargs
# ---------------------------------------------------------------------------

def test_extract_patch_kwargs_set_op():
    p = make_parser()
    args = p.parse_args(["--patch", "env=prod"])
    result = extract_patch_kwargs(args)
    assert result["ops"] == [(SET, "env", "prod")]


def test_extract_patch_kwargs_delete_op():
    p = make_parser()
    args = p.parse_args(["--patch-delete", "secret"])
    result = extract_patch_kwargs(args)
    assert result["ops"] == [(DELETE, "secret", None)]


def test_extract_patch_kwargs_default_op():
    p = make_parser()
    args = p.parse_args(["--patch-default", "region=us-east-1"])
    result = extract_patch_kwargs(args)
    assert result["ops"] == [(DEFAULT, "region", "us-east-1")]


def test_extract_patch_kwargs_mixed_ops():
    p = make_parser()
    args = p.parse_args(
        ["--patch", "env=prod", "--patch-delete", "secret"]
    )
    result = extract_patch_kwargs(args)
    ops = result["ops"]
    assert (SET, "env", "prod") in ops
    assert (DELETE, "secret", None) in ops


def test_extract_patch_kwargs_empty_returns_empty_ops():
    p = make_parser()
    args = p.parse_args([])
    result = extract_patch_kwargs(args)
    assert result["ops"] == []
