"""CLI argument registration and extraction for the diff feature."""

import argparse
from typing import Any


def register_diff_args(parser: argparse.ArgumentParser) -> None:
    """Add diff-related arguments to an argument parser."""
    parser.add_argument(
        "--diff-key",
        metavar="FIELD",
        help="Field to use as the unique key when diffing two log sources.",
    )
    parser.add_argument(
        "--diff-file",
        metavar="FILE",
        help="Second log file to diff against the primary input.",
    )
    parser.add_argument(
        "--diff-ignore",
        metavar="FIELD",
        action="append",
        default=[],
        help="Fields to ignore when comparing records (repeatable).",
    )
    parser.add_argument(
        "--diff-only-changed",
        action="store_true",
        default=False,
        help="Only show added, removed, or changed records (skip unchanged).",
    )


def extract_diff_kwargs(args: argparse.Namespace) -> dict[str, Any]:
    """Extract diff-related kwargs from parsed arguments."""
    return {
        "diff_key": getattr(args, "diff_key", None),
        "diff_file": getattr(args, "diff_file", None),
        "diff_ignore": getattr(args, "diff_ignore", []),
        "diff_only_changed": getattr(args, "diff_only_changed", False),
    }
