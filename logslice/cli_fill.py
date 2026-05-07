"""CLI helpers for the fill feature."""

import argparse
from typing import Any, Dict, List


def register_fill_args(parser: argparse.ArgumentParser) -> None:
    """Add fill-related arguments to *parser*."""
    parser.add_argument(
        "--fill",
        metavar="FIELD",
        dest="fill_fields",
        action="append",
        default=[],
        help="Fill missing values for FIELD (repeatable).",
    )
    parser.add_argument(
        "--fill-default",
        metavar="VALUE",
        dest="fill_default",
        default=None,
        help="Default value used when filling (default: null).",
    )
    parser.add_argument(
        "--fill-forward",
        dest="fill_forward",
        action="store_true",
        default=False,
        help="Carry the last seen value forward instead of using a fixed default.",
    )


def is_fill_active(args: argparse.Namespace) -> bool:
    """Return True if any fill arguments were supplied."""
    return bool(getattr(args, "fill_fields", None))


def extract_fill_kwargs(args: argparse.Namespace) -> Dict[str, Any]:
    """Extract fill keyword arguments from parsed *args*."""
    return {
        "fields": list(args.fill_fields),
        "default": args.fill_default,
        "forward": args.fill_forward,
    }
