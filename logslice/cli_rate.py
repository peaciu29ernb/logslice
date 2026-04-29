"""CLI helpers for the rate-limiting feature."""

from __future__ import annotations

import argparse


def register_rate_args(parser: argparse.ArgumentParser) -> None:
    """Add rate-limiting arguments to an argument parser."""
    parser.add_argument(
        "--rate-limit",
        type=int,
        default=None,
        metavar="N",
        help="Emit at most N records per time bucket (requires --rate-interval).",
    )
    parser.add_argument(
        "--rate-interval",
        type=int,
        default=1,
        metavar="SECONDS",
        help="Bucket size in seconds for rate limiting (default: 1).",
    )
    parser.add_argument(
        "--rate-field",
        default="timestamp",
        metavar="FIELD",
        help="Field to use as the timestamp for rate limiting (default: timestamp).",
    )


def is_rate_active(args: argparse.Namespace) -> bool:
    """Return True if rate limiting has been requested."""
    return getattr(args, "rate_limit", None) is not None


def extract_rate_kwargs(args: argparse.Namespace) -> dict:
    """Extract rate-limiting kwargs from parsed arguments."""
    return {
        "max_per_bucket": args.rate_limit,
        "interval": args.rate_interval,
        "time_field": args.rate_field,
    }


def validate_rate_args(args: argparse.Namespace) -> list[str]:
    """Return a list of validation error messages for rate args."""
    errors = []
    if getattr(args, "rate_limit", None) is not None and args.rate_limit <= 0:
        errors.append("--rate-limit must be a positive integer")
    if getattr(args, "rate_interval", 1) <= 0:
        errors.append("--rate-interval must be a positive integer")
    return errors
