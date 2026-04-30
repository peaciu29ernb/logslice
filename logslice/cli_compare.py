"""CLI helpers for the compare feature."""

import argparse
from typing import Optional


def register_compare_args(parser: argparse.ArgumentParser) -> None:
    """Add compare-related arguments to *parser*."""
    parser.add_argument(
        "--compare-file",
        metavar="FILE",
        default=None,
        help="Path to the second log file to compare against the primary input.",
    )
    parser.add_argument(
        "--compare-key",
        metavar="FIELD",
        default=None,
        help="Field used to match records between the two files.",
    )
    parser.add_argument(
        "--compare-fields",
        metavar="FIELD",
        nargs="+",
        default=None,
        help="Restrict comparison to these fields (default: all fields).",
    )
    parser.add_argument(
        "--compare-label-left",
        metavar="LABEL",
        default="left",
        help="Label for the primary (left) input in the output table.",
    )
    parser.add_argument(
        "--compare-label-right",
        metavar="LABEL",
        default="right",
        help="Label for the secondary (right) input in the output table.",
    )


def is_compare_active(args: argparse.Namespace) -> bool:
    """Return True when compare mode has been requested."""
    return bool(getattr(args, "compare_file", None) and getattr(args, "compare_key", None))


def extract_compare_kwargs(args: argparse.Namespace) -> dict:
    """Return a dict of kwargs suitable for *compare_records*."""
    return {
        "key_field": args.compare_key,
        "fields": args.compare_fields or None,
        "label_left": args.compare_label_left,
        "label_right": args.compare_label_right,
    }


def validate_compare_args(args: argparse.Namespace) -> Optional[str]:
    """Return an error string if the compare arguments are inconsistent."""
    if getattr(args, "compare_file", None) and not getattr(args, "compare_key", None):
        return "--compare-key is required when --compare-file is specified"
    if getattr(args, "compare_key", None) and not getattr(args, "compare_file", None):
        return "--compare-file is required when --compare-key is specified"
    return None
