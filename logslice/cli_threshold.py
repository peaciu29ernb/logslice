"""CLI argument registration and extraction for threshold filtering/flagging."""

import argparse
from logslice.threshold import OPS, parse_threshold_arg


def register_threshold_args(parser: argparse.ArgumentParser) -> None:
    """Add threshold-related arguments to an argument parser."""
    parser.add_argument(
        "--threshold",
        metavar="FIELD:OP:VALUE",
        dest="threshold",
        default=None,
        help=(
            "Filter records by numeric threshold. "
            f"OP must be one of: {', '.join(OPS)}. "
            "Example: --threshold response_time:gt:500"
        ),
    )
    parser.add_argument(
        "--threshold-invert",
        action="store_true",
        default=False,
        dest="threshold_invert",
        help="Invert the threshold filter (keep records that do NOT match).",
    )
    parser.add_argument(
        "--threshold-flag",
        metavar="FIELD:OP:VALUE",
        dest="threshold_flag",
        default=None,
        help=(
            "Annotate records with a boolean flag instead of filtering. "
            "Example: --threshold-flag latency:gte:1000"
        ),
    )
    parser.add_argument(
        "--threshold-flag-field",
        metavar="FIELD",
        dest="threshold_flag_field",
        default="threshold_exceeded",
        help="Name of the annotation field added by --threshold-flag (default: threshold_exceeded).",
    )


def is_threshold_active(args: argparse.Namespace) -> bool:
    """Return True if any threshold option is set."""
    return bool(getattr(args, "threshold", None) or getattr(args, "threshold_flag", None))


def extract_threshold_kwargs(args: argparse.Namespace) -> dict:
    """Extract threshold configuration from parsed args."""
    return {
        "threshold": getattr(args, "threshold", None),
        "threshold_invert": getattr(args, "threshold_invert", False),
        "threshold_flag": getattr(args, "threshold_flag", None),
        "threshold_flag_field": getattr(args, "threshold_flag_field", "threshold_exceeded"),
    }


def validate_threshold_args(args: argparse.Namespace) -> list:
    """Return a list of validation error strings (empty if valid)."""
    errors = []
    for attr in ("threshold", "threshold_flag"):
        raw = getattr(args, attr, None)
        if raw is not None and parse_threshold_arg(raw) is None:
            errors.append(
                f"--{attr.replace('_', '-')} '{raw}' is invalid. "
                f"Expected FIELD:OP:VALUE where OP in {OPS}."
            )
    return errors
