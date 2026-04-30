"""CLI helpers for the score feature."""
from __future__ import annotations

import argparse
from typing import Any, Dict, List, Optional, Tuple

from logslice.score import parse_score_rules


def register_score_args(parser: argparse.ArgumentParser) -> None:
    """Attach score-related arguments to *parser*."""
    parser.add_argument(
        "--score-rule",
        dest="score_rules",
        metavar="FIELD:PATTERN",
        action="append",
        default=[],
        help=(
            "Score rule in 'field:pattern' form.  Each matching rule adds 1 "
            "to the record's score.  Repeatable."
        ),
    )
    parser.add_argument(
        "--score-field",
        dest="score_field",
        metavar="NAME",
        default="_score",
        help="Field name to write the score into (default: _score).",
    )
    parser.add_argument(
        "--min-score",
        dest="min_score",
        metavar="N",
        type=int,
        default=0,
        help="Only emit records with score >= N (default: 0).",
    )


def is_score_active(args: argparse.Namespace) -> bool:
    """Return True when at least one score rule has been supplied."""
    return bool(getattr(args, "score_rules", None))


def extract_score_kwargs(
    args: argparse.Namespace,
) -> Dict[str, Any]:
    """Return keyword arguments suitable for :func:`score_records`."""
    rules: List[str] = getattr(args, "score_rules", [])
    return {
        "rules": parse_score_rules(rules),
        "field": getattr(args, "score_field", "_score"),
        "min_score": getattr(args, "min_score", 0),
    }
