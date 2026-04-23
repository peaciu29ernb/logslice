"""Join records from two sources on a common key field."""

from typing import Dict, Iterable, Iterator, List, Optional


def index_by_key(records: Iterable[dict], key: str) -> Dict[str, List[dict]]:
    """Build an index mapping key values to lists of matching records."""
    index: Dict[str, List[dict]] = {}
    for record in records:
        value = record.get(key)
        if value is None:
            continue
        k = str(value)
        index.setdefault(k, []).append(record)
    return index


def inner_join(
    left: Iterable[dict],
    right_index: Dict[str, List[dict]],
    key: str,
    prefix: str = "right_",
) -> Iterator[dict]:
    """Yield merged records for each left record that has a match in right_index."""
    for record in left:
        value = record.get(key)
        if value is None:
            continue
        matches = right_index.get(str(value), [])
        for match in matches:
            merged = dict(record)
            raw = merged.pop("__raw__", None)
            for k, v in match.items():
                if k == "__raw__" or k == key:
                    continue
                merged[f"{prefix}{k}"] = v
            if raw is not None:
                merged["__raw__"] = raw
            yield merged


def left_join(
    left: Iterable[dict],
    right_index: Dict[str, List[dict]],
    key: str,
    prefix: str = "right_",
) -> Iterator[dict]:
    """Yield merged records for every left record; unmatched records pass through."""
    for record in left:
        value = record.get(key)
        matches = right_index.get(str(value), []) if value is not None else []
        if not matches:
            yield dict(record)
        else:
            for match in matches:
                merged = dict(record)
                raw = merged.pop("__raw__", None)
                for k, v in match.items():
                    if k == "__raw__" or k == key:
                        continue
                    merged[f"{prefix}{k}"] = v
                if raw is not None:
                    merged["__raw__"] = raw
                yield merged


def join_records(
    left: Iterable[dict],
    right: Iterable[dict],
    key: str,
    how: str = "inner",
    prefix: str = "right_",
) -> Iterator[dict]:
    """Join two record streams on a shared key field.

    Args:
        left: Primary record stream.
        right: Secondary record stream to join against.
        key: Field name to join on.
        how: Join strategy — 'inner' or 'left'.
        prefix: Prefix applied to fields from the right stream.
    """
    right_index = index_by_key(right, key)
    if how == "left":
        return left_join(left, right_index, key, prefix)
    return inner_join(left, right_index, key, prefix)
