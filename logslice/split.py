"""Split records into multiple output files based on a field value."""

import os
import json
from collections import defaultdict
from typing import Iterable, Dict, List, Optional, Callable


def split_records(
    records: Iterable[dict],
    field: str,
    missing: str = "__unknown__",
) -> Dict[str, List[dict]]:
    """Partition records into buckets keyed by the value of *field*.

    Records that lack *field* are placed under *missing*.
    """
    buckets: Dict[str, List[dict]] = defaultdict(list)
    for record in records:
        key = record.get(field)
        if key is None:
            bucket_key = missing
        else:
            bucket_key = str(key)
        buckets[bucket_key].append(record)
    return dict(buckets)


def make_filename(directory: str, prefix: str, key: str, ext: str = ".log") -> str:
    """Build an output filename for a given bucket key.

    Non-alphanumeric characters in *key* are replaced with underscores so the
    result is always a safe filesystem path.
    """
    safe_key = "".join(c if c.isalnum() or c in "-_" else "_" for c in key)
    filename = f"{prefix}{safe_key}{ext}"
    return os.path.join(directory, filename)


def write_split(
    buckets: Dict[str, List[dict]],
    directory: str,
    prefix: str = "",
    ext: str = ".log",
    formatter: Optional[Callable[[dict], str]] = None,
) -> Dict[str, int]:
    """Write each bucket to its own file inside *directory*.

    Returns a mapping of ``{filename: record_count}`` for every file written.
    If *formatter* is provided it is called per record; otherwise records are
    serialised as JSON.
    """
    os.makedirs(directory, exist_ok=True)
    summary: Dict[str, int] = {}

    def default_fmt(rec: dict) -> str:
        payload = {k: v for k, v in rec.items() if k != "_raw"}
        return json.dumps(payload, ensure_ascii=False)

    fmt = formatter or default_fmt

    for key, records in buckets.items():
        path = make_filename(directory, prefix, key, ext)
        with open(path, "w", encoding="utf-8") as fh:
            for rec in records:
                fh.write(fmt(rec) + "\n")
        summary[path] = len(records)

    return summary
