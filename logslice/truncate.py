"""Truncate long field values in log records."""

from typing import Iterable, Iterator


DEFAULT_MAX_LENGTH = 200
DEFAULT_SUFFIX = "..."


def truncate_value(value: str, max_length: int, suffix: str = DEFAULT_SUFFIX) -> str:
    """Truncate a string value to max_length, appending suffix if truncated."""
    if not isinstance(value, str):
        return value
    if len(value) <= max_length:
        return value
    cut = max(0, max_length - len(suffix))
    return value[:cut] + suffix


def truncate_fields(
    record: dict,
    fields: list[str] | None,
    max_length: int,
    suffix: str = DEFAULT_SUFFIX,
) -> dict:
    """Return a new record with specified fields (or all string fields) truncated.

    The ``_raw`` key is always preserved unchanged.
    """
    result = dict(record)
    for key, value in record.items():
        if key == "_raw":
            continue
        if fields is not None and key not in fields:
            continue
        if isinstance(value, str):
            result[key] = truncate_value(value, max_length, suffix)
    return result


def truncate_records(
    records: Iterable[dict],
    fields: list[str] | None = None,
    max_length: int = DEFAULT_MAX_LENGTH,
    suffix: str = DEFAULT_SUFFIX,
) -> Iterator[dict]:
    """Yield records with long field values truncated."""
    for record in records:
        yield truncate_fields(record, fields, max_length, suffix)
