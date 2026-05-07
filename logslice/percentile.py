"""Percentile computation over a numeric field across log records."""

from __future__ import annotations

import math
from typing import Iterable, Iterator


def _to_float(value) -> float | None:
    if value is None:
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def compute_percentile(values: list[float], p: float) -> float | None:
    """Return the p-th percentile (0-100) of a sorted list using linear interpolation."""
    if not values:
        return None
    if not 0.0 <= p <= 100.0:
        raise ValueError(f"Percentile must be between 0 and 100, got {p}")
    sorted_vals = sorted(values)
    n = len(sorted_vals)
    if n == 1:
        return sorted_vals[0]
    idx = (p / 100.0) * (n - 1)
    lo = int(math.floor(idx))
    hi = int(math.ceil(idx))
    if lo == hi:
        return sorted_vals[lo]
    frac = idx - lo
    return sorted_vals[lo] * (1 - frac) + sorted_vals[hi] * frac


def percentile_records(
    records: Iterable[dict],
    field: str,
    percentiles: list[float],
    group_by: str | None = None,
) -> dict:
    """Collect values and compute percentiles, optionally grouped."""
    groups: dict[str, list[float]] = {}
    for rec in records:
        val = _to_float(rec.get(field))
        if val is None:
            continue
        key = str(rec.get(group_by, "_all")) if group_by else "_all"
        groups.setdefault(key, []).append(val)
    result = {}
    for group, values in groups.items():
        result[group] = {
            f"p{int(p)}": compute_percentile(values, p) for p in percentiles
        }
        result[group]["count"] = len(values)
    return result


def format_percentile_table(
    data: dict, percentiles: list[float], group_by: str | None = None
) -> str:
    """Render percentile results as a plain-text table."""
    if not data:
        return "(no data)"
    p_headers = [f"p{int(p)}" for p in percentiles]
    headers = (["group"] if group_by else []) + p_headers + ["count"]
    rows = []
    for group, stats in sorted(data.items()):
        row = ([group] if group_by else []) + [
            f"{stats[h]:.4g}" if stats[h] is not None else "N/A" for h in p_headers
        ] + [str(stats["count"])]
        rows.append(row)
    col_widths = [
        max(len(h), max((len(r[i]) for r in rows), default=0))
        for i, h in enumerate(headers)
    ]
    fmt = "  ".join(f"{{:<{w}}}" for w in col_widths)
    lines = [fmt.format(*headers), "-" * sum(col_widths + [2 * (len(headers) - 1)])]
    for row in rows:
        lines.append(fmt.format(*row))
    return "\n".join(lines)
