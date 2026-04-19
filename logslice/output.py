"""Output formatting for logslice records."""

import json
import sys
from typing import IO, Iterable, Literal

OutputFormat = Literal["json", "logfmt", "raw"]


def format_as_json(record: dict) -> str:
    """Serialize a record as compact JSON."""
    return json.dumps(record, default=str)


def format_as_logfmt(record: dict) -> str:
    """Serialize a record as logfmt key=value pairs."""
    parts = []
    for key, value in record.items():
        if key == "_raw":
            continue
        str_value = str(value)
        if " " in str_value or "=" in str_value or '"' in str_value:
            str_value = '"' + str_value.replace('"', '\\"') + '"'
        parts.append(f"{key}={str_value}")
    return " ".join(parts)


def format_record(record: dict, fmt: OutputFormat) -> str:
    """Format a single record according to the chosen output format."""
    if fmt == "raw":
        return record.get("_raw", format_as_json(record))
    if fmt == "logfmt":
        return format_as_logfmt(record)
    return format_as_json(record)


def write_records(
    records: Iterable[dict],
    fmt: OutputFormat = "json",
    out: IO[str] = sys.stdout,
) -> int:
    """Write formatted records to *out*. Returns count of records written."""
    count = 0
    for record in records:
        out.write(format_record(record, fmt))
        out.write("\n")
        count += 1
    return count
