"""Field computation: evaluate simple arithmetic expressions over record fields."""

from __future__ import annotations

import operator
import re
from typing import Any, Dict, Iterable, Iterator, List, Optional, Tuple

Record = Dict[str, Any]

_OPERATORS = {
    "+": operator.add,
    "-": operator.sub,
    "*": operator.mul,
    "/": operator.truediv,
    "%": operator.mod,
}

_EXPR_RE = re.compile(
    r"^\s*([\w.]+)\s*([+\-*/%])\s*([\w.]+)\s*$"
)


def _resolve(token: str, record: Record) -> Optional[float]:
    """Return token as a float literal or look it up in the record."""
    try:
        return float(token)
    except ValueError:
        val = record.get(token)
        if val is None:
            return None
        try:
            return float(val)
        except (TypeError, ValueError):
            return None


def parse_compute_arg(arg: str) -> Optional[Tuple[str, str]]:
    """Parse 'dest=expr' into (dest, expr). Returns None on bad format."""
    parts = arg.split("=", 1)
    if len(parts) != 2:
        return None
    dest, expr = parts[0].strip(), parts[1].strip()
    if not dest or not expr:
        return None
    return dest, expr


def evaluate_expr(expr: str, record: Record) -> Optional[float]:
    """Evaluate a binary arithmetic expression against a record.

    Supports: field OP field, field OP literal, literal OP field.
    Returns None if operands cannot be resolved or division by zero.
    """
    m = _EXPR_RE.match(expr)
    if not m:
        return None
    left_tok, op_sym, right_tok = m.group(1), m.group(2), m.group(3)
    left = _resolve(left_tok, record)
    right = _resolve(right_tok, record)
    if left is None or right is None:
        return None
    op_fn = _OPERATORS[op_sym]
    try:
        return op_fn(left, right)
    except ZeroDivisionError:
        return None


def compute_fields(
    record: Record,
    assignments: List[Tuple[str, str]],
) -> Record:
    """Return a new record with computed fields added (or overwritten)."""
    result = dict(record)
    for dest, expr in assignments:
        value = evaluate_expr(expr, record)
        if value is not None:
            # Store as int when the result is a whole number
            result[dest] = int(value) if value == int(value) else value
    return result


def compute_records(
    records: Iterable[Record],
    assignments: List[Tuple[str, str]],
) -> Iterator[Record]:
    """Yield records with computed fields applied."""
    for rec in records:
        yield compute_fields(rec, assignments)
