"""Flatten nested dicts in log records into dot-separated keys."""

from typing import Any, Dict, Iterator, List, Optional


def flatten_dict(
    data: Dict[str, Any],
    prefix: str = "",
    separator: str = ".",
    max_depth: Optional[int] = None,
    _depth: int = 0,
) -> Dict[str, Any]:
    """Recursively flatten a nested dict into dot-separated keys.

    Args:
        data: The dict to flatten.
        prefix: Key prefix accumulated during recursion.
        separator: Separator between key segments (default '.').
        max_depth: Maximum nesting depth to flatten; deeper levels are kept as-is.
        _depth: Internal recursion depth counter.

    Returns:
        A flat dict with no nested dict values (up to max_depth).
    """
    result: Dict[str, Any] = {}
    for key, value in data.items():
        full_key = f"{prefix}{separator}{key}" if prefix else key
        if (
            isinstance(value, dict)
            and value
            and (max_depth is None or _depth < max_depth)
        ):
            nested = flatten_dict(
                value,
                prefix=full_key,
                separator=separator,
                max_depth=max_depth,
                _depth=_depth + 1,
            )
            result.update(nested)
        else:
            result[full_key] = value
    return result


def flatten_record(
    record: Dict[str, Any],
    separator: str = ".",
    max_depth: Optional[int] = None,
    preserve_raw: bool = True,
) -> Dict[str, Any]:
    """Flatten a single log record, preserving the '_raw' key if present."""
    raw = record.get("_raw")
    flat = flatten_dict(
        {k: v for k, v in record.items() if k != "_raw"},
        separator=separator,
        max_depth=max_depth,
    )
    if preserve_raw and raw is not None:
        flat["_raw"] = raw
    return flat


def flatten_records(
    records: Iterator[Dict[str, Any]],
    separator: str = ".",
    max_depth: Optional[int] = None,
) -> Iterator[Dict[str, Any]]:
    """Yield flattened versions of each record in the stream."""
    for record in records:
        yield flatten_record(record, separator=separator, max_depth=max_depth)
