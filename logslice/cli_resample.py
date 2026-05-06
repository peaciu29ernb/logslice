"""CLI argument registration and extraction for the resample feature."""

import argparse
from typing import Any, Dict

VALID_AGG = {"mean", "sum", "min", "max", "count"}


def register_resample_args(parser: argparse.ArgumentParser) -> None:
    """Add resample-related arguments to an ArgumentParser."""
    parser.add_argument(
        "--resample-time",
        metavar="FIELD",
        help="Field containing parsed datetime objects to bucket by.",
    )
    parser.add_argument(
        "--resample-value",
        metavar="FIELD",
        help="Numeric field to aggregate within each bucket.",
    )
    parser.add_argument(
        "--resample-interval",
        type=int,
        default=60,
        metavar="SECONDS",
        help="Bucket width in seconds (default: 60).",
    )
    parser.add_argument(
        "--resample-agg",
        choices=sorted(VALID_AGG),
        default="mean",
        metavar="AGG",
        help="Aggregation function: mean, sum, min, max, count (default: mean).",
    )
    parser.add_argument(
        "--resample-group",
        metavar="FIELD",
        default=None,
        help="Optional field to group by within each bucket.",
    )


def is_resample_active(args: argparse.Namespace) -> bool:
    """Return True if resample arguments have been supplied."""
    return bool(getattr(args, "resample_time", None) and getattr(args, "resample_value", None))


def extract_resample_kwargs(args: argparse.Namespace) -> Dict[str, Any]:
    """Extract resample keyword arguments from parsed args."""
    return {
        "time_field": args.resample_time,
        "value_field": args.resample_value,
        "interval_seconds": args.resample_interval,
        "agg": args.resample_agg,
        "group_field": args.resample_group,
    }


def validate_resample_args(args: argparse.Namespace) -> None:
    """Raise ValueError if resample arguments are inconsistent."""
    if getattr(args, "resample_time", None) and not getattr(args, "resample_value", None):
        raise ValueError("--resample-time requires --resample-value")
    if getattr(args, "resample_value", None) and not getattr(args, "resample_time", None):
        raise ValueError("--resample-value requires --resample-time")
    interval = getattr(args, "resample_interval", 60)
    if interval <= 0:
        raise ValueError("--resample-interval must be a positive integer")
