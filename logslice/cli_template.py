"""CLI helpers for template-based output formatting."""

import argparse
from typing import Any, Dict, Optional

from logslice.template import validate_template


def register_template_args(parser: argparse.ArgumentParser) -> None:
    """Add template-related arguments to an argument parser.

    Args:
        parser: The argparse.ArgumentParser to extend.
    """
    parser.add_argument(
        "--template",
        metavar="TMPL",
        default=None,
        help=(
            "Output each record using a Python format string. "
            "Field names in curly braces are replaced with record values. "
            "Example: --template '{timestamp} [{level}] {message}'"
        ),
    )
    parser.add_argument(
        "--template-field",
        metavar="FIELD",
        default="_rendered",
        help=(
            "When --template is combined with structured output, store the "
            "rendered result in this field name (default: _rendered)."
        ),
    )


def extract_template_kwargs(args: argparse.Namespace) -> Dict[str, Any]:
    """Extract template settings from parsed CLI arguments.

    Returns:
        A dict with keys 'template' and 'dest_field' (or empty if not active).
    """
    template = getattr(args, "template", None)
    dest_field = getattr(args, "template_field", "_rendered")
    return {"template": template, "dest_field": dest_field}


def is_template_active(args: argparse.Namespace) -> bool:
    """Return True if a template has been specified."""
    return bool(getattr(args, "template", None))


def validate_template_arg(args: argparse.Namespace) -> Optional[str]:
    """Validate the --template argument if present.

    Returns:
        An error message string if invalid, or None if valid / not set.
    """
    template = getattr(args, "template", None)
    if not template:
        return None
    return validate_template(template)
