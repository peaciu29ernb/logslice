"""Tests for logslice/cli_threshold.py"""

import argparse
import pytest
from logslice.cli_threshold import (
    register_threshold_args,
    is_threshold_active,
    extract_threshold_kwargs,
    validate_threshold_args,
)


def make_parser():
    parser = argparse.ArgumentParser()
    register_threshold_args(parser)
    return parser


def test_register_adds_threshold_arg():
    parser = make_parser()
    args = parser.parse_args(["--threshold", "latency:gt:500"])
    assert args.threshold == "latency:gt:500"

def test_register_adds_invert_flag():
    parser = make_parser()
    args = parser.parse_args(["--threshold-invert"])
    assert args.threshold_invert is True

def test_register_invert_default_false():
    parser = make_parser()
    args = parser.parse_args([])
    assert args.threshold_invert is False

def test_register_adds_flag_arg():
    parser = make_parser()
    args = parser.parse_args(["--threshold-flag", "cpu:gte:90"])
    assert args.threshold_flag == "cpu:gte:90"

def test_register_default_flag_field():
    parser = make_parser()
    args = parser.parse_args([])
    assert args.threshold_flag_field == "threshold_exceeded"

def test_register_custom_flag_field():
    parser = make_parser()
    args = parser.parse_args(["--threshold-flag-field", "alert"])
    assert args.threshold_flag_field == "alert"


def test_is_threshold_active_with_threshold():
    parser = make_parser()
    args = parser.parse_args(["--threshold", "x:gt:1"])
    assert is_threshold_active(args) is True

def test_is_threshold_active_with_flag():
    parser = make_parser()
    args = parser.parse_args(["--threshold-flag", "x:gt:1"])
    assert is_threshold_active(args) is True

def test_is_threshold_active_none():
    parser = make_parser()
    args = parser.parse_args([])
    assert is_threshold_active(args) is False


def test_extract_kwargs_all_fields():
    parser = make_parser()
    args = parser.parse_args([
        "--threshold", "latency:gt:500",
        "--threshold-invert",
        "--threshold-flag", "cpu:gte:90",
        "--threshold-flag-field", "alert",
    ])
    kwargs = extract_threshold_kwargs(args)
    assert kwargs["threshold"] == "latency:gt:500"
    assert kwargs["threshold_invert"] is True
    assert kwargs["threshold_flag"] == "cpu:gte:90"
    assert kwargs["threshold_flag_field"] == "alert"


def test_validate_valid_threshold():
    parser = make_parser()
    args = parser.parse_args(["--threshold", "latency:gt:500"])
    assert validate_threshold_args(args) == []

def test_validate_invalid_threshold_returns_error():
    parser = make_parser()
    args = parser.parse_args(["--threshold", "latency:bad:500"])
    errors = validate_threshold_args(args)
    assert len(errors) == 1
    assert "threshold" in errors[0]

def test_validate_invalid_flag_returns_error():
    parser = make_parser()
    args = parser.parse_args(["--threshold-flag", "cpu:gte"])
    errors = validate_threshold_args(args)
    assert len(errors) == 1

def test_validate_no_args_no_errors():
    parser = make_parser()
    args = parser.parse_args([])
    assert validate_threshold_args(args) == []
