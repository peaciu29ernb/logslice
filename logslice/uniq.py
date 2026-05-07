"""Consecutive deduplication: suppress repeated records by field value."""

from typing import Iterator, Iterable, Optional, List


def _make_key(record: dict, fields: List[str]) -> tuple:
    """Build a comparison key from the specified fields."""
    return tuple(record.get(f) for f in fields)


def uniq_records(
    records: Iterable[dict],
    fields: List[str],
    count: bool = False,
    count_field: str = "_count",
) -> Iterator[dict]:
    """Yield records, suppressing consecutive duplicates by field values.

    If *count* is True, a ``count_field`` key is added with the number of
    consecutive occurrences that were collapsed into the emitted record.
    """
    prev_key: Optional[tuple] = None
    prev_record: Optional[dict] = None
    run: int = 0

    for record in records:
        key = _make_key(record, fields)
        if key == prev_key:
            run += 1
        else:
            if prev_record is not None:
                yield _maybe_add_count(prev_record, run, count, count_field)
            prev_key = key
            prev_record = record
            run = 1

    if prev_record is not None:
        yield _maybe_add_count(prev_record, run, count, count_field)


def _maybe_add_count(record: dict, run: int, count: bool, count_field: str) -> dict:
    if not count:
        return record
    out = dict(record)
    raw = out.pop("_raw", None)
    out[count_field] = run
    if raw is not None:
        out["_raw"] = raw
    return out
