"""CLI helpers for the countif feature."""

import argparse
from typing import Dict, List, Optional, Tuple

from logslice.countif import parse_countif_rule


def register_countif_args(parser: argparse.ArgumentParser) -> None:
    """Add countif-related arguments to an argument parser."""
    parser.add_argument(
        "--countif",
        dest="countif_rules",
        metavar="FIELD:OP:VALUE",
        action="append",
        default=[],
        help=(
            "Count records where field satisfies condition. "
            "OP is one of: eq, ne, gt, lt, gte, lte, re. "
            "Repeatable; all rules must match."
        ),
    )
    parser.add_argument(
        "--countif-group",
        dest="countif_group",
        metavar="FIELD",
        default=None,
        help="Group countif results by this field.",
    )


def is_countif_active(args: argparse.Namespace) -> bool:
    """Return True if any countif rules are specified."""
    return bool(getattr(args, "countif_rules", None))


def extract_countif_kwargs(args: argparse.Namespace) -> Optional[Dict]:
    """Parse and validate countif args; return kwargs dict or None on error."""
    raw_rules = getattr(args, "countif_rules", [])
    if not raw_rules:
        return None

    parsed: List[Tuple[str, str, str]] = []
    for rule in raw_rules:
        result = parse_countif_rule(rule)
        if result is None:
            return None
        parsed.append(result)

    return {
        "rules": parsed,
        "group_by": getattr(args, "countif_group", None),
    }


def validate_countif_args(args: argparse.Namespace) -> List[str]:
    """Return a list of validation error messages (empty if valid)."""
    errors = []
    for rule in getattr(args, "countif_rules", []):
        if parse_countif_rule(rule) is None:
            errors.append(
                f"Invalid --countif rule {rule!r}. "
                "Expected format: FIELD:OP:VALUE where OP is eq/ne/gt/lt/gte/lte/re."
            )
    return errors
