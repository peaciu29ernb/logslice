"""CLI argument registration and extraction for the percentile feature."""

from __future__ import annotations

import argparse

_DEFAULT_PERCENTILES = [50.0, 90.0, 95.0, 99.0]


def register_percentile_args(parser: argparse.ArgumentParser) -> None:
    """Add --percentile-field, --percentile, and --percentile-group to parser."""
    parser.add_argument(
        "--percentile-field",
        metavar="FIELD",
        default=None,
        help="Numeric field to compute percentiles over.",
    )
    parser.add_argument(
        "--percentile",
        metavar="P",
        type=float,
        action="append",
        dest="percentiles",
        default=None,
        help="Percentile value to compute (0-100). May be repeated. Defaults: 50 90 95 99.",
    )
    parser.add_argument(
        "--percentile-group",
        metavar="FIELD",
        default=None,
        help="Optional field to group percentile results by.",
    )


def is_percentile_active(args: argparse.Namespace) -> bool:
    """Return True if the percentile feature has been requested."""
    return bool(getattr(args, "percentile_field", None))


def extract_percentile_kwargs(args: argparse.Namespace) -> dict:
    """Extract percentile settings from parsed args."""
    raw = getattr(args, "percentiles", None) or _DEFAULT_PERCENTILES
    percentiles = sorted(set(raw))
    return {
        "field": args.percentile_field,
        "percentiles": percentiles,
        "group_by": getattr(args, "percentile_group", None),
    }


def validate_percentile_args(args: argparse.Namespace) -> list[str]:
    """Return a list of validation error strings, empty if valid."""
    errors = []
    raw = getattr(args, "percentiles", None) or []
    for p in raw:
        if not 0.0 <= p <= 100.0:
            errors.append(f"--percentile value {p} is out of range (0-100).")
    return errors
