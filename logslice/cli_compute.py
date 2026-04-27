"""CLI helpers for the --compute feature."""

from __future__ import annotations

import argparse
from typing import Any, Dict, List, Optional, Tuple

from logslice.compute import parse_compute_arg


def register_compute_args(parser: argparse.ArgumentParser) -> None:
    """Add --compute flag to an argument parser.

    Example usage::

        --compute rate=bytes/duration --compute total=count+extra
    """
    parser.add_argument(
        "--compute",
        metavar="DEST=EXPR",
        action="append",
        default=[],
        help=(
            "Add a computed field. EXPR may be 'field OP field' or "
            "'field OP literal' where OP is one of +, -, *, /, %%."
        ),
    )


def extract_compute_kwargs(
    args: argparse.Namespace,
) -> Dict[str, Any]:
    """Return kwargs suitable for passing to compute_records."""
    assignments = _parse_compute_list(getattr(args, "compute", []) or [])
    return {"assignments": assignments}


def _parse_compute_list(
    raw: List[str],
) -> List[Tuple[str, str]]:
    """Parse a list of 'dest=expr' strings into (dest, expr) tuples.

    Silently skips malformed entries.
    """
    result = []
    for item in raw:
        parsed = parse_compute_arg(item)
        if parsed is not None:
            result.append(parsed)
    return result


def is_compute_active(args: argparse.Namespace) -> bool:
    """Return True when at least one valid --compute argument was given."""
    raw = getattr(args, "compute", None) or []
    return any(parse_compute_arg(item) is not None for item in raw)


def describe_compute(assignments: List[Tuple[str, str]]) -> Optional[str]:
    """Return a human-readable summary of the compute assignments."""
    if not assignments:
        return None
    parts = [f"{dest}={expr}" for dest, expr in assignments]
    return "compute: " + ", ".join(parts)
