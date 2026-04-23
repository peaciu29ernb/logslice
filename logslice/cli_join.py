"""CLI argument registration and extraction for the join feature."""

import argparse
from typing import Any, Dict


def register_join_args(parser: argparse.ArgumentParser) -> None:
    """Add join-related arguments to an argument parser."""
    parser.add_argument(
        "--join-file",
        metavar="FILE",
        default=None,
        help="Path to a second log file to join against the primary input.",
    )
    parser.add_argument(
        "--join-key",
        metavar="FIELD",
        default=None,
        help="Field name to use as the join key in both streams.",
    )
    parser.add_argument(
        "--join-how",
        choices=["inner", "left"],
        default="inner",
        help="Join strategy: 'inner' keeps only matched records, "
             "'left' keeps all primary records (default: inner).",
    )
    parser.add_argument(
        "--join-prefix",
        metavar="PREFIX",
        default="right_",
        help="Prefix applied to field names from the joined file (default: right_).",
    )


def extract_join_kwargs(args: argparse.Namespace) -> Dict[str, Any]:
    """Extract join-related options from parsed arguments.

    Returns an empty dict when no join file is specified.
    """
    if not getattr(args, "join_file", None):
        return {}
    if not getattr(args, "join_key", None):
        raise ValueError("--join-key is required when --join-file is provided")
    return {
        "join_file": args.join_file,
        "key": args.join_key,
        "how": args.join_how,
        "prefix": args.join_prefix,
    }
