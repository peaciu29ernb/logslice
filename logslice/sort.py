"""Sort log records by one or more fields."""

from typing import Any, Iterable, Iterator


def _get_sort_key(record: dict, fields: list[str], missing: Any = None) -> tuple:
    """Return a tuple of values for the given fields, used as a sort key."""
    return tuple(record.get(f, missing) for f in fields)


def _coerce_for_comparison(value: Any) -> tuple:
    """Return a (type_rank, value) pair so mixed types sort stably."""
    if value is None:
        return (0, "")
    if isinstance(value, bool):
        return (1, int(value))
    if isinstance(value, (int, float)):
        return (2, value)
    return (3, str(value))


def sort_records(
    records: Iterable[dict],
    fields: list[str],
    reverse: bool = False,
    stable: bool = True,
) -> list[dict]:
    """Sort *records* by *fields* in ascending order (or descending if *reverse*).

    Mixed-type values are handled gracefully: None < numbers < strings.
    When *stable* is True (default) the original relative order is preserved
    for records that compare equal.
    """
    if not fields:
        return list(records)

    def key_fn(record: dict) -> tuple:
        raw = _get_sort_key(record, fields)
        return tuple(_coerce_for_comparison(v) for v in raw)

    return sorted(records, key=key_fn, reverse=reverse)


def sort_records_iter(
    records: Iterable[dict],
    fields: list[str],
    reverse: bool = False,
) -> Iterator[dict]:
    """Streaming wrapper around :func:`sort_records`.

    Note: sorting requires buffering all records in memory.
    """
    yield from sort_records(records, fields, reverse=reverse)
