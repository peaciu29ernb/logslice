"""Score records by how many pattern conditions they match."""
from __future__ import annotations

import re
from typing import Any, Dict, Iterable, Iterator, List, Optional, Tuple

Record = Dict[str, Any]


def _compile(pattern: str) -> Optional[re.Pattern]:
    try:
        return re.compile(pattern)
    except re.error:
        return None


def score_record(
    record: Record,
    rules: List[Tuple[str, str]],
    field: str = "_score",
) -> Record:
    """Add a score field counting how many (key, pattern) rules match.

    Each rule is a (field_name, regex_pattern) pair.  A rule contributes
    1 point when the named field exists and its string representation
    matches the pattern.  The total is written to *field*.
    """
    score = 0
    for key, pattern in rules:
        rx = _compile(pattern)
        if rx is None:
            continue
        value = record.get(key)
        if value is None:
            continue
        if rx.search(str(value)):
            score += 1
    result = dict(record)
    result[field] = score
    return result


def score_records(
    records: Iterable[Record],
    rules: List[Tuple[str, str]],
    field: str = "_score",
    min_score: int = 0,
) -> Iterator[Record]:
    """Yield records annotated with a score, optionally filtering by min_score."""
    for record in records:
        scored = score_record(record, rules, field=field)
        if scored[field] >= min_score:
            yield scored


def parse_score_rules(raw: List[str]) -> List[Tuple[str, str]]:
    """Parse 'field:pattern' strings into (field, pattern) tuples.

    Entries that do not contain ':' are silently skipped.
    """
    rules: List[Tuple[str, str]] = []
    for item in raw:
        if ":" not in item:
            continue
        key, _, pattern = item.partition(":")
        key = key.strip()
        pattern = pattern.strip()
        if key and pattern:
            rules.append((key, pattern))
    return rules
