"""Template-based output formatting for log records."""

import re
import string
from typing import Any, Dict, Iterable, Iterator, Optional

_FIELD_RE = re.compile(r"\{(\w+)(?::(.*?))?\}")


class _SafeDict(dict):
    """dict subclass that returns '{key}' for missing keys instead of raising."""

    def __missing__(self, key: str) -> str:
        return "{" + key + "}"


def render_template(template: str, record: Dict[str, Any]) -> str:
    """Render a template string against a record.

    Supports standard Python str.format_map style placeholders: {field}.
    Missing fields are left as-is rather than raising KeyError.

    Args:
        template: A format string like "{level} {message} latency={latency_ms}ms"
        record: The log record dict (may contain a '_raw' key which is ignored).

    Returns:
        The rendered string.
    """
    data = {k: v for k, v in record.items() if k != "_raw"}
    try:
        return template.format_map(_SafeDict(data))
    except (ValueError, KeyError):
        return template


def validate_template(template: str) -> Optional[str]:
    """Check whether a template string is syntactically valid.

    Returns an error message string if invalid, or None if valid.
    """
    try:
        # Attempt a parse with an empty safe dict to detect format errors.
        template.format_map(_SafeDict())
        return None
    except (ValueError, KeyError) as exc:
        return str(exc)


def apply_template(
    records: Iterable[Dict[str, Any]],
    template: str,
    dest_field: str = "_rendered",
) -> Iterator[Dict[str, Any]]:
    """Yield records with a new field containing the rendered template.

    Args:
        records: Iterable of log record dicts.
        template: Format string to render for each record.
        dest_field: Name of the field to store the rendered result.

    Yields:
        New record dicts with ``dest_field`` added.
    """
    for record in records:
        rendered = render_template(template, record)
        yield {**record, dest_field: rendered}


def format_records_as_template(
    records: Iterable[Dict[str, Any]],
    template: str,
) -> Iterator[str]:
    """Yield rendered template strings for each record.

    Useful for custom single-line output formats.

    Args:
        records: Iterable of log record dicts.
        template: Format string to render.

    Yields:
        Rendered strings, one per record.
    """
    for record in records:
        yield render_template(template, record)
