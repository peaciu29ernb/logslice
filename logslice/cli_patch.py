"""cli_patch.py — CLI helpers for the patch feature."""

import argparse
from typing import Any, Dict, List, Optional, Tuple

from logslice.patch import DELETE, DEFAULT, SET, parse_patch_arg


def register_patch_args(parser: argparse.ArgumentParser) -> None:
    """Add --patch / --patch-delete / --patch-default flags to *parser*."""
    parser.add_argument(
        "--patch",
        metavar="FIELD=VALUE",
        action="append",
        default=[],
        dest="patch_set",
        help="Set FIELD to VALUE on every record (e.g. --patch env=prod).",
    )
    parser.add_argument(
        "--patch-delete",
        metavar="FIELD",
        action="append",
        default=[],
        dest="patch_delete",
        help="Remove FIELD from every record.",
    )
    parser.add_argument(
      "--patch-default",
        metavar="FIELD=VALUE",
        action="append",
        default=[],
        dest="patch_default",
        help="Set FIELD=VALUE only when the field is absent or None.",
    )


def is_patch_active(args: argparse.Namespace) -> bool:
    """Return True when at least one patch operation was requested."""
    return bool(
        getattr(args, "patch_set", [])
        or getattr(args, "patch_delete", [])
        or getattr(args, "patch_default", [])
    )


def extract_patch_kwargs(
    args: argparse.Namespace,
) -> Dict[str, Any]:
    """Build the *ops* list from parsed CLI arguments."""
    ops: List[Tuple[str, str, Any]] = []

    for raw in getattr(args, "patch_set", []):
        parsed = parse_patch_arg(raw)
        if parsed:
            ops.append(parsed)

    for field in getattr(args, "patch_delete", []):
        ops.append((DELETE, field, None))

    for raw in getattr(args, "patch_default", []):
        parsed = parse_patch_arg("?" + raw if not raw.startswith("?") else raw)
        if parsed:
            ops.append(parsed)

    return {"ops": ops}
