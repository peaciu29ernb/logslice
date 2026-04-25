"""CLI helpers for the sort feature."""

import argparse
from typing import Any


def register_sort_args(parser: argparse.ArgumentParser) -> None:
    """Attach sort-related arguments to *parser*."""
    parser.add_argument(
        "--sort-by",
        metavar="FIELD",
        action="append",
        dest="sort_by",
        default=None,
        help=(
            "Sort output records by FIELD. "
            "Repeat to sort by multiple fields (leftmost has highest priority)."
        ),
    )
    parser.add_argument(
        "--sort-desc",
        action="store_true",
        default=False,
        help="Sort in descending order instead of ascending.",
    )


def extract_sort_kwargs(args: argparse.Namespace) -> dict[str, Any]:
    """Return a kwargs dict suitable for :func:`logslice.sort.sort_records`."""
    return {
        "fields": args.sort_by or [],
        "reverse": args.sort_desc,
    }


def is_sort_active(args: argparse.Namespace) -> bool:
    """Return True when the user requested sorting."""
    return bool(getattr(args, "sort_by", None))
