"""Tests for logslice.cli_pivot_time."""

import argparse
import pytest
from logslice.cli_pivot_time import (
    register_pivot_time_args,
    is_pivot_time_active,
    validate_pivot_time_args,
    extract_pivot_time_kwargs,
)


def make_parser():
    p = argparse.ArgumentParser()
    register_pivot_time_args(p)
    return p


def test_register_adds_pivot_time_flag():
    p = make_parser()
    args = p.parse_args(["--pivot-time", "ts"])
    assert args.pivot_time == "ts"


def test_register_adds_pivot_category():
    p = make_parser()
    args = p.parse_args(["--pivot-category", "svc"])
    assert args.pivot_category == "svc"


def test_register_default_interval_is_60():
    p = make_parser()
    args = p.parse_args([])
    assert args.pivot_interval == 60


def test_register_default_agg_is_count():
    p = make_parser()
    args = p.parse_args([])
    assert args.pivot_agg == "count"


def test_register_default_fill_is_zero():
    p = make_parser()
    args = p.parse_args([])
    assert args.pivot_fill == 0.0


def test_is_pivot_time_active_true():
    p = make_parser()
    args = p.parse_args(["--pivot-time", "ts"])
    assert is_pivot_time_active(args) is True


def test_is_pivot_time_active_false():
    p = make_parser()
    args = p.parse_args([])
    assert is_pivot_time_active(args) is False


def test_validate_raises_if_no_category():
    p = make_parser()
    args = p.parse_args(["--pivot-time", "ts"])
    with pytest.raises(ValueError, match="--pivot-category"):
        validate_pivot_time_args(args)


def test_validate_raises_if_interval_zero():
    p = make_parser()
    args = p.parse_args(
        ["--pivot-time", "ts", "--pivot-category", "svc", "--pivot-interval", "0"]
    )
    with pytest.raises(ValueError, match="positive"):
        validate_pivot_time_args(args)


def test_validate_passes_with_valid_args():
    p = make_parser()
    args = p.parse_args(
        ["--pivot-time", "ts", "--pivot-category", "svc"]
    )
    validate_pivot_time_args(args)  # should not raise


def test_extract_kwargs_basic():
    p = make_parser()
    args = p.parse_args(
        ["--pivot-time", "ts", "--pivot-category", "svc", "--pivot-agg", "sum"]
    )
    kwargs = extract_pivot_time_kwargs(args)
    assert kwargs["time_field"] == "ts"
    assert kwargs["category_field"] == "svc"
    assert kwargs["agg"] == "sum"
    assert kwargs["interval_seconds"] == 60


def test_extract_value_field_falls_back_to_time_field():
    p = make_parser()
    args = p.parse_args(["--pivot-time", "ts", "--pivot-category", "svc"])
    kwargs = extract_pivot_time_kwargs(args)
    assert kwargs["value_field"] == "ts"


def test_extract_custom_value_field():
    p = make_parser()
    args = p.parse_args(
        ["--pivot-time", "ts", "--pivot-category", "svc", "--pivot-value", "latency"]
    )
    kwargs = extract_pivot_time_kwargs(args)
    assert kwargs["value_field"] == "latency"
