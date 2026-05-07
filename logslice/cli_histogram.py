"""CLI helpers for the histogram feature."""

import argparse
from typing import Optional


def register_histogram_args(parser: argparse.ArgumentParser) -> None:
    """Add histogram-related arguments to an ArgumentParser."""
    parser.add_argument(
        "--histogram",
        metavar="FIELD",
        dest="histogram_field",
        default=None,
        help="Compute histogram over numeric values of FIELD.",
    )
    parser.add_argument(
        "--histogram-bins",
        metavar="N",
        dest="histogram_bins",
        type=int,
        default=10,
        help="Number of bins (default: 10).",
    )
    parser.add_argument(
        "--histogram-min",
        metavar="MIN",
        dest="histogram_min",
        type=float,
        default=None,
        help="Minimum value for the first bin.",
    )
    parser.add_argument(
        "--histogram-max",
        metavar="MAX",
        dest="histogram_max",
        type=float,
        default=None,
        help="Maximum value for the last bin.",
    )


def is_histogram_active(args: argparse.Namespace) -> bool:
    """Return True if histogram mode was requested."""
    return bool(getattr(args, "histogram_field", None))


def extract_histogram_kwargs(args: argparse.Namespace) -> dict:
    """Extract histogram kwargs from parsed args."""
    return {
        "field": args.histogram_field,
        "bins": args.histogram_bins,
        "min_val": args.histogram_min,
        "max_val": args.histogram_max,
    }


def validate_histogram_args(args: argparse.Namespace) -> Optional[str]:
    """Return an error message string if args are invalid, else None."""
    if getattr(args, "histogram_bins", 10) < 1:
        return "--histogram-bins must be at least 1"
    min_val = getattr(args, "histogram_min", None)
    max_val = getattr(args, "histogram_max", None)
    if min_val is not None and max_val is not None and min_val >= max_val:
        return "--histogram-min must be less than --histogram-max"
    return None
