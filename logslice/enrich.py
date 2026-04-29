"""Enrich log records by looking up field values in an external mapping file."""

from __future__ import annotations

import csv
import json
from typing import Dict, Iterable, Iterator, Optional

Record = Dict[str, object]


def load_mapping(path: str, key_field: str, value_field: str) -> Dict[str, str]:
    """Load a CSV or JSON file and return a dict mapping key_field -> value_field."""
    mapping: Dict[str, str] = {}
    if path.endswith(".json"):
        with open(path, encoding="utf-8") as fh:
            data = json.load(fh)
        if isinstance(data, list):
            for row in data:
                if key_field in row and value_field in row:
                    mapping[str(row[key_field])] = str(row[value_field])
        elif isinstance(data, dict):
            mapping = {str(k): str(v) for k, v in data.items()}
    else:
        with open(path, newline="", encoding="utf-8") as fh:
            reader = csv.DictReader(fh)
            for row in reader:
                if key_field in row and value_field in row:
                    mapping[row[key_field]] = row[value_field]
    return mapping


def enrich_record(
    record: Record,
    lookup_field: str,
    mapping: Dict[str, str],
    dest_field: str,
    default: Optional[str] = None,
) -> Record:
    """Return a new record with dest_field populated from mapping."""
    value = record.get(lookup_field)
    if value is None:
        enriched_value: Optional[str] = default
    else:
        enriched_value = mapping.get(str(value), default)
    result = dict(record)
    result[dest_field] = enriched_value
    return result


def enrich_records(
    records: Iterable[Record],
    lookup_field: str,
    mapping: Dict[str, str],
    dest_field: str,
    default: Optional[str] = None,
    skip_missing: bool = False,
) -> Iterator[Record]:
    """Yield enriched records. If skip_missing, drop records with no mapping hit."""
    for record in records:
        value = record.get(lookup_field)
        hit = mapping.get(str(value)) if value is not None else None
        if hit is None and skip_missing:
            continue
        yield enrich_record(record, lookup_field, mapping, dest_field, default)
