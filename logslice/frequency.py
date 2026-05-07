"""Compute per-field value frequency distributions over a stream of records."""

from collections import Counter
from typing import Iterable, Iterator


def count_values(records: Iterable[dict], field: str) -> Counter:
    """Return a Counter of all values seen for *field* across *records*."""
    counts: Counter = Counter()
    for record in records:
        value = record.get(field)
        if value is not None:
            counts[str(value)] += 1
    return counts


def frequency_records(
    records: Iterable[dict],
    field: str,
    top_n: int = 0,
    min_count: int = 1,
) -> Iterator[dict]:
    """Yield frequency-summary records sorted by count descending.

    Args:
        records:   Input log records.
        field:     The field whose value distribution to compute.
        top_n:     If > 0, only yield the top-N values.
        min_count: Skip values whose count is below this threshold.
    """
    counts = count_values(records, field)
    ranked = counts.most_common() if top_n <= 0 else counts.most_common(top_n)
    total = sum(counts.values())
    for value, count in ranked:
        if count < min_count:
            continue
        pct = (count / total * 100) if total > 0 else 0.0
        yield {
            field: value,
            "count": count,
            "total": total,
            "pct": round(pct, 2),
        }


def format_frequency_table(
    rows: Iterable[dict],
    field: str,
    width: int = 20,
) -> str:
    """Return a human-readable frequency table as a string."""
    rows = list(rows)
    if not rows:
        return "(no data)"

    lines = [f"{'VALUE':<{width}}  {'COUNT':>8}  {'PCT':>7}"]
    lines.append("-" * (width + 20))
    for row in rows:
        value = str(row.get(field, ""))
        count = row.get("count", 0)
        pct = row.get("pct", 0.0)
        lines.append(f"{value:<{width}}  {count:>8}  {pct:>6.2f}%")
    return "\n".join(lines)
