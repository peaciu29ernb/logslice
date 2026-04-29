"""CLI argument registration and extraction for the mask feature."""

import argparse
from typing import Any, Dict


def register_mask_args(parser: argparse.ArgumentParser) -> None:
    """Add masking-related arguments to an ArgumentParser."""
    parser.add_argument(
        "--mask",
        metavar="FIELD",
        action="append",
        dest="mask_fields",
        default=[],
        help="Field name to partially mask (repeatable).",
    )
    parser.add_argument(
        "--mask-show-first",
        metavar="N",
        type=int,
        default=0,
        help="Number of leading characters to leave visible (default: 0).",
    )
    parser.add_argument(
        "--mask-show-last",
        metavar="N",
        type=int,
        default=0,
        help="Number of trailing characters to leave visible (default: 0).",
    )
    parser.add_argument(
        "--mask-char",
        metavar="CHAR",
        default="*",
        help="Character used for masking (default: '*').",
    )
    parser.add_argument(
        "--mask-pattern",
        metavar="REGEX",
        default=None,
        help="Regex pattern to replace in all string field values.",
    )
    parser.add_argument(
        "--mask-replacement",
        metavar="TEXT",
        default="[MASKED]",
        help="Replacement text for --mask-pattern matches (default: '[MASKED]').",
    )


def is_mask_active(args: argparse.Namespace) -> bool:
    """Return True if any masking option has been specified."""
    return bool(getattr(args, "mask_fields", [])) or bool(getattr(args, "mask_pattern", None))


def extract_mask_kwargs(args: argparse.Namespace) -> Dict[str, Any]:
    """Extract mask-related kwargs from parsed args for mask_records()."""
    return {
        "fields": list(args.mask_fields),
        "pattern": args.mask_pattern,
        "show_first": args.mask_show_first,
        "show_last": args.mask_show_last,
        "char": args.mask_char,
        "replacement": args.mask_replacement,
    }
