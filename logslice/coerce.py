"""Field type coercion for log records."""

from typing import Any, Dict, List, Optional


def coerce_int(value: Any) -> Optional[int]:
    """Try to coerce a value to int. Returns None on failure."""
    try:
        return int(value)
    except (TypeError, ValueError):
        return None


def coerce_float(value: Any) -> Optional[float]:
    """Try to coerce a value to float. Returns None on failure."""
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def coerce_bool(value: Any) -> Optional[bool]:
    """Try to coerce a value to bool from common string representations."""
    if isinstance(value, bool):
        return value
    if isinstance(value, str):
        lowered = value.strip().lower()
        if lowered in ("true", "1", "yes", "on"):
            return True
        if lowered in ("false", "0", "no", "off"):
            return False
    return None


def coerce_field(value: Any, target_type: str) -> Any:
    """Coerce a single field value to the named type.

    Supported types: 'int', 'float', 'bool', 'str'.
    Returns the original value if coercion fails or type is unknown.
    """
    if target_type == "int":
        result = coerce_int(value)
        return result if result is not None else value
    if target_type == "float":
        result = coerce_float(value)
        return result if result is not None else value
    if target_type == "bool":
        result = coerce_bool(value)
        return result if result is not None else value
    if target_type == "str":
        return str(value)
    return value


def coerce_record(
    record: Dict[str, Any],
    coercions: List[tuple],
) -> Dict[str, Any]:
    """Apply a list of (field, type) coercions to a record.

    Returns a new record dict; does not mutate the original.
    The '_raw' key is always preserved unchanged.
    """
    result = dict(record)
    for field, target_type in coercions:
        if field == "_raw":
            continue
        if field in result:
            result[field] = coerce_field(result[field], target_type)
    return result


def coerce_records(records, coercions: List[tuple]):
    """Yield records with field coercions applied."""
    for record in records:
        yield coerce_record(record, coercions)
