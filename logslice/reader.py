"""Log file reader that yields parsed records from a file or stdin."""

import sys
from typing import Iterator, Optional
from logslice.parser import parse_line


def iter_records(path: Optional[str] = None) -> Iterator[dict]:
    """
    Yield parsed log records from *path* (or stdin if path is None/'-').
    Lines that cannot be parsed are skipped.
    Each yielded dict also contains '_raw' with the original line.
    """
    if path is None or path == '-':
        source = sys.stdin
    else:
        source = open(path, 'r', encoding='utf-8', errors='replace')

    try:
        for line in source:
            record = parse_line(line)
            if record is not None:
                record['_raw'] = line.rstrip('\n')
                yield record
    finally:
        if source is not sys.stdin:
            source.close()
