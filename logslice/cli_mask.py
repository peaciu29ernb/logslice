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


def validate_mask_args(args: argparse.Namespace) -> None:
    """Validate mask-related arguments, raising ArgumentTypeError on invalid input.

    Checks:
    - ``--mask-show-first`` and ``--mask-show-last`` must be non-negative.
    - ``--mask-char`` must be exactly one character.
    - ``--mask-replacement`` is only meaningful when ``--mask-pattern`` is set.
    """
    if args.mask_show_first < 0:
        raise argparse.ArgumentTypeError("--mask-show-first must be a non-negative integer.")
    if args.mask_show_last < 0:
        raise argparse.ArgumentTypeError("--mask-show-last must be a non-negative integer.")
    if len(args.mask_char) != 1:
        raise argparse.ArgumentTypeError("--mask-char must be exactly one character.")
    if args.mask_replacement != "[MASKED]" and not args.mask_pattern:
        raise argparse.ArgumentTypeError("--mask-replacement requires --mask-pattern to be set.")


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
