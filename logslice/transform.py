"""Field transformation utilities for logslice records."""

from typing import Any, Dict, List, Optional


def rename_fields(record: Dict[str, Any], mapping: Dict[str, str]) -> Dict[str, Any]:
    """Return a new record with fields renamed according to mapping."""
    result = {}
    for key, value in record.items():
        if key == "_raw":
            result[key] = value
        elif key in mapping:
            result[mapping[key]] = value
        else:
            result[key] = value
    return result


def drop_fields(record: Dict[str, Any], fields: List[str]) -> Dict[str, Any]:
    """Return a new record with specified fields removed."""
    return {k: v for k, v in record.items() if k not in fields or k == "_raw"}


def keep_fields(record: Dict[str, Any], fields: List[str]) -> Dict[str, Any]:
    """Return a new record keeping only specified fields (plus _raw)."""
    kept = set(fields) | {"_raw"}
    return {k: v for k, v in record.items() if k in kept}


def add_field(record: Dict[str, Any], key: str, value: Any) -> Dict[str, Any]:
    """Return a new record with an additional field set."""
    result = dict(record)
    result[key] = value
    return result


def apply_transforms(
    records,
    rename: Optional[Dict[str, str]] = None,
    drop: Optional[List[str]] = None,
    keep: Optional[List[str]] = None,
):
    """Apply a chain of transformations to an iterable of records."""
    for record in records:
        if rename:
            record = rename_fields(record, rename)
        if drop:
            record = drop_fields(record, drop)
        if keep:
            record = keep_fields(record, keep)
        yield record
