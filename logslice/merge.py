"""merge.py — merge multiple sorted or unsorted record streams into one.

Provides utilities to merge records from several sources, with optional
de-duplication and chronological ordering by a timestamp field.
"""

from __future__ import annotations

import heapq
from typing import Iterable, Iterator, List, Optional

from logslice.filter import parse_timestamp


def merge_records(
    streams: List[Iterable[dict]],
    sort_key: Optional[str] = None,
    dedupe_key: Optional[str] = None,
) -> Iterator[dict]:
    """Merge multiple record streams into a single iterator.

    Args:
        streams:    A list of iterables, each yielding record dicts.
        sort_key:   If given, merge-sort the streams using this field.
                    The field is expected to hold an ISO-8601 timestamp or
                    any string that compares correctly with ``<``.  Records
                    whose field is missing or unparseable are emitted last.
        dedupe_key: If given, suppress consecutive duplicate values for this
                    field (useful when merging overlapping log windows).

    Yields:
        Merged record dicts in the requested order.
    """
    if sort_key:
        yield from _merge_sorted(streams, sort_key, dedupe_key)
    else:
        yield from _merge_unsorted(streams, dedupe_key)


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

def _sort_value(record: dict, key: str):
    """Return a comparison key for *record* based on *key*.

    Timestamps are converted to datetime objects so they sort correctly.
    Missing / unparseable values sort to the end via a (1, …) tuple.
    """
    raw = record.get(key)
    if raw is None:
        return (1, "")
    ts = parse_timestamp(str(raw))
    if ts is not None:
        return (0, ts)
    # Fall back to lexicographic comparison for non-timestamp fields.
    return (0, str(raw))


def _merge_sorted(
    streams: List[Iterable[dict]],
    sort_key: str,
    dedupe_key: Optional[str],
) -> Iterator[dict]:
    """K-way merge using a min-heap; each heap entry is (sort_value, idx, record).

    *idx* breaks ties deterministically by stream order so that records with
    equal sort values are emitted in stream order rather than causing a
    comparison between dicts (which may contain unhashable values).
    """
    heap: list = []
    iterators = [iter(s) for s in streams]

    for idx, it in enumerate(iterators):
        record = next(it, None)
        if record is not None:
            heapq.heappush(heap, (_sort_value(record, sort_key), idx, record))

    seen_dedupe: Optional[str] = None

    while heap:
        sort_val, idx, record = heapq.heappop(heap)

        # Advance the exhausted stream's iterator.
        nxt = next(iterators[idx], None)
        if nxt is not None:
            heapq.heappush(heap, (_sort_value(nxt, sort_key), idx, nxt))

        if dedupe_key is not None:
            val = str(record.get(dedupe_key, ""))
            if val == seen_dedupe:
                continue
            seen_dedupe = val

        yield record


def _merge_unsorted(
    streams: List[Iterable[dict]],
    dedupe_key: Optional[str],
) -> Iterator[dict]:
    """Concatenate streams in order, with optional consecutive deduplication."""
    seen_dedupe: Optional[str] = None

    for stream in streams:
        for record in stream:
            if dedupe_key is not None:
                val = str(record.get(dedupe_key, ""))
                if val == seen_dedupe:
                    continue
                seen_dedupe = val
            yield record
