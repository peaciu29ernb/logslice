"""CLI argument registration for export subcommand."""

import argparse
from typing import Any, Dict, Optional


def register_export_args(parser: argparse.ArgumentParser) -> None:
    """Add export-related arguments to a parser."""
    parser.add_argument(
        "--export-format",
        choices=["csv", "tsv"],
        default="csv",
        help="Output format for export (default: csv)",
    )
    parser.add_argument(
        "--export-fields",
        metavar="FIELD",
        nargs="+",
        default=None,
        help="Explicit list of fields to include as columns (in order)",
    )
    parser.add_argument(
        "--export-output",
        metavar="FILE",
        default=None,
        help="Write export to FILE instead of stdout",
    )


def extract_export_kwargs(args: argparse.Namespace) -> Dict[str, Any]:
    """Extract export kwargs from parsed args."""
    return {
        "fmt": getattr(args, "export_format", "csv"),
        "fieldnames": getattr(args, "export_fields", None),
        "output_path": getattr(args, "export_output", None),
    }
