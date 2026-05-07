"""patch.py — apply field-level patches (set/delete/default) to log records."""

from typing import Any, Dict, Iterable, Iterator, List, Optional, Tuple


Record = Dict[str, Any]

# Operation types
SET = "set"
DELETE = "delete"
DEFAULT = "default"  # set only if field is absent or None


def parse_patch_arg(arg: str) -> Optional[Tuple[str, str, Any]]:
    """Parse a patch argument string like 'field=value', 'field=', or '~field'.

    Returns (op, field, value) or None if the argument is invalid.
    - '~field'      -> (DELETE, field, None)
    - 'field=value' -> (SET, field, value)
    - '?field=value'-> (DEFAULT, field, value)
    """
    if not arg:
        return None
    if arg.startswith("~"):
        field = arg[1:].strip()
        if not field:
            return None
        return (DELETE, field, None)
    if arg.startswith("?"):
        rest = arg[1:]
        if "=" not in rest:
            return None
        field, _, value = rest.partition("=")
        field = field.strip()
        if not field:
            return None
        return (DEFAULT, field, value)
    if "=" not in arg:
        return None
    field, _, value = arg.partition("=")
    field = field.strip()
    if not field:
        return None
    return (SET, field, value)


def patch_record(
    record: Record,
    ops: List[Tuple[str, str, Any]],
) -> Record:
    """Apply a list of patch operations to a single record.

    Returns a new record dict; the original is not mutated.
    """
    result = dict(record)
    for op, field, value in ops:
        if field == "_raw":
            continue
        if op == SET:
            result[field] = value
        elif op == DELETE:
            result.pop(field, None)
        elif op == DEFAULT:
            if result.get(field) is None:
                result[field] = value
    return result


def patch_records(
    records: Iterable[Record],
    ops: List[Tuple[str, str, Any]],
) -> Iterator[Record]:
    """Apply patch operations to every record in the iterable."""
    for record in records:
        yield patch_record(record, ops)
