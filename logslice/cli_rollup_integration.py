"""cli_rollup_integration.py — wire rollup into the main CLI pipeline."""
from __future__ import annotations

import sys
from typing import Iterable, Optional

from logslice.rollup import format_rollup_table, rollup_records


def run_rollup_pipeline(
    records: Iterable[dict],
    value_field: str,
    group_field: Optional[str] = None,
    time_field: str = "timestamp",
    interval_seconds: int = 60,
    ops: tuple = ("sum", "count", "min", "max", "avg"),
    output_format: str = "table",
) -> None:
    """Execute rollup aggregation and write results to stdout."""
    import json

    rows = rollup_records(
        records,
        value_field=value_field,
        group_field=group_field,
        time_field=time_field,
        interval_seconds=interval_seconds,
        ops=ops,
    )

    if output_format == "json":
        for row in rows:
            sys.stdout.write(json.dumps(row) + "\n")
    elif output_format == "logfmt":
        for row in rows:
            parts = []
            for k, v in row.items():
                sv = str(v)
                if " " in sv:
                    sv = f'"{sv}"'
                parts.append(f"{k}={sv}")
            sys.stdout.write(" ".join(parts) + "\n")
    else:
        sys.stdout.write(format_rollup_table(rows, group_field=group_field) + "\n")


def describe_rollup(
    value_field: str,
    group_field: Optional[str],
    interval_seconds: int,
    ops: tuple,
) -> str:
    """Return a human-readable description of the rollup configuration."""
    parts = [
        f"field={value_field}",
        f"interval={interval_seconds}s",
        f"ops={','.join(ops)}",
    ]
    if group_field:
        parts.append(f"group={group_field}")
    return "rollup(" + ", ".join(parts) + ")"
