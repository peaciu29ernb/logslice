"""Diff two streams of log records by a key field, reporting added/removed/changed records."""

from typing import Iterator, Optional
from logslice.reader import Record


def index_records(records: list[Record], key: str) -> dict:
    """Build a dict mapping key-field value -> record for a list of records."""
    index = {}
    for rec in records:
        k = rec.get(key)
        if k is not None:
            index[str(k)] = rec
    return index


def diff_records(
    left: list[Record],
    right: list[Record],
    key: str,
    ignore_fields: Optional[list[str]] = None,
) -> Iterator[dict]:
    """
    Yield diff entries comparing left vs right records by key field.

    Each yielded dict has:
      - 'status': 'added' | 'removed' | 'changed' | 'unchanged'
      - 'key': the key value
      - 'left': left record (or None)
      - 'right': right record (or None)
      - 'changed_fields': list of field names that differ (for 'changed')
    """
    ignore = set(ignore_fields or [])
    ignore.add("_raw")

    left_index = index_records(left, key)
    right_index = index_records(right, key)

    all_keys = sorted(set(left_index) | set(right_index))

    for k in all_keys:
        l_rec = left_index.get(k)
        r_rec = right_index.get(k)

        if l_rec is None:
            yield {"status": "added", "key": k, "left": None, "right": r_rec, "changed_fields": []}
        elif r_rec is None:
            yield {"status": "removed", "key": k, "left": l_rec, "right": None, "changed_fields": []}
        else:
            l_fields = {f: v for f, v in l_rec.items() if f not in ignore}
            r_fields = {f: v for f, v in r_rec.items() if f not in ignore}
            changed = [
                f for f in set(l_fields) | set(r_fields)
                if l_fields.get(f) != r_fields.get(f)
            ]
            status = "changed" if changed else "unchanged"
            yield {"status": status, "key": k, "left": l_rec, "right": r_rec, "changed_fields": sorted(changed)}


def format_diff_table(diff_entries: list[dict]) -> str:
    """Format diff entries as a human-readable table."""
    lines = []
    symbols = {"added": "+", "removed": "-", "changed": "~", "unchanged": " "}
    for entry in diff_entries:
        sym = symbols.get(entry["status"], "?")
        k = entry["key"]
        if entry["status"] == "changed":
            fields_str = ", ".join(entry["changed_fields"])
            lines.append(f"{sym} {k}  (changed: {fields_str})")
        else:
            lines.append(f"{sym} {k}")
    return "\n".join(lines)
