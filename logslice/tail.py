"""Tail support: yield last N records or follow a file for new lines."""

from __future__ import annotations

import time
from collections import deque
from typing import Iterable, Iterator

from logslice.reader import iter_records


def tail_records(records: Iterable[dict], n: int) -> list[dict]:
    """Return the last *n* records from an iterable."""
    return list(deque(records, maxlen=n))


def follow_file(path: str, poll_interval: float = 0.25) -> Iterator[dict]:
    """Yield new records appended to *path*, polling indefinitely.

    Opens the file, seeks to the end, then yields parsed records as lines
    are appended.  Stops only when the caller breaks out of the iterator.
    """
    with open(path, "r") as fh:
        fh.seek(0, 2)  # seek to end
        while True:
            line = fh.readline()
            if not line:
                time.sleep(poll_interval)
                continue
            line = line.rstrip("\n")
            if not line:
                continue
            # re-use iter_records logic by wrapping single line
            for record in iter_records([line]):
                yield record
