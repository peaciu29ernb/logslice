"""CLI helpers for the --annotate family of flags."""

import argparse
from functools import partial
from typing import Callable, Dict, List

from logslice.annotate import (
    annotate_with_extract,
    annotate_with_template,
    annotate_with_value,
)


def register_annotate_args(parser: argparse.ArgumentParser) -> None:
    """Add annotation-related arguments to *parser*."""
    parser.add_argument(
        "--add-field",
        metavar="FIELD=VALUE",
        action="append",
        dest="add_fields",
        default=[],
        help="Add a static field, e.g. --add-field env=prod",
    )
    parser.add_argument(
        "--extract",
        metavar="SRC:DEST:PATTERN",
        action="append",
        dest="extracts",
        default=[],
        help="Extract regex group 1 from SRC into DEST",
    )
    parser.add_argument(
        "--template",
        metavar="DEST:TEMPLATE",
        action="append",
        dest="templates",
        default=[],
        help="Render a template into DEST, e.g. --template msg:{level}:{message}",
    )


def _parse_add_field(spec: str):
    """Parse 'key=value' into (key, value)."""
    if "=" not in spec:
        raise argparse.ArgumentTypeError(
            f"--add-field requires FIELD=VALUE, got: {spec!r}"
        )
    key, _, value = spec.partition("=")
    return key.strip(), value


def _parse_extract(spec: str):
    """Parse 'src:dest:pattern' into (src, dest, pattern)."""
    parts = spec.split(":", 2)
    if len(parts) != 3:
        raise argparse.ArgumentTypeError(
            f"--extract requires SRC:DEST:PATTERN, got: {spec!r}"
        )
    return parts[0], parts[1], parts[2]


def _parse_template(spec: str):
    """Parse 'dest:template' into (dest, template)."""
    if ":" not in spec:
        raise argparse.ArgumentTypeError(
            f"--template requires DEST:TEMPLATE, got: {spec!r}"
        )
    dest, _, tmpl = spec.partition(":")
    return dest.strip(), tmpl


def extract_annotate_kwargs(args: argparse.Namespace) -> List[Callable[[dict], dict]]:
    """Build a list of annotation callables from parsed CLI args."""
    fns: List[Callable[[dict], dict]] = []

    for spec in getattr(args, "add_fields", []) or []:
        key, value = _parse_add_field(spec)
        fns.append(partial(annotate_with_value, field=key, value=value))

    for spec in getattr(args, "extracts", []) or []:
        src, dest, pattern = _parse_extract(spec)
        fns.append(
            partial(annotate_with_extract, src_field=src, dest_field=dest, pattern=pattern)
        )

    for spec in getattr(args, "templates", []) or []:
        dest, tmpl = _parse_template(spec)
        fns.append(partial(annotate_with_template, dest_field=dest, template=tmpl))

    return fns
