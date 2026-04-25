"""Limit and offset support for log record streams."""

from typing import Iterable, Iterator


def skip_records(records: Iterable[dict], offset: int) -> Iterator[dict]:
    """Skip the first `offset` records from the stream."""
    if offset < 0:
        raise ValueError(f"offset must be non-negative, got {offset}")
    it = iter(records)
    skipped = 0
    for record in it:
        if skipped < offset:
            skipped += 1
            continue
        yield record


def limit_records(records: Iterable[dict], count: int) -> Iterator[dict]:
    """Yield at most `count` records from the stream."""
    if count < 0:
        raise ValueError(f"count must be non-negative, got {count}")
    emitted = 0
    for record in records:
        if emitted >= count:
            break
        yield record
        emitted += 1


def limit_offset_records(
    records: Iterable[dict],
    count: int | None = None,
    offset: int = 0,
) -> Iterator[dict]:
    """Apply optional offset then optional limit to a record stream.

    Args:
        records: Source iterable of parsed log records.
        count:   Maximum number of records to emit.  ``None`` means no limit.
        offset:  Number of leading records to skip before emitting.

    Yields:
        Records after skipping `offset` entries, up to `count` records.
    """
    stream: Iterable[dict] = records
    if offset:
        stream = skip_records(stream, offset)
    if count is not None:
        stream = limit_records(stream, count)
    yield from stream
