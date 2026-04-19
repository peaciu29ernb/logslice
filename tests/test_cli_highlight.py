import argparse
import pytest
from logslice.cli_highlight import (
    register_highlight_args,
    resolve_color_flag,
    extract_highlight_kwargs,
)


def make_parser():
    parser = argparse.ArgumentParser()
    register_highlight_args(parser)
    return parser


def test_register_adds_color_flag():
    parser = make_parser()
    args = parser.parse_args(["--color"])
    assert args.color is True


def test_register_adds_no_color_flag():
    parser = make_parser()
    args = parser.parse_args(["--no-color"])
    assert args.no_color is True


def test_resolve_color_no_flags():
    parser = make_parser()
    args = parser.parse_args([])
    assert resolve_color_flag(args) is None


def test_resolve_color_force_true():
    parser = make_parser()
    args = parser.parse_args(["--color"])
    assert resolve_color_flag(args) is True


def test_resolve_color_force_false():
    parser = make_parser()
    args = parser.parse_args(["--no-color"])
    assert resolve_color_flag(args) is False


def test_no_color_takes_precedence():
    ns = argparse.Namespace(color=True, no_color=True)
    assert resolve_color_flag(ns) is False


def test_extract_highlight_kwargs_auto():
    parser = make_parser()
    args = parser.parse_args([])
    kwargs = extract_highlight_kwargs(args)
    assert kwargs == {"force_color": None}


def test_extract_highlight_kwargs_forced():
    parser = make_parser()
    args = parser.parse_args(["--color"])
    kwargs = extract_highlight_kwargs(args)
    assert kwargs == {"force_color": True}
