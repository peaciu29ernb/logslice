"""Group and count log records by a field value."""
from __future__ import annotations

from collections import Counter, defaultdict
from typing import Iterable


def group_by(records: Iterable[dict], field: str) -> dict[str, list[dict]]:
    """Group records into lists keyed by the value of *field*."""
    groups: dict[str, list[dict]] = defaultdict(list)
    for record in records:
        key = str(record.get(field, "<missing>"))
        groups[key].append(record)
    return dict(groups)


def count_by(records: Iterable[dict], field: str) -> Counter:
    """Return a Counter of record counts keyed by *field* value."""
    counter: Counter = Counter()
    for record in records:
        key = str(record.get(field, "<missing>"))
        counter[key] += 1
    return counter


def format_count_table(counter: Counter, title: str = "") -> str:
    """Render a sorted count table as plain text."""
    lines = []
    if title:
        lines.append(title)
        lines.append("-" * len(title))
    width = max((len(k) for k in counter), default=5)
    for value, count in counter.most_common():
        lines.append(f"{value:<{width}}  {count}")
    return "\n".join(lines)
