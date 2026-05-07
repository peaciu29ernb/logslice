"""Count records matching field conditions, optionally grouped."""

from collections import defaultdict
from typing import Dict, Iterable, Iterator, List, Optional, Tuple
import re


def _compile(pattern: str):
    try:
        return re.compile(pattern)
    except re.error:
        return None


def parse_countif_rule(rule: str) -> Optional[Tuple[str, str, str]]:
    """Parse a rule like 'field:op:value' into (field, op, value).

    Supported ops: eq, ne, gt, lt, gte, lte, re (regex match).
    Returns None if the rule is malformed.
    """
    parts = rule.split(":", 2)
    if len(parts) != 3:
        return None
    field, op, value = parts
    if not field or not op or op not in ("eq", "ne", "gt", "lt", "gte", "lte", "re"):
        return None
    return field, op, value


def _matches_rule(record: dict, field: str, op: str, value: str) -> bool:
    raw = record.get(field)
    if raw is None:
        return False
    sv = str(raw)
    if op == "eq":
        return sv == value
    if op == "ne":
        return sv != value
    if op == "re":
        compiled = _compile(value)
        return bool(compiled and compiled.search(sv))
    try:
        fv = float(sv)
        thresh = float(value)
    except (ValueError, TypeError):
        return False
    if op == "gt":
        return fv > thresh
    if op == "lt":
        return fv < thresh
    if op == "gte":
        return fv >= thresh
    if op == "lte":
        return fv <= thresh
    return False


def countif_records(
    records: Iterable[dict],
    rules: List[Tuple[str, str, str]],
    group_by: Optional[str] = None,
) -> Dict[str, int]:
    """Count records where ALL rules match, optionally grouped by a field."""
    counts: Dict[str, int] = defaultdict(int)
    for record in records:
        if all(_matches_rule(record, f, op, v) for f, op, v in rules):
            key = str(record.get(group_by, "_all")) if group_by else "_all"
            counts[key] += 1
    return dict(counts)


def format_countif_table(counts: Dict[str, int]) -> str:
    """Format countif results as a simple text table."""
    if not counts:
        return "(no matches)"
    width = max(len(k) for k in counts)
    lines = [f"{'group':<{width}}  count"]
    lines.append("-" * (width + 8))
    for key, count in sorted(counts.items(), key=lambda x: -x[1]):
        lines.append(f"{key:<{width}}  {count}")
    return "\n".join(lines)
