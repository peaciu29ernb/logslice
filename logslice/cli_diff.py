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


def validate_diff_kwargs(kwargs: dict[str, Any]) -> None:
    """Validate diff-related kwargs for logical consistency.

    Raises:
        ValueError: If ``diff_file`` is provided without ``diff_key``, or if
            ``diff_only_changed`` or ``diff_ignore`` are set without ``diff_file``.
    """
    has_file = bool(kwargs.get("diff_file"))
    has_key = bool(kwargs.get("diff_key"))

    if has_file and not has_key:
        raise ValueError("--diff-key is required when --diff-file is specified.")
    if not has_file and has_key:
        raise ValueError("--diff-file is required when --diff-key is specified.")
    if not has_file and kwargs.get("diff_only_changed"):
        raise ValueError("--diff-only-changed requires --diff-file to be specified.")
    if not has_file and kwargs.get("diff_ignore"):
        raise ValueError("--diff-ignore requires --diff-file to be specified.")
