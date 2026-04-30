"""cli_top.py — argument registration and extraction for the --top feature."""

from __future__ import annotations

import argparse


def register_top_args(parser: argparse.ArgumentParser) -> None:
    """Add --top-field, --top-n, and --top-asc flags to *parser*."""
    parser.add_argument(
        "--top-field",
        metavar="FIELD",
        default=None,
        help="Rank records by this numeric field and keep the top N.",
    )
    parser.add_argument(
        "--top-n",
        metavar="N",
        type=int,
        default=10,
        help="Number of top records to keep (default: 10).",
    )
    parser.add_argument(
        "--top-asc",
        action="store_true",
        default=False,
        help="Return the lowest N values instead of the highest.",
    )


def is_top_active(args: argparse.Namespace) -> bool:
    """Return True when the top-N feature should be applied."""
    return bool(getattr(args, "top_field", None))


def extract_top_kwargs(args: argparse.Namespace) -> dict:
    """Extract top-N parameters from parsed *args* as a kwargs dict."""
    return {
        "field": args.top_field,
        "n": args.top_n,
        "ascending": args.top_asc,
    }


def validate_top_args(args: argparse.Namespace) -> list[str]:
    """Return a list of validation error messages (empty when valid)."""
    errors: list[str] = []
    if is_top_active(args):
        if args.top_n <= 0:
            errors.append("--top-n must be a positive integer.")
    return errors
