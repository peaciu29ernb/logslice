"""Tests for logslice.cli_enrich."""

from __future__ import annotations

import argparse

import pytest

from logslice.cli_enrich import (
    extract_enrich_kwargs,
    is_enrich_active,
    register_enrich_args,
)


def make_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser()
    register_enrich_args(p)
    return p


def test_register_adds_enrich_file():
    p = make_parser()
    args = p.parse_args(["--enrich-file", "map.csv"])
    assert args.enrich_file == "map.csv"


def test_register_adds_enrich_on():
    p = make_parser()
    args = p.parse_args(["--enrich-on", "status"])
    assert args.enrich_on == "status"


def test_register_default_key_and_value():
    p = make_parser()
    args = p.parse_args([])
    assert args.enrich_key == "key"
    assert args.enrich_value == "value"


def test_register_skip_missing_default_false():
    p = make_parser()
    args = p.parse_args([])
    assert args.enrich_skip_missing is False


def test_register_skip_missing_flag():
    p = make_parser()
    args = p.parse_args(["--enrich-skip-missing"])
    assert args.enrich_skip_missing is True


def test_is_enrich_active_true():
    p = make_parser()
    args = p.parse_args(["--enrich-file", "f.csv", "--enrich-on", "status"])
    assert is_enrich_active(args) is True


def test_is_enrich_active_missing_file():
    p = make_parser()
    args = p.parse_args(["--enrich-on", "status"])
    assert is_enrich_active(args) is False


def test_is_enrich_active_missing_on():
    p = make_parser()
    args = p.parse_args(["--enrich-file", "f.csv"])
    assert is_enrich_active(args) is False


def test_extract_enrich_kwargs_dest_default():
    p = make_parser()
    args = p.parse_args(["--enrich-file", "f.csv", "--enrich-on", "status"])
    kwargs = extract_enrich_kwargs(args)
    assert kwargs["dest_field"] == "status_enriched"


def test_extract_enrich_kwargs_explicit_dest():
    p = make_parser()
    args = p.parse_args(["--enrich-file", "f.csv", "--enrich-on", "status", "--enrich-dest", "label"])
    kwargs = extract_enrich_kwargs(args)
    assert kwargs["dest_field"] == "label"


def test_extract_enrich_kwargs_all_fields():
    p = make_parser()
    args = p.parse_args([
        "--enrich-file", "map.json",
        "--enrich-on", "code",
        "--enrich-key", "id",
        "--enrich-value", "name",
        "--enrich-default", "n/a",
        "--enrich-skip-missing",
    ])
    kwargs = extract_enrich_kwargs(args)
    assert kwargs["enrich_file"] == "map.json"
    assert kwargs["lookup_field"] == "code"
    assert kwargs["key_field"] == "id"
    assert kwargs["value_field"] == "name"
    assert kwargs["default"] == "n/a"
    assert kwargs["skip_missing"] is True
