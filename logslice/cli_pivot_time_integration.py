"""Integration helpers: wire pivot_time into the main CLI pipeline."""

from typing import Iterable, List

from logslice.pivot_time import pivot_time_records, format_pivot_time_table
from logslice.cli_pivot_time import (
    is_pivot_time_active,
    validate_pivot_time_args,
    extract_pivot_time_kwargs,
)


def run_pivot_time_pipeline(
    records: Iterable[dict],
    args,
    output_file=None,
) -> bool:
    """Run the pivot-time pipeline if active.  Returns True if handled.

    Prints the formatted table to *output_file* (or stdout if None).
    Returns False if pivot-time is not requested so the caller can
    continue with the normal output path.
    """
    import sys

    if not is_pivot_time_active(args):
        return False

    validate_pivot_time_args(args)
    kwargs = extract_pivot_time_kwargs(args)

    fill = kwargs.pop("fill", 0.0)
    table = pivot_time_records(records, **kwargs)
    text = format_pivot_time_table(table, fill=fill)

    dest = output_file or sys.stdout
    dest.write(text)
    dest.write("\n")
    return True


def describe_pivot_time(args) -> List[str]:
    """Return human-readable description lines for pivot-time config."""
    if not is_pivot_time_active(args):
        return []
    kwargs = extract_pivot_time_kwargs(args)
    return [
        f"pivot-time: time={kwargs['time_field']}",
        f"  category={kwargs['category_field']}",
        f"  value={kwargs['value_field']}",
        f"  agg={kwargs['agg']}",
        f"  interval={kwargs['interval_seconds']}s",
        f"  fill={kwargs['fill']}",
    ]
