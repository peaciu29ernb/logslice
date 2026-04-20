"""CLI argument registration and extraction for redact/mask options."""

import argparse
from typing import Any, Dict

from logslice.redact import REDACTED_PLACEHOLDER


def register_redact_args(parser: argparse.ArgumentParser) -> None:
    """Add redaction-related arguments to an argument parser."""
    parser.add_argument(
        "--redact",
        metavar="FIELD",
        action="append",
        default=[],
        help="Redact the value of FIELD, replacing it with a placeholder. "
             "May be specified multiple times.",
    )
    parser.add_argument(
        "--mask-field",
        metavar="FIELD",
        default=None,
        help="Field whose value should be partially masked using --mask-pattern.",
    )
    parser.add_argument(
        "--mask-pattern",
        metavar="REGEX",
        default=None,
        help="Regular expression to match within --mask-field value for masking.",
    )
    parser.add_argument(
        "--mask-replacement",
        metavar="TEXT",
        default=REDACTED_PLACEHOLDER,
        help="Replacement text for masked pattern matches (default: %(default)s).",
    )


def extract_redact_kwargs(args: argparse.Namespace) -> Dict[str, Any]:
    """Extract redaction kwargs from parsed CLI arguments."""
    return {
        "redact": args.redact or [],
        "mask_field": args.mask_field,
        "mask_pattern": args.mask_pattern,
        "mask_replacement": args.mask_replacement,
    }
