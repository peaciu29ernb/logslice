"""Integration helpers that wire the label feature into the main pipeline."""

from __future__ import annotations

import argparse
from typing import Any, Dict, Iterable, Iterator

from logslice.label import label_records, Rule
from logslice.cli_label import (
    is_label_active,
    extract_label_kwargs,
    describe_label,
)

Record = Dict[str, Any]


def run_label_pipeline(
    records: Iterable[Record],
    args: argparse.Namespace,
) -> Iterator[Record]:
    """Apply label rules from *args* to *records* if the feature is active.

    Passes records through unchanged when no rules are configured.
    """
    if not is_label_active(args):
        yield from records
        return

    kwargs = extract_label_kwargs(args)
    yield from label_records(records, **kwargs)


def describe_label_pipeline(args: argparse.Namespace) -> str:
    """Return a human-readable description of the label pipeline stage.

    Returns an empty string when the feature is inactive.
    """
    if not is_label_active(args):
        return ""

    try:
        kwargs = extract_label_kwargs(args)
    except ValueError:
        return "label: (invalid configuration)"

    rules: list[Rule] = kwargs.get("rules", [])
    dest: str = kwargs.get("dest", "label")
    default = kwargs.get("default")
    multi: bool = kwargs.get("multi", False)

    parts = [describe_label(rules)]
    parts.append(f"dest={dest!r}")
    if default is not None:
        parts.append(f"default={default!r}")
    if multi:
        parts.append("multi=True")
    return "label: " + ", ".join(parts)
