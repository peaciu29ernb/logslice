"""Command-line entry point for logslice."""

import argparse
import sys
from typing import Optional

from logslice.reader import iter_records
from logslice.filter import parse_timestamp, filter_records
from logslice.output import write_records, OutputFormat


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="logslice",
        description="Filter and slice structured log files by time range or field patterns.",
    )
    p.add_argument("file", nargs="?", help="Log file to read (default: stdin)")
    p.add_argument("--from", dest="from_ts", metavar="TIMESTAMP",
                   help="Include records at or after this timestamp")
    p.add_argument("--to", dest="to_ts", metavar="TIMESTAMP",
                   help="Include records at or before this timestamp")
    p.add_argument("--match", metavar="FIELD=PATTERN", action="append", default=[],
                   help="Filter by field pattern (repeatable)")
    p.add_argument("--format", dest="fmt", choices=["json", "logfmt", "raw"],
                   default="json", help="Output format (default: json)")
    p.add_argument("--ts-field", dest="ts_field", default="ts",
                   help="Name of the timestamp field (default: ts)")
    return p


def parse_patterns(match_args: list[str]) -> dict[str, str]:
    patterns: dict[str, str] = {}
    for item in match_args:
        if "=" not in item:
            raise ValueError(f"--match value must be FIELD=PATTERN, got: {item!r}")
        field, _, pattern = item.partition("=")
        patterns[field.strip()] = pattern.strip()
    return patterns


def main(argv: Optional[list[str]] = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    from_dt = parse_timestamp(args.from_ts) if args.from_ts else None
    to_dt = parse_timestamp(args.to_ts) if args.to_ts else None

    try:
        patterns = parse_patterns(args.match)
    except ValueError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2

    source = open(args.file) if args.file else sys.stdin  # noqa: SIM115
    try:
        records = iter_records(source)
        filtered = filter_records(
            records,
            from_time=from_dt,
            to_time=to_dt,
            patterns=patterns,
            ts_field=args.ts_field,
        )
        write_records(filtered, fmt=args.fmt)
    finally:
        if args.file:
            source.close()

    return 0


if __name__ == "__main__":  # pragma: no cover
    sys.exit(main())
