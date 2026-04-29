"""Full-text and field-targeted grep for log records."""

import re
from typing import Iterable, Iterator, Optional


def _compile(pattern: str, ignore_case: bool = False) -> Optional[re.Pattern]:
    """Compile a regex pattern, returning None on error."""
    flags = re.IGNORECASE if ignore_case else 0
    try:
        return re.compile(pattern, flags)
    except re.error:
        return None


def grep_record(
    record: dict,
    pattern: str,
    fields: Optional[list] = None,
    ignore_case: bool = False,
    invert: bool = False,
) -> bool:
    """Return True if record matches the grep pattern.

    Args:
        record: Parsed log record dict.
        pattern: Regex pattern to search for.
        fields: If given, only search these field names; else search all values.
        ignore_case: Case-insensitive matching.
        invert: Return True when the record does NOT match.
    """
    compiled = _compile(pattern, ignore_case)
    if compiled is None:
        return False

    if fields:
        candidates = [str(record[f]) for f in fields if f in record and f != "_raw"]
    else:
        candidates = [
            str(v) for k, v in record.items() if k != "_raw" and v is not None
        ]

    matched = any(compiled.search(c) for c in candidates)
    return matched if not invert else not matched


def grep_records(
    records: Iterable[dict],
    pattern: str,
    fields: Optional[list] = None,
    ignore_case: bool = False,
    invert: bool = False,
) -> Iterator[dict]:
    """Yield records that match (or don't match) the pattern."""
    for record in records:
        if grep_record(record, pattern, fields=fields, ignore_case=ignore_case, invert=invert):
            yield record
