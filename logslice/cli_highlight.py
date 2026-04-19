"""CLI argument registration for highlight/color output options."""
import argparse
from typing import Optional


def register_highlight_args(parser: argparse.ArgumentParser) -> None:
    group = parser.add_argument_group("output color")
    group.add_argument(
        "--color",
        dest="color",
        action="store_true",
        default=None,
        help="Force colored output",
    )
    group.add_argument(
        "--no-color",
        dest="no_color",
        action="store_true",
        default=False,
        help="Disable colored output",
    )


def resolve_color_flag(args: argparse.Namespace) -> Optional[bool]:
    """Return True/False to force color, or None to auto-detect."""
    if getattr(args, "no_color", False):
        return False
    if getattr(args, "color", None):
        return True
    return None


def extract_highlight_kwargs(args: argparse.Namespace) -> dict:
    force_color = resolve_color_flag(args)
    return {"force_color": force_color}
