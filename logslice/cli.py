"""Command-line interface for logslice."""
from __future__ import annotations

import argparse
import sys

from logslice.reader import iter_records
from logslice.filter import filter_records
from logslice.output import write_records
from logslice.stats import compute_stats, format_stats
from logslice.aggregate import count_by, format_count_table


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="logslice",
        description="Filter and slice structured log files.",
    )
    p.add_argument("file", nargs="?", help="Log file (default: stdin)")
    p.add_argument("--from", dest="from_ts", metavar="TS", help="Start timestamp (inclusive)")
    p.add_argument("--to", dest="to_ts", metavar="TS", help="End timestamp (inclusive)")
    p.add_argument("-p", "--pattern", dest="patterns", action="append", metavar="FIELD=VALUE",
                   help="Filter field=value pattern (repeatable)")
    p.add_argument("-f", "--format", dest="fmt", choices=["json", "logfmt", "raw"],
                   default="json", help="Output format")
    p.add_argument("--stats", action="store_true", help="Print summary statistics instead of records")
    p.add_argument("--count-by", dest="count_by", metavar="FIELD",
                   help="Print record counts grouped by FIELD")
    return p


def parse_patterns(raw: list[str] | None) -> list[tuple[str, str]]:
    patterns = []
    for item in raw or []:
        if "=" not in item:
            raise SystemExit(f"Invalid pattern (expected field=value): {item!r}")
        field, _, value = item.partition("=")
        patterns.append((field.strip(), value.strip()))
    return patterns


def open_input(path: str | None):
    """Open the input file by path, or return stdin if path is None."""
    if path is None:
        return sys.stdin
    try:
        return open(path)
    except OSError as exc:
        raise SystemExit(f"Cannot open file {path!r}: {exc.strerror}") from exc


def main(argv: list[str] | None = None) -> None:
    parser = build_parser()
    args = parser.parse_args(argv)

    fh = open_input(args.file)
    try:
        patterns = parse_patterns(args.patterns)
        records = iter_records(fh)
        records = filter_records(
            records,
            from_ts=args.from_ts,
            to_ts=args.to_ts,
            patterns=patterns,
        )

        if args.stats:
            stats = compute_stats(records)
            print(format_stats(stats))
        elif args.count_by:
            counter = count_by(records, args.count_by)
            print(format_count_table(counter, title=args.count_by))
        else:
            write_records(records, fmt=args.fmt)
    finally:
        if args.file:
            fh.close()


if __name__ == "__main__":
    main()
