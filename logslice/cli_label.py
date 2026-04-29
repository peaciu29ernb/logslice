"""CLI integration for the label feature."""

from __future__ import annotations

import argparse
from typing import Any, Dict, List, Optional

from logslice.label import Rule, parse_label_rule


def register_label_args(parser: argparse.ArgumentParser) -> None:
    """Add label-related arguments to *parser*."""
    parser.add_argument(
        "--label-rule",
        metavar="FIELD:OP:VALUE=LABEL",
        dest="label_rules",
        action="append",
        default=[],
        help=(
            "Labelling rule in the form field:op:value=label. "
            "Supported ops: eq, neq, contains, startswith, endswith, regex, gt, lt, gte, lte. "
            "May be repeated."
        ),
    )
    parser.add_argument(
        "--label-dest",
        metavar="FIELD",
        default="label",
        help="Destination field name for the assigned label (default: label).",
    )
    parser.add_argument(
        "--label-default",
        metavar="VALUE",
        default=None,
        help="Default label when no rule matches.",
    )
    parser.add_argument(
        "--label-multi",
        action="store_true",
        default=False,
        help="Collect all matching labels joined by '|' instead of stopping at first match.",
    )


def is_label_active(args: argparse.Namespace) -> bool:
    """Return True if any label rules were supplied."""
    return bool(getattr(args, "label_rules", []))


def extract_label_kwargs(args: argparse.Namespace) -> Dict[str, Any]:
    """Parse and validate label arguments, returning kwargs for *label_records*."""
    raw_rules: List[str] = getattr(args, "label_rules", [])
    rules: List[Rule] = []
    for spec in raw_rules:
        parsed = parse_label_rule(spec)
        if parsed is None:
            raise ValueError(
                f"Invalid --label-rule {spec!r}. "
                "Expected format: field:op:value=label"
            )
        rules.append(parsed)
    return {
        "rules": rules,
        "dest": args.label_dest,
        "default": args.label_default,
        "multi": args.label_multi,
    }


def describe_label(rules: List[Rule]) -> str:
    """Return a human-readable summary of the active label rules."""
    if not rules:
        return "no label rules"
    parts = [f"{f}:{op}:{val} -> {lbl}" for f, op, val, lbl in rules]
    return "label rules: " + "; ".join(parts)
