"""Tests for logslice.cli_resample."""

import argparse
import pytest
from logslice.cli_resample import (
    register_resample_args,
    is_resample_active,
    extract_resample_kwargs,
    validate_resample_args,
)


def make_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser()
    register_resample_args(p)
    return p


def test_register_adds_resample_time():
    p = make_parser()
    args = p.parse_args(["--resample-time", "ts"])
    assert args.resample_time == "ts"


def test_register_adds_resample_value():
    p = make_parser()
    args = p.parse_args(["--resample-value", "latency"])
    assert args.resample_value == "latency"


def test_register_default_interval_is_60():
    p = make_parser()
    args = p.parse_args([])
    assert args.resample_interval == 60


def test_register_custom_interval():
    p = make_parser()
    args = p.parse_args(["--resample-interval", "300"])
    assert args.resample_interval == 300


def test_register_default_agg_is_mean():
    p = make_parser()
    args = p.parse_args([])
    assert args.resample_agg == "mean"


def test_register_agg_choices():
    p = make_parser()
    for agg in ("mean", "sum", "min", "max", "count"):
        args = p.parse_args(["--resample-agg", agg])
        assert args.resample_agg == agg


def test_register_group_default_none():
    p = make_parser()
    args = p.parse_args([])
    assert args.resample_group is None


def test_register_group_field():
    p = make_parser()
    args = p.parse_args(["--resample-group", "service"])
    assert args.resample_group == "service"


def test_is_resample_active_true():
    p = make_parser()
    args = p.parse_args(["--resample-time", "ts", "--resample-value", "val"])
    assert is_resample_active(args) is True


def test_is_resample_active_false_no_time():
    p = make_parser()
    args = p.parse_args(["--resample-value", "val"])
    assert is_resample_active(args) is False


def test_is_resample_active_false_no_value():
    p = make_parser()
    args = p.parse_args(["--resample-time", "ts"])
    assert is_resample_active(args) is False


def test_extract_resample_kwargs():
    p = make_parser()
    args = p.parse_args([
        "--resample-time", "ts",
        "--resample-value", "latency",
        "--resample-interval", "120",
        "--resample-agg", "sum",
        "--resample-group", "host",
    ])
    kwargs = extract_resample_kwargs(args)
    assert kwargs["time_field"] == "ts"
    assert kwargs["value_field"] == "latency"
    assert kwargs["interval_seconds"] == 120
    assert kwargs["agg"] == "sum"
    assert kwargs["group_field"] == "host"


def test_validate_resample_args_time_without_value_raises():
    p = make_parser()
    args = p.parse_args(["--resample-time", "ts"])
    with pytest.raises(ValueError, match="--resample-time requires --resample-value"):
        validate_resample_args(args)


def test_validate_resample_args_value_without_time_raises():
    p = make_parser()
    args = p.parse_args(["--resample-value", "val"])
    with pytest.raises(ValueError, match="--resample-value requires --resample-time"):
        validate_resample_args(args)


def test_validate_resample_args_invalid_interval_raises():
    p = make_parser()
    args = p.parse_args([
        "--resample-time", "ts",
        "--resample-value", "val",
        "--resample-interval", "0",
    ])
    with pytest.raises(ValueError, match="positive integer"):
        validate_resample_args(args)


def test_validate_resample_args_valid_passes():
    p = make_parser()
    args = p.parse_args([
        "--resample-time", "ts",
        "--resample-value", "val",
    ])
    validate_resample_args(args)  # should not raise
