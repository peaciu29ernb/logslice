"""Field casting: apply explicit type conversions to record fields."""

from typing import Any, Dict, Iterable, List, Optional


CAST_TYPES = {"int", "float", "str", "bool"}


def _cast_value(value: Any, to_type: str) -> Any:
    """Cast a single value to the given type string.

    Returns the original value if casting fails or the type is unknown.
    """
    if to_type not in CAST_TYPES:
        return value
    try:
        if to_type == "int":
            return int(float(value))
        if to_type == "float":
            return float(value)
        if to_type == "str":
            return str(value)
        if to_type == "bool":
            if isinstance(value, bool):
                return value
            if isinstance(value, str):
                return value.strip().lower() not in ("false", "0", "no", "")
            return bool(value)
    except (ValueError, TypeError):
        return value
    return value


def cast_fields(
    record: Dict[str, Any],
    casts: Dict[str, str],
) -> Dict[str, Any]:
    """Return a new record with specified fields cast to new types.

    Fields not listed in *casts* are passed through unchanged.
    The ``_raw`` key is always preserved as-is.
    """
    result = dict(record)
    for field, to_type in casts.items():
        if field == "_raw":
            continue
        if field in result:
            result[field] = _cast_value(result[field], to_type)
    return result


def cast_records(
    records: Iterable[Dict[str, Any]],
    casts: Dict[str, str],
) -> Iterable[Dict[str, Any]]:
    """Yield records with *casts* applied to each."""
    for record in records:
        yield cast_fields(record, casts)


def parse_cast_args(args: List[str]) -> Dict[str, str]:
    """Parse a list of ``field:type`` strings into a mapping.

    Raises ``ValueError`` for malformed entries or unsupported types.
    """
    casts: Dict[str, str] = {}
    for arg in args:
        if ":" not in arg:
            raise ValueError(f"Invalid cast spec (expected field:type): {arg!r}")
        field, _, to_type = arg.partition(":")
        field = field.strip()
        to_type = to_type.strip()
        if not field:
            raise ValueError(f"Empty field name in cast spec: {arg!r}")
        if to_type not in CAST_TYPES:
            raise ValueError(
                f"Unsupported cast type {to_type!r}. Choose from: {sorted(CAST_TYPES)}"
            )
        casts[field] = to_type
    return casts
