"""Field redaction and masking for sensitive log data."""

import re
from typing import Any, Dict, Iterable, Iterator, List, Optional


REDACTED_PLACEHOLDER = "[REDACTED]"


def redact_fields(
    record: Dict[str, Any],
    fields: List[str],
    placeholder: str = REDACTED_PLACEHOLDER,
) -> Dict[str, Any]:
    """Return a copy of record with specified fields replaced by placeholder."""
    result = dict(record)
    for field in fields:
        if field in result and field != "_raw":
            result[field] = placeholder
    return result


def mask_field_pattern(
    record: Dict[str, Any],
    field: str,
    pattern: str,
    replacement: str = REDACTED_PLACEHOLDER,
) -> Dict[str, Any]:
    """Return a copy of record with regex pattern replaced in the given field value."""
    result = dict(record)
    value = result.get(field)
    if value is None or field == "_raw":
        return result
    try:
        result[field] = re.sub(pattern, replacement, str(value))
    except re.error:
        pass
    return result


def apply_redactions(
    record: Dict[str, Any],
    redact: Optional[List[str]] = None,
    mask_field: Optional[str] = None,
    mask_pattern: Optional[str] = None,
    mask_replacement: str = REDACTED_PLACEHOLDER,
) -> Dict[str, Any]:
    """Apply all configured redaction operations to a record."""
    if redact:
        record = redact_fields(record, redact)
    if mask_field and mask_pattern:
        record = mask_field_pattern(record, mask_field, mask_pattern, mask_replacement)
    return record


def redact_records(
    records: Iterable[Dict[str, Any]],
    redact: Optional[List[str]] = None,
    mask_field: Optional[str] = None,
    mask_pattern: Optional[str] = None,
    mask_replacement: str = REDACTED_PLACEHOLDER,
) -> Iterator[Dict[str, Any]]:
    """Yield records with redaction applied to each."""
    for record in records:
        yield apply_redactions(
            record,
            redact=redact,
            mask_field=mask_field,
            mask_pattern=mask_pattern,
            mask_replacement=mask_replacement,
        )
