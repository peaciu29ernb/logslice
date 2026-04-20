"""Wiring helpers to integrate annotation into the main CLI pipeline.

This module is intentionally thin — it imports the building blocks from
cli_annotate and annotate, then exposes a single ``run_annotate_pipeline``
function that the main CLI can call.
"""

from __future__ import annotations

import argparse
from typing import Iterable

from logslice.annotate import annotate_records
from logslice.cli_annotate import extract_annotate_kwargs


def run_annotate_pipeline(
    records: Iterable[dict],
    args: argparse.Namespace,
) -> Iterable[dict]:
    """Apply CLI-specified annotations to *records* and return the stream.

    If no annotation flags were supplied the original iterator is returned
    unchanged so there is zero overhead on the hot path.

    Parameters
    ----------
    records:
        Iterable of parsed log record dicts (each may contain ``_raw``).
    args:
        Parsed :class:`argparse.Namespace` that was built with
        :func:`~logslice.cli_annotate.register_annotate_args`.

    Returns
    -------
    Iterable[dict]
        Possibly-annotated record stream.
    """
    annotations = extract_annotate_kwargs(args)
    if not annotations:
        return records
    return annotate_records(records, annotations)


def describe_annotations(args: argparse.Namespace) -> list[str]:
    """Return human-readable descriptions of active annotation steps.

    Useful for ``--verbose`` / debug output in the main CLI.
    """
    lines: list[str] = []
    for spec in getattr(args, "add_fields", []) or []:
        lines.append(f"add-field: {spec}")
    for spec in getattr(args, "extracts", []) or []:
        lines.append(f"extract: {spec}")
    for spec in getattr(args, "templates", []) or []:
        lines.append(f"template: {spec}")
    return lines
