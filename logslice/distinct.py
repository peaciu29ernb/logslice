"""distinct.py — emit only records with unique values for one or more fields."""

from typing import Iterable, Iterator, List, Optional, Tuple


def _make_key(record: dict, fields: List[str]) -> Tuple:
    """Build a hashable key from the specified fields of a record."""
    return tuple(record.get(f) for f in fields)


def distinct_records(
    records: Iterable[dict],
    fields: List[str],
    keep: str = "first",
) -> Iterator[dict]:
    """Yield records that are distinct with respect to *fields*.

    Args:
        records: Iterable of parsed log records.
        fields:  Field names whose combined value forms the uniqueness key.
        keep:    ``"first"`` (default) keeps the first occurrence;
                 ``"last"`` keeps the last occurrence (requires buffering).

    Yields:
        Records whose key has not been seen before (``keep="first"``), or
        the final record for each key (``keep="last"``).  Records that are
        missing *all* of the requested fields are always passed through.
    """
    if not fields:
        yield from records
        return

    if keep == "first":
        seen: set = set()
        for record in records:
            key = _make_key(record, fields)
            if key not in seen:
                seen.add(key)
                yield record
    elif keep == "last":
        latest: dict = {}
        order: List[Tuple] = []
        for record in records:
            key = _make_key(record, fields)
            if key not in latest:
                order.append(key)
            latest[key] = record
        for key in order:
            yield latest[key]
    else:
        raise ValueError(f"keep must be 'first' or 'last', got {keep!r}")


def count_distinct(records: Iterable[dict], fields: List[str]) -> int:
    """Return the number of distinct key combinations seen across *records*."""
    seen: set = set()
    for record in records:
        seen.add(_make_key(record, fields))
    return len(seen)
