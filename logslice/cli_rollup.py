"""cli_rollup.py — argument registration and extraction for the rollup feature."""
from __future__ import annotations

import argparse
from typing import Any, Dict

_DEFAULT_OPS = "sum,count,min,max,avg"


def register_rollup_args(parser: argparse.ArgumentParser) -> None:
    """Add rollup-related arguments to *parser*."""
    g = parser.add_argument_group("rollup")
    g.add_argument(
        "--rollup-field",
        metavar="FIELD",
        help="Numeric field to aggregate.",
    )
    g.add_argument(
        "--rollup-group",
        metavar="FIELD",
        default=None,
        help="Optional field to group by within each time bucket.",
    )
    g.add_argument(
        "--rollup-time-field",
        metavar="FIELD",
        default="timestamp",
        help="Field containing the record timestamp (default: timestamp).",
    )
    g.add_argument(
        "--rollup-interval",
        metavar="SECONDS",
        type=int,
        default=60,
        help="Bucket width in seconds (default: 60).",
    )
    g.add_argument(
        "--rollup-ops",
        metavar="OPS",
        default=_DEFAULT_OPS,
        help=f"Comma-separated operations: sum,count,min,max,avg (default: {_DEFAULT_OPS}).",
    )


def is_rollup_active(args: argparse.Namespace) -> bool:
    return bool(getattr(args, "rollup_field", None))


def extract_rollup_kwargs(args: argparse.Namespace) -> Dict[str, Any]:
    ops = tuple(op.strip() for op in args.rollup_ops.split(",") if op.strip())
    return {
        "value_field": args.rollup_field,
        "group_field": args.rollup_group,
        "time_field": args.rollup_time_field,
        "interval_seconds": args.rollup_interval,
        "ops": ops,
    }


def validate_rollup_args(args: argparse.Namespace) -> None:
    if not is_rollup_active(args):
        return
    if args.rollup_interval <= 0:
        raise ValueError("--rollup-interval must be a positive integer.")
    valid_ops = {"sum", "count", "min", "max", "avg"}
    for op in args.rollup_ops.split(","):
        op = op.strip()
        if op and op not in valid_ops:
            raise ValueError(f"Unknown rollup op '{op}'. Choose from: {', '.join(sorted(valid_ops))}.")
