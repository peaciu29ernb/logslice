"""Compute summary statistics over a stream of log records."""
from __future__ import annotations

from collections import Counter, defaultdict
from typing import Iterable, Any


def compute_stats(records: Iterable[dict]) -> dict[str, Any]:
    """Return summary statistics for the given records."""
    total = 0
    field_counts: Counter = Counter()
    value_counts: dict[str, Counter] = defaultdict(Counter)
    earliest = None
    latest = None

    for record in records:
        total += 1
        for key, value in record.items():
            if key == "_raw":
                continue
            field_counts[key] += 1
            if isinstance(value, str):
                value_counts[key][value] += 1

        ts = record.get("timestamp") or record.get("time") or record.get("ts")
        if ts:
            if earliest is None or ts < earliest:
                earliest = ts
            if latest is None or ts > latest:
                latest = ts

    return {
        "total": total,
        "fields": dict(field_counts),
        "top_values": {k: v.most_common(5) for k, v in value_counts.items()},
        "earliest": earliest,
        "latest": latest,
    }


def format_stats(stats: dict[str, Any]) -> str:
    """Format stats dict as a human-readable string."""
    lines = [
        f"Total records : {stats['total']}",
        f"Earliest      : {stats['earliest'] or 'n/a'}",
        f"Latest        : {stats['latest'] or 'n/a'}",
        "Fields:",
    ]
    for field, count in sorted(stats["fields"].items()):
        lines.append(f"  {field}: {count}")
        top = stats["top_values"].get(field, [])
        for val, n in top:
            lines.append(f"    '{val}': {n}")
    return "\n".join(lines)
