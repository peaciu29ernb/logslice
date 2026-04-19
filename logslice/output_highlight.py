"""Integration of highlight into record output pipeline."""
import sys
from typing import Iterable, Optional, TextIO

from logslice.highlight import highlight_record, should_use_color


def write_highlighted_records(
    records: Iterable[dict],
    patterns: Optional[list] = None,
    force_color: Optional[bool] = None,
    out: TextIO = None,
) -> int:
    """Write records with terminal highlighting. Returns count written."""
    if out is None:
        out = sys.stdout

    use_color = should_use_color(force=force_color, stream=out)
    count = 0

    for record in records:
        if use_color:
            line = highlight_record(record, patterns=patterns)
        else:
            # Fallback: plain logfmt without color
            from logslice.output import format_as_logfmt
            line = format_as_logfmt(record)
        out.write(line + "\n")
        count += 1

    return count
