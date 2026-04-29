"""Tests for logslice.cli_label."""

import argparse
import pytest
from logslice.cli_label import (
    register_label_args,
    is_label_active,
    extract_label_kwargs,
    describe_label,
)


def make_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser()
    register_label_args(p)
    return p


def test_register_adds_label_rule():
    p = make_parser()
    args = p.parse_args(["--label-rule", "level:eq:error=bad"])
    assert args.label_rules == ["level:eq:error=bad"]


def test_register_repeatable():
    p = make_parser()
    args = p.parse_args(["--label-rule", "level:eq:error=bad", "--label-rule", "level:eq:warn=meh"])
    assert len(args.label_rules) == 2


def test_register_default_dest():
    p = make_parser()
    args = p.parse_args([])
    assert args.label_dest == "label"


def test_register_custom_dest():
    p = make_parser()
    args = p.parse_args(["--label-dest", "category"])
    assert args.label_dest == "category"


def test_register_default_multi_false():
    p = make_parser()
    args = p.parse_args([])
    assert args.label_multi is False


def test_register_multi_flag():
    p = make_parser()
    args = p.parse_args(["--label-multi"])
    assert args.label_multi is True


def test_is_label_active_with_rules():
    p = make_parser()
    args = p.parse_args(["--label-rule", "level:eq:error=bad"])
    assert is_label_active(args) is True


def test_is_label_active_no_rules():
    p = make_parser()
    args = p.parse_args([])
    assert is_label_active(args) is False


def test_extract_label_kwargs_valid():
    p = make_parser()
    args = p.parse_args(["--label-rule", "level:eq:error=bad", "--label-default", "ok"])
    kwargs = extract_label_kwargs(args)
    assert kwargs["rules"] == [("level", "eq", "error", "bad")]
    assert kwargs["default"] == "ok"
    assert kwargs["dest"] == "label"
    assert kwargs["multi"] is False


def test_extract_label_kwargs_invalid_rule_raises():
    p = make_parser()
    args = p.parse_args(["--label-rule", "badspec"])
    with pytest.raises(ValueError, match="Invalid --label-rule"):
        extract_label_kwargs(args)


def test_describe_label_no_rules():
    assert describe_label([]) == "no label rules"


def test_describe_label_with_rules():
    rules = [("level", "eq", "error", "bad")]
    desc = describe_label(rules)
    assert "level:eq:error -> bad" in desc
