"""top.py — select top-N records by a numeric field value."""

from __future__ import annotations

import heapq
from typing import Iterable, Iterator


def _to_float(value) -> float | None:
    """Coerce a value to float, returning None on failure."""
    if value is None:
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def top_records(
    records: Iterable[dict],
    field: str,
    n: int,
    ascending: bool = False,
) -> list[dict]:
    """Return the top-N records ranked by *field*.

    Records where *field* is missing or non-numeric are skipped.

    Args:
        records:   Iterable of parsed log records.
        field:     Field name to rank by.
        n:         Number of records to return.
        ascending: When True return the *lowest* N values instead.

    Returns:
        List of up to *n* records sorted by *field* (highest first by default).
    """
    if n <= 0:
        return []

    scored: list[tuple[float, dict]] = []
    for rec in records:
        val = _to_float(rec.get(field))
        if val is None:
            continue
        scored.append((val, rec))

    scored.sort(key=lambda t: t[0], reverse=not ascending)
    return [rec for _, rec in scored[:n]]


def top_records_iter(
    records: Iterable[dict],
    field: str,
    n: int,
    ascending: bool = False,
) -> Iterator[dict]:
    """Streaming variant — buffers all scoreable records then yields top-N."""
    yield from top_records(records, field, n, ascending=ascending)


def format_top_table(records: list[dict], field: str) -> str:
    """Format top records as a simple ranked text table."""
    if not records:
        return f"(no records with field '{field}')"

    lines = [f"{'Rank':<6} {field}"]
    lines.append("-" * (6 + 1 + max(len(field), 10)))
    for rank, rec in enumerate(records, start=1):
        val = rec.get(field, "")
        lines.append(f"{rank:<6} {val}")
    return "\n".join(lines)
