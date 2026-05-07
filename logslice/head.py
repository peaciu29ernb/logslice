"""head.py — return the first N records from a stream."""

from typing import Iterable, Iterator


def head_records(records: Iterable[dict], n: int) -> Iterator[dict]:
    """Yield at most the first *n* records.

    Args:
        records: Iterable of parsed log record dicts.
        n: Maximum number of records to yield.  If *n* is zero or
           negative the function yields nothing.

    Yields:
        Record dicts, in original order, up to *n* items.
    """
    if n <= 0:
        return
    count = 0
    for record in records:
        yield record
        count += 1
        if count >= n:
            break


def head_records_iter(records: Iterable[dict], n: int) -> list[dict]:
    """Collect the first *n* records into a list.

    Convenience wrapper around :func:`head_records` for callers that
    need a concrete list rather than a lazy iterator.

    Args:
        records: Iterable of parsed log record dicts.
        n: Maximum number of records to collect.

    Returns:
        A list containing at most *n* records.
    """
    return list(head_records(records, n))
