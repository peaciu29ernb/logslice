"""Compare two streams of records field-by-field and emit difference records."""

from typing import Iterable, Iterator, Optional


def compare_records(
    left: Iterable[dict],
    right: Iterable[dict],
    key_field: str,
    fields: Optional[list] = None,
    label_left: str = "left",
    label_right: str = "right",
) -> Iterator[dict]:
    """Yield one record per field difference between matched records.

    Records are matched by *key_field*.  Unmatched records from either side
    produce a single row with source=label_left/label_right and value=<missing>.
    """
    left_index: dict = {}
    for rec in left:
        k = rec.get(key_field)
        if k is not None:
            left_index[k] = rec

    right_index: dict = {}
    for rec in right:
        k = rec.get(key_field)
        if k is not None:
            right_index[k] = rec

    all_keys = sorted(set(left_index) | set(right_index), key=str)

    for k in all_keys:
        l_rec = left_index.get(k)
        r_rec = right_index.get(k)

        if l_rec is None:
            yield {key_field: k, "source": label_right, "field": "*", "value": "<missing in left>"}
            continue
        if r_rec is None:
            yield {key_field: k, "source": label_left, "field": "*", "value": "<missing in right>"}
            continue

        compare_fields = fields if fields else sorted(
            set(l_rec) | set(r_rec) - {"_raw"}
        )

        for field in compare_fields:
            if field == "_raw" or field == key_field:
                continue
            lv = l_rec.get(field)
            rv = r_rec.get(field)
            if lv != rv:
                yield {
                    key_field: k,
                    "field": field,
                    label_left: lv,
                    label_right: rv,
                }


def format_compare_table(rows: list, label_left: str = "left", label_right: str = "right") -> str:
    """Render comparison rows as a plain-text table."""
    if not rows:
        return "(no differences)"

    key_col = [r for r in rows[0] if r not in ("field", label_left, label_right)]
    key_field = key_col[0] if key_col else "key"

    header = f"{'KEY':<20} {'FIELD':<20} {label_left.upper():<25} {label_right.upper():<25}"
    sep = "-" * len(header)
    lines = [header, sep]
    for row in rows:
        k = str(row.get(key_field, ""))
        f = str(row.get("field", ""))
        lv = str(row.get(label_left, ""))
        rv = str(row.get(label_right, ""))
        lines.append(f"{k:<20} {f:<20} {lv:<25} {rv:<25}")
    return "\n".join(lines)
