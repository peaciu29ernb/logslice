"""Field validation for log records — check required fields and value constraints."""

from typing import Any, Dict, Iterable, Iterator, List, Optional, Tuple
import re

Record = Dict[str, Any]


def check_required_fields(record: Record, required: List[str]) -> List[str]:
    """Return a list of required field names missing from the record."""
    return [f for f in required if f not in record]


def check_field_pattern(record: Record, field: str, pattern: str) -> bool:
    """Return True if record[field] matches the regex pattern, False otherwise.

    Returns False if the field is absent or the pattern is invalid.
    """
    value = record.get(field)
    if value is None:
        return False
    try:
        return bool(re.search(pattern, str(value)))
    except re.error:
        return False


def validate_record(
    record: Record,
    required: Optional[List[str]] = None,
    field_patterns: Optional[Dict[str, str]] = None,
) -> Tuple[bool, List[str]]:
    """Validate a single record against required fields and field patterns.

    Returns (is_valid, list_of_error_messages).
    """
    errors: List[str] = []

    if required:
        missing = check_required_fields(record, required)
        for field in missing:
            errors.append(f"missing required field: {field!r}")

    if field_patterns:
        for field, pattern in field_patterns.items():
            if field in record and not check_field_pattern(record, field, pattern):
                errors.append(
                    f"field {field!r} value {record[field]!r} does not match pattern {pattern!r}"
                )

    return (len(errors) == 0, errors)


def filter_valid_records(
    records: Iterable[Record],
    required: Optional[List[str]] = None,
    field_patterns: Optional[Dict[str, str]] = None,
    invert: bool = False,
) -> Iterator[Record]:
    """Yield records that pass (or fail, if invert=True) validation."""
    for record in records:
        is_valid, _ = validate_record(record, required=required, field_patterns=field_patterns)
        if is_valid != invert:
            yield record
