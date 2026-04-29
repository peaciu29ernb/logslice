"""Integration helpers: wire enrich into a processing pipeline."""

from __future__ import annotations

import argparse
from typing import Iterator

from logslice.cli_enrich import extract_enrich_kwargs, is_enrich_active
from logslice.enrich import enrich_records, load_mapping

Record = dict


def run_enrich_pipeline(
    records: Iterator[Record],
    args: argparse.Namespace,
) -> Iterator[Record]:
    """If enrich args are present, apply enrichment; otherwise pass through."""
    if not is_enrich_active(args):
        yield from records
        return

    kwargs = extract_enrich_kwargs(args)
    mapping = load_mapping(
        kwargs["enrich_file"],
        kwargs["key_field"],
        kwargs["value_field"],
    )
    yield from enrich_records(
        records,
        lookup_field=kwargs["lookup_field"],
        mapping=mapping,
        dest_field=kwargs["dest_field"],
        default=kwargs["default"],
        skip_missing=kwargs["skip_missing"],
    )


def describe_enrich(args: argparse.Namespace) -> str:
    """Return a human-readable summary of the active enrich configuration."""
    if not is_enrich_active(args):
        return "enrich: inactive"
    kwargs = extract_enrich_kwargs(args)
    parts = [
        f"file={kwargs['enrich_file']}",
        f"on={kwargs['lookup_field']}",
        f"dest={kwargs['dest_field']}",
    ]
    if kwargs["default"] is not None:
        parts.append(f"default={kwargs['default']}")
    if kwargs["skip_missing"]:
        parts.append("skip_missing=true")
    return "enrich: " + ", ".join(parts)
