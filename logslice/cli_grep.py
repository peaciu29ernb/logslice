"""CLI argument registration and extraction for the grep feature."""

import argparse
from typing import Any, Dict, Optional


def register_grep_args(parser: argparse.ArgumentParser) -> None:
    """Add grep-related arguments to an ArgumentParser."""
    parser.add_argument(
        "--grep",
        metavar="PATTERN",
        default=None,
        help="Filter records whose field values match PATTERN (regex).",
    )
    parser.add_argument(
        "--grep-fields",
        metavar="FIELD",
        nargs="+",
        default=None,
        dest="grep_fields",
        help="Restrict grep search to these fields (default: all fields).",
    )
    parser.add_argument(
        "--grep-ignore-case",
        action="store_true",
        default=False,
        dest="grep_ignore_case",
        help="Case-insensitive grep matching.",
    )
    parser.add_argument(
        "--grep-invert",
        action="store_true",
        default=False,
        dest="grep_invert",
        help="Invert grep: keep records that do NOT match.",
    )


def is_grep_active(args: argparse.Namespace) -> bool:
    """Return True if a grep pattern has been specified."""
    return bool(getattr(args, "grep", None))


def extract_grep_kwargs(args: argparse.Namespace) -> Dict[str, Any]:
    """Extract grep kwargs from parsed CLI args."""
    return {
        "pattern": args.grep,
        "fields": getattr(args, "grep_fields", None),
        "ignore_case": getattr(args, "grep_ignore_case", False),
        "invert": getattr(args, "grep_invert", False),
    }
