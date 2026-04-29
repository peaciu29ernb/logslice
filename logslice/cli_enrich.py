"""CLI helpers for the --enrich feature."""

from __future__ import annotations

import argparse
from typing import Any, Dict


def register_enrich_args(parser: argparse.ArgumentParser) -> None:
    """Add enrich-related arguments to *parser*."""
    parser.add_argument(
        "--enrich-file",
        metavar="FILE",
        help="CSV or JSON file used as the lookup table for enrichment.",
    )
    parser.add_argument(
        "--enrich-on",
        metavar="FIELD",
        help="Record field whose value is looked up in the enrich file.",
    )
    parser.add_argument(
        "--enrich-key",
        metavar="FIELD",
        default="key",
        help="Column in the enrich file that contains lookup keys (default: key).",
    )
    parser.add_argument(
        "--enrich-value",
        metavar="FIELD",
        default="value",
        help="Column in the enrich file that contains lookup values (default: value).",
    )
    parser.add_argument(
        "--enrich-dest",
        metavar="FIELD",
        help="Destination field written to each record (defaults to --enrich-on + '_enriched').",
    )
    parser.add_argument(
        "--enrich-default",
        metavar="VALUE",
        default=None,
        help="Value to use when no mapping entry is found.",
    )
    parser.add_argument(
        "--enrich-skip-missing",
        action="store_true",
        default=False,
        help="Drop records that have no mapping hit instead of emitting them.",
    )


def is_enrich_active(args: argparse.Namespace) -> bool:
    """Return True when enough enrich arguments are present to run enrichment."""
    return bool(getattr(args, "enrich_file", None) and getattr(args, "enrich_on", None))


def extract_enrich_kwargs(args: argparse.Namespace) -> Dict[str, Any]:
    """Extract enrich settings from parsed args into a kwargs dict."""
    lookup_field: str = args.enrich_on
    dest_field: str = getattr(args, "enrich_dest", None) or f"{lookup_field}_enriched"
    return {
        "enrich_file": args.enrich_file,
        "lookup_field": lookup_field,
        "key_field": args.enrich_key,
        "value_field": args.enrich_value,
        "dest_field": dest_field,
        "default": args.enrich_default,
        "skip_missing": args.enrich_skip_missing,
    }
