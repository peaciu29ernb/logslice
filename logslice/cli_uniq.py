"""CLI helpers for the --uniq feature."""

import argparse
from typing import List


def register_uniq_args(parser: argparse.ArgumentParser) -> None:
    """Add --uniq and related flags to *parser*."""
    parser.add_argument(
        "--uniq",
        metavar="FIELD",
        dest="uniq_fields",
        action="append",
        default=[],
        help=(
            "Suppress consecutive records with the same value for FIELD. "
            "Repeat to compare multiple fields."
        ),
    )
    parser.add_argument(
        "--uniq-count",
        dest="uniq_count",
        action="store_true",
        default=False,
        help="Add a '_count' field with the number of collapsed consecutive duplicates.",
    )
    parser.add_argument(
        "--uniq-count-field",
        dest="uniq_count_field",
        default="_count",
        metavar="FIELD",
        help="Name of the count field added by --uniq-count (default: '_count').",
    )


def is_uniq_active(args: argparse.Namespace) -> bool:
    return bool(getattr(args, "uniq_fields", None))


def extract_uniq_kwargs(args: argparse.Namespace) -> dict:
    return {
        "fields": args.uniq_fields,
        "count": args.uniq_count,
        "count_field": args.uniq_count_field,
    }
