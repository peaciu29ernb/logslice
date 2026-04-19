"""CLI helpers for parsing transform arguments passed to logslice."""

from typing import Dict, List, Optional, Tuple


def parse_rename_args(args: List[str]) -> Dict[str, str]:
    """Parse a list of 'old=new' strings into a rename mapping.

    Example:
        ['msg=message', 'ts=timestamp'] -> {'msg': 'message', 'ts': 'timestamp'}
    """
    mapping = {}
    for arg in args:
        if "=" not in arg:
            raise ValueError(f"Invalid rename spec (expected old=new): {arg!r}")
        old, new = arg.split("=", 1)
        old, new = old.strip(), new.strip()
        if not old or not new:
            raise ValueError(f"Rename spec has empty key or value: {arg!r}")
        mapping[old] = new
    return mapping


def parse_field_list(args: List[str]) -> List[str]:
    """Parse a comma-separated or repeated list of field names.

    Accepts both ['a,b', 'c'] and ['a', 'b', 'c'] styles.
    """
    fields = []
    for arg in args:
        for part in arg.split(","):
            part = part.strip()
            if part:
                fields.append(part)
    return fields


def register_transform_args(parser) -> None:
    """Register --rename, --drop, --keep arguments on an argparse parser."""
    parser.add_argument(
        "--rename",
        metavar="OLD=NEW",
        action="append",
        default=[],
        help="Rename a field, e.g. --rename msg=message",
    )
    parser.add_argument(
        "--drop",
        metavar="FIELD",
        action="append",
        default=[],
        help="Drop a field from output, e.g. --drop ts",
    )
    parser.add_argument(
        "--keep",
        metavar="FIELD",
        action="append",
        default=[],
        help="Keep only specified fields, e.g. --keep level,msg",
    )


def extract_transform_kwargs(args) -> dict:
    """Extract transform keyword arguments from parsed CLI args."""
    kwargs = {}
    if args.rename:
        kwargs["rename"] = parse_rename_args(args.rename)
    if args.drop:
        kwargs["drop"] = parse_field_list(args.drop)
    if args.keep:
        kwargs["keep"] = parse_field_list(args.keep)
    return kwargs
