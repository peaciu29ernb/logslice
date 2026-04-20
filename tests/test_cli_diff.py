"""Tests for logslice.cli_diff module."""

import argparse
import pytest
from logslice.cli_diff import register_diff_args, extract_diff_kwargs


def make_parser():
    parser = argparse.ArgumentParser()
    register_diff_args(parser)
    return parser


def test_register_adds_diff_key():
    parser = make_parser()
    args = parser.parse_args(["--diff-key", "id"])
    assert args.diff_key == "id"


def test_register_adds_diff_file():
    parser = make_parser()
    args = parser.parse_args(["--diff-file", "other.log"])
    assert args.diff_file == "other.log"


def test_register_diff_ignore_repeatable():
    parser = make_parser()
    args = parser.parse_args(["--diff-ignore", "ts", "--diff-ignore", "host"])
    assert "ts" in args.diff_ignore
    assert "host" in args.diff_ignore


def test_register_diff_only_changed_flag():
    parser = make_parser()
    args = parser.parse_args(["--diff-only-changed"])
    assert args.diff_only_changed is True


def test_diff_only_changed_defaults_false():
    parser = make_parser()
    args = parser.parse_args([])
    assert args.diff_only_changed is False


def test_extract_diff_kwargs_full():
    parser = make_parser()
    args = parser.parse_args([
        "--diff-key", "request_id",
        "--diff-file", "new.log",
        "--diff-ignore", "timestamp",
        "--diff-only-changed",
    ])
    kwargs = extract_diff_kwargs(args)
    assert kwargs["diff_key"] == "request_id"
    assert kwargs["diff_file"] == "new.log"
    assert kwargs["diff_ignore"] == ["timestamp"]
    assert kwargs["diff_only_changed"] is True


def test_extract_diff_kwargs_defaults():
    parser = make_parser()
    args = parser.parse_args([])
    kwargs = extract_diff_kwargs(args)
    assert kwargs["diff_key"] is None
    assert kwargs["diff_file"] is None
    assert kwargs["diff_ignore"] == []
    assert kwargs["diff_only_changed"] is False


def test_extract_diff_kwargs_missing_attrs():
    """extract_diff_kwargs should handle a namespace without diff attrs gracefully."""
    args = argparse.Namespace()
    kwargs = extract_diff_kwargs(args)
    assert kwargs["diff_key"] is None
    assert kwargs["diff_file"] is None
