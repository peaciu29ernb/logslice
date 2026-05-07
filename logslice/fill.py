"""Fill missing field values in records using a default or a carry-forward strategy."""

from typing import Any, Dict, Iterable, Iterator, List, Optional

Record = Dict[str, Any]


def fill_with_default(
    record: Record,
    fields: List[str],
    default: Any = None,
) -> Record:
    """Return a copy of record with missing fields filled by *default*."""
    out = dict(record)
    for field in fields:
        if field not in out or out[field] is None:
            out[field] = default
    return out


def fill_forward(
    record: Record,
    fields: List[str],
    carry: Dict[str, Any],
) -> Record:
    """Return a copy of record with missing fields filled from *carry* (last seen value).

    *carry* is mutated in-place so the caller can pass the same dict across calls.
    """
    out = dict(record)
    for field in fields:
        value = out.get(field)
        if value is None:
            if field in carry:
                out[field] = carry[field]
        else:
            carry[field] = value
    return out


def fill_records(
    records: Iterable[Record],
    fields: List[str],
    default: Any = None,
    forward: bool = False,
) -> Iterator[Record]:
    """Yield records with missing field values filled.

    If *forward* is True, carry the last seen value for each field forward.
    Otherwise fill with *default*.
    """
    carry: Dict[str, Any] = {}
    for record in records:
        if forward:
            yield fill_forward(record, fields, carry)
        else:
            yield fill_with_default(record, fields, default)
