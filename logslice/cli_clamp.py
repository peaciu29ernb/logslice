"""CLI helpers for the --clamp feature."""

from argparse import ArgumentParser, Namespace
from typing import Any, Dict, Optional


def register_clamp_args(parser: ArgumentParser) -> None:
    """Add clamp-related arguments to *parser*."""
    parser.add_argument(
        "--clamp-field",
        dest="clamp_fields",
        metavar="FIELD",
        action="append",
        default=[],
        help="Field to clamp (repeatable).",
    )
    parser.add_argument(
        "--clamp-min",
        dest="clamp_min",
        type=float,
        default=None,
        metavar="MIN",
        help="Lower bound for clamping.",
    )
    parser.add_argument(
        "--clamp-max",
        dest="clamp_max",
        type=float,
        default=None,
        metavar="MAX",
        help="Upper bound for clamping.",
    )


def is_clamp_active(args: Namespace) -> bool:
    """Return True when at least one clamp field is specified."""
    return bool(getattr(args, "clamp_fields", None))


def validate_clamp_args(args: Namespace) -> Optional[str]:
    """Return an error string if arguments are invalid, else None."""
    lo = getattr(args, "clamp_min", None)
    hi = getattr(args, "clamp_max", None)
    if lo is not None and hi is not None and lo > hi:
        return f"--clamp-min ({lo}) must not exceed --clamp-max ({hi})"
    if is_clamp_active(args) and lo is None and hi is None:
        return "At least one of --clamp-min or --clamp-max must be provided with --clamp-field"
    return None


def extract_clamp_kwargs(args: Namespace) -> Dict[str, Any]:
    """Extract clamp parameters from parsed *args*."""
    return {
        "fields": getattr(args, "clamp_fields", []),
        "lo": getattr(args, "clamp_min", None),
        "hi": getattr(args, "clamp_max", None),
    }
