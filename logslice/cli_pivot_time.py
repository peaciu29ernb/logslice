"""CLI helpers for the pivot_time feature."""

import argparse
from typing import Any, Dict

VALID_AGGS = ("count", "sum", "min", "max", "mean")


def register_pivot_time_args(parser: argparse.ArgumentParser) -> None:
    """Add pivot-time arguments to an ArgumentParser."""
    parser.add_argument(
        "--pivot-time",
        metavar="FIELD",
        default=None,
        help="Time field to use as row axis for pivot table.",
    )
    parser.add_argument(
        "--pivot-category",
        metavar="FIELD",
        default=None,
        help="Field whose values become column headers.",
    )
    parser.add_argument(
        "--pivot-value",
        metavar="FIELD",
        default=None,
        help="Numeric field to aggregate (default: count records).",
    )
    parser.add_argument(
        "--pivot-agg",
        choices=VALID_AGGS,
        default="count",
        help="Aggregation function (default: count).",
    )
    parser.add_argument(
        "--pivot-interval",
        type=int,
        default=60,
        metavar="SECONDS",
        help="Bucket width in seconds (default: 60).",
    )
    parser.add_argument(
        "--pivot-fill",
        type=float,
        default=0.0,
        metavar="VALUE",
        help="Fill value for empty cells (default: 0.0).",
    )


def is_pivot_time_active(args: argparse.Namespace) -> bool:
    """Return True if pivot-time mode has been requested."""
    return bool(getattr(args, "pivot_time", None))


def validate_pivot_time_args(args: argparse.Namespace) -> None:
    """Raise ValueError if required pivot-time args are missing."""
    if not getattr(args, "pivot_category", None):
        raise ValueError("--pivot-category is required when --pivot-time is set.")
    if args.pivot_interval <= 0:
        raise ValueError("--pivot-interval must be a positive integer.")


def extract_pivot_time_kwargs(args: argparse.Namespace) -> Dict[str, Any]:
    """Extract pivot-time keyword arguments from parsed args."""
    return {
        "time_field": args.pivot_time,
        "category_field": args.pivot_category,
        "value_field": args.pivot_value or args.pivot_time,
        "interval_seconds": args.pivot_interval,
        "agg": args.pivot_agg,
        "fill": args.pivot_fill,
    }
