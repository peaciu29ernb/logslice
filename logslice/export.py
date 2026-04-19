"""Export records to CSV or TSV formats."""

import csv
import io
from typing import Iterable, List, Optional


def collect_fieldnames(records: List[dict], exclude: Optional[List[str]] = None) -> List[str]:
    """Collect ordered unique field names from records, excluding internal keys."""
    exclude_set = set(exclude or ["_raw"])
    seen = []
    seen_set = set()
    for record in records:
        for key in record:
            if key not in exclude_set and key not in seen_set:
                seen.append(key)
                seen_set.add(key)
    return seen


def format_as_csv(records: List[dict], fieldnames: Optional[List[str]] = None, delimiter: str = ",") -> str:
    """Format records as CSV/TSV string with header row."""
    if not records:
        return ""
    fields = fieldnames or collect_fieldnames(records)
    buf = io.StringIO()
    writer = csv.DictWriter(
        buf,
        fieldnames=fields,
        delimiter=delimiter,
        extrasaction="ignore",
        lineterminator="\n",
    )
    writer.writeheader()
    for record in records:
        writer.writerow({f: record.get(f, "") for f in fields})
    return buf.getvalue()


def write_export(records: Iterable[dict], fmt: str = "csv", fieldnames: Optional[List[str]] = None) -> str:
    """Consume records iterable and return formatted export string."""
    record_list = list(records)
    delimiter = "\t" if fmt == "tsv" else ","
    return format_as_csv(record_list, fieldnames=fieldnames, delimiter=delimiter)
