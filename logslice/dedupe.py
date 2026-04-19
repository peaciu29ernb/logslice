"""Deduplication of log records based on field values."""

from typing import Iterator, List, Optional, Tuple
from collections import OrderedDict


def make_key(record: dict, fields: List[str]) -> Tuple:
    """Build a hashable key from specified fields in a record."""
    return tuple(record.get(f) for f in fields)


def dedupe_records(
    records: Iterator[dict],
    fields: List[str],
    keep: str = "first",
    max_seen: Optional[int] = None,
) -> Iterator[dict]:
    """
    Yield records deduplicated by the given fields.

    Args:
        records: iterable of parsed log records
        fields: list of field names to form the dedup key
        keep: 'first' or 'last' — which occurrence to keep
        max_seen: if set, limit the seen-key cache to this size (LRU eviction)
    """
    if not fields:
        yield from records
        return

    if keep == "first":
        seen: OrderedDict = OrderedDict()
        for record in records:
            key = make_key(record, fields)
            if key not in seen:
                if max_seen and len(seen) >= max_seen:
                    seen.popitem(last=False)
                seen[key] = True
                yield record
    elif keep == "last":
        # Buffer all records, emit last seen per key
        latest: OrderedDict = OrderedDict()
        for record in records:
            key = make_key(record, fields)
            latest[key] = record
        yield from latest.values()
    else:
        raise ValueError(f"keep must be 'first' or 'last', got {keep!r}")
