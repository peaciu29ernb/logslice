"""Integration helpers for running the percentile pipeline from the CLI."""

from __future__ import annotations

import sys
from typing import Iterable

from logslice.percentile import percentile_records, format_percentile_table
from logslice.cli_percentile import (
    extract_percentile_kwargs,
    is_percentile_active,
    validate_percentile_args,
)


def run_percentile_pipeline(records: Iterable[dict], args) -> bool:
    """Compute and print percentile table if the feature is active.

    Returns True if output was produced (caller should skip normal output).
    """
    if not is_percentile_active(args):
        return False

    errors = validate_percentile_args(args)
    if errors:
        for err in errors:
            print(f"error: {err}", file=sys.stderr)
        sys.exit(1)

    kwargs = extract_percentile_kwargs(args)
    data = percentile_records(records, **kwargs)
    table = format_percentile_table(
        data,
        percentiles=kwargs["percentiles"],
        group_by=kwargs["group_by"],
    )
    print(table)
    return True


def describe_percentile(args) -> str | None:
    """Return a human-readable description of active percentile settings."""
    if not is_percentile_active(args):
        return None
    kwargs = extract_percentile_kwargs(args)
    ps = ", ".join(f"p{int(p)}" for p in kwargs["percentiles"])
    desc = f"percentiles [{ps}] of '{kwargs['field']}'"
    if kwargs["group_by"]:
        desc += f" grouped by '{kwargs['group_by']}'"
    return desc
