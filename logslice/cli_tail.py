"""CLI helpers for --tail and --follow options."""

from __future__ import annotations

import argparse
from typing import Any


def register_tail_args(parser: argparse.ArgumentParser) -> None:
    """Add tail/follow arguments to *parser*."""
    group = parser.add_argument_group("tail / follow")
    group.add_argument(
        "-n",
        "--tail",
        metavar="N",
        type=int,
        default=None,
        help="Output only the last N records.",
    )
    group.add_argument(
        "-f",
        "--follow",
        action="store_true",
        default=False,
        help="Follow a file and emit new records as they are appended.",
    )


def extract_tail_kwargs(args: argparse.Namespace) -> dict[str, Any]:
    """Return a dict with 'tail' and 'follow' keys from parsed *args*."""
    return {
        "tail": getattr(args, "tail", None),
        "follow": getattr(args, "follow", False),
    }
