"""Tests for logslice/cli_percentile.py"""

import argparse
import pytest
from logslice.cli_percentile import (
    register_percentile_args,
    is_percentile_active,
    extract_percentile_kwargs,
    validate_percentile_args,
    _DEFAULT_PERCENTILES,
)


def make_parser():
    p = argparse.ArgumentParser()
    register_percentile_args(p)
    return p


def test_register_adds_percentile_field():
    p = make_parser()
    args = p.parse_args(["--percentile-field", "latency"])
    assert args.percentile_field == "latency"


def test_register_adds_percentile_repeatable():
    p = make_parser()
    args = p.parse_args(["--percentile-field", "v", "--percentile", "50", "--percentile", "95"])
    assert args.percentiles == [50.0, 95.0]


def test_register_default_percentiles_is_none():
    p = make_parser()
    args = p.parse_args([])
    assert args.percentiles is None


def test_register_adds_percentile_group():
    p = make_parser()
    args = p.parse_args(["--percentile-field", "v", "--percentile-group", "env"])
    assert args.percentile_group == "env"


def test_is_percentile_active_true():
    p = make_parser()
    args = p.parse_args(["--percentile-field", "latency"])
    assert is_percentile_active(args) is True


def test_is_percentile_active_false():
    p = make_parser()
    args = p.parse_args([])
    assert is_percentile_active(args) is False


def test_extract_percentile_kwargs_defaults():
    p = make_parser()
    args = p.parse_args(["--percentile-field", "latency"])
    kwargs = extract_percentile_kwargs(args)
    assert kwargs["field"] == "latency"
    assert kwargs["percentiles"] == sorted(set(_DEFAULT_PERCENTILES))
    assert kwargs["group_by"] is None


def test_extract_percentile_kwargs_custom():
    p = make_parser()
    args = p.parse_args(
        ["--percentile-field", "rt", "--percentile", "75", "--percentile-group", "svc"]
    )
    kwargs = extract_percentile_kwargs(args)
    assert kwargs["percentiles"] == [75.0]
    assert kwargs["group_by"] == "svc"


def test_validate_percentile_args_valid():
    p = make_parser()
    args = p.parse_args(["--percentile-field", "v", "--percentile", "50"])
    assert validate_percentile_args(args) == []


def test_validate_percentile_args_out_of_range():
    p = make_parser()
    args = p.parse_args(["--percentile-field", "v", "--percentile", "101"])
    errors = validate_percentile_args(args)
    assert len(errors) == 1
    assert "101" in errors[0]


def test_validate_percentile_args_no_percentiles_is_valid():
    p = make_parser()
    args = p.parse_args(["--percentile-field", "v"])
    assert validate_percentile_args(args) == []
