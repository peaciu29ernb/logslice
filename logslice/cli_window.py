"""CLI argument registration and extraction for window aggregation."""

import argparse
from typing import Any, Dict


def register_window_args(parser: argparse.ArgumentParser) -> None:
    """Add window-related arguments to an argument parser."""
    parser.add_argument(
        "--window",
        type=int,
        metavar="SECONDS",
        default=None,
        help="Tumbling window size in seconds (e.g. 60 for 1-minute windows).",
    )
    parser.add_argument(
        "--window-step",
        type=int,
        metavar="SECONDS",
        default=None,
        help="Step size in seconds for sliding windows (requires --window).",
    )
    parser.add_argument(
        "--window-field",
        type=str,
        default="time",
        metavar="FIELD",
        help="Field name to use as the timestamp for windowing (default: time).",
    )
    parser.add_argument(
        "--window-count",
        action="store_true",
        default=False,
        help="Print window counts table instead of passing records through.",
    )


def extract_window_kwargs(args: argparse.Namespace) -> Dict[str, Any]:
    """Extract window-related kwargs from parsed args."""
    return {
        "window": getattr(args, "window", None),
        "window_step": getattr(args, "window_step", None),
        "window_field": getattr(args, "window_field", "time"),
        "window_count": getattr(args, "window_count", False),
    }


def is_window_active(kwargs: Dict[str, Any]) -> bool:
    """Return True if windowing has been requested."""
    return kwargs.get("window") is not None
