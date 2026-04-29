"""Assign categorical labels to records based on field value conditions."""

from __future__ import annotations

import re
from typing import Any, Dict, Iterable, Iterator, List, Optional, Tuple

Record = Dict[str, Any]
Rule = Tuple[str, str, str, str]  # (field, op, value, label)


def _matches_rule(record: Record, field: str, op: str, operand: str) -> bool:
    """Return True if the record field satisfies the condition."""
    raw = record.get(field)
    if raw is None:
        return False
    value = str(raw)
    if op == "eq":
        return value == operand
    if op == "neq":
        return value != operand
    if op == "contains":
        return operand in value
    if op == "startswith":
        return value.startswith(operand)
    if op == "endswith":
        return value.endswith(operand)
    if op == "regex":
        try:
            return bool(re.search(operand, value))
        except re.error:
            return False
    if op in ("gt", "lt", "gte", "lte"):
        try:
            fv, fo = float(value), float(operand)
        except (ValueError, TypeError):
            return False
        return {"gt": fv > fo, "lt": fv < fo, "gte": fv >= fo, "lte": fv <= fo}[op]
    return False


def parse_label_rule(spec: str) -> Optional[Rule]:
    """Parse a rule string of the form 'field:op:operand=label'.

    Returns a (field, op, operand, label) tuple or None if invalid.
    """
    if "=" not in spec:
        return None
    lhs, _, label = spec.partition("=")
    parts = lhs.split(":", 2)
    if len(parts) != 3:
        return None
    field, op, operand = parts
    if not field or not op or not label:
        return None
    return field, op, operand, label


def label_record(
    record: Record,
    rules: List[Rule],
    dest: str = "label",
    default: Optional[str] = None,
    multi: bool = False,
) -> Record:
    """Apply label rules to a record, returning an updated copy.

    If *multi* is True, all matching labels are joined with '|'.
    Otherwise the first match wins.
    """
    matched: List[str] = []
    for field, op, operand, lbl in rules:
        if _matches_rule(record, field, op, operand):
            if multi:
                matched.append(lbl)
            else:
                matched = [lbl]
                break
    result = dict(record)
    if matched:
        result[dest] = "|".join(matched)
    elif default is not None:
        result[dest] = default
    return result


def label_records(
    records: Iterable[Record],
    rules: List[Rule],
    dest: str = "label",
    default: Optional[str] = None,
    multi: bool = False,
) -> Iterator[Record]:
    """Yield labelled versions of each record."""
    for record in records:
        yield label_record(record, rules, dest=dest, default=default, multi=multi)
