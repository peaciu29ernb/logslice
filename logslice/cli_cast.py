"""CLI helpers for the --cast feature."""

import argparse
from typing import Any, Dict

from logslice.cast import parse_cast_args


def register_cast_args(parser: argparse.ArgumentParser) -> None:
    """Add ``--cast`` argument to *parser*.

    Can be supplied multiple times::

        --cast duration:float --cast retries:int --cast active:bool
    """
    parser.add_argument(
        "--cast",
        metavar="FIELD:TYPE",
        action="append",
        default=[],
        dest="cast",
        help=(
            "Cast FIELD to TYPE before output. "
            "TYPE must be one of: int, float, str, bool. "
            "May be repeated."
        ),
    )


def extract_cast_kwargs(args: argparse.Namespace) -> Dict[str, Any]:
    """Return a dict with ``casts`` key ready for :func:`cast_records`.

    Returns an empty dict when no ``--cast`` flags were supplied so callers
    can skip the cast step entirely.
    """
    raw: list = getattr(args, "cast", []) or []
    if not raw:
        return {}
    casts = parse_cast_args(raw)
    return {"casts": casts}


def is_cast_active(args: argparse.Namespace) -> bool:
    """Return True when at least one ``--cast`` flag was provided."""
    return bool(getattr(args, "cast", None))
