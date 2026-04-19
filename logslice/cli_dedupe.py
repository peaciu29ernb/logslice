"""CLI argument registration and extraction for deduplication."""

import argparse
from typing import Dict, Any


def register_dedupe_args(parser: argparse.ArgumentParser) -> None:
    """Add deduplication arguments to an ArgumentParser."""
    group = parser.add_argument_group("deduplication")
    group.add_argument(
        "--dedupe",
        metavar="FIELD",
        nargs="+",
        dest="dedupe_fields",
        help="Deduplicate records by these fields.",
    )
    group.add_argument(
        "--dedupe-keep",
        choices=["first", "last"],
        default="first",
        dest="dedupe_keep",
        help="Which occurrence to keep when deduplicating (default: first).",
    )
    group.add_argument(
        "--dedupe-cache",
        type=int,
        default=None,
        metavar="N",
        dest="dedupe_max_seen",
        help="Limit dedup key cache to N entries (LRU). Useful for large streams.",
    )


def extract_dedupe_kwargs(args: argparse.Namespace) -> Dict[str, Any]:
    """
    Extract deduplication kwargs from parsed args.

    Returns an empty dict if deduplication is not requested.
    """
    if not getattr(args, "dedupe_fields", None):
        return {}
    kwargs: Dict[str, Any] = {
        "fields": args.dedupe_fields,
        "keep": args.dedupe_keep,
    }
    if args.dedupe_max_seen is not None:
        kwargs["max_seen"] = args.dedupe_max_seen
    return kwargs
