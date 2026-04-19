"""Terminal highlighting for matched fields and values."""
import re
from typing import Optional

ANSI_RESET = "\033[0m"
ANSI_BOLD = "\033[1m"
ANSI_YELLOW = "\033[33m"
ANSI_CYAN = "\033[36m"
ANSI_RED = "\033[31m"


def colorize(text: str, color: str) -> str:
    return f"{color}{text}{ANSI_RESET}"


def highlight_value(value: str, pattern: Optional[str] = None) -> str:
    """Highlight a value, optionally emphasizing a matching pattern."""
    if pattern is None:
        return colorize(value, ANSI_CYAN)
    try:
        highlighted = re.sub(
            pattern,
            lambda m: colorize(m.group(0), ANSI_RED),
            value,
        )
        return highlighted
    except re.error:
        return colorize(value, ANSI_CYAN)


def highlight_key(key: str) -> str:
    return colorize(key, ANSI_BOLD + ANSI_YELLOW)


def highlight_record(record: dict, patterns: Optional[list] = None) -> str:
    """Format a record as logfmt with terminal colors applied."""
    parts = []
    for key, value in record.items():
        if key == "_raw":
            continue
        str_value = str(value)
        pattern = patterns[0] if patterns else None
        colored_key = highlight_key(key)
        colored_value = highlight_value(str_value, pattern)
        if " " in str_value:
            parts.append(f'{colored_key}="{colored_value}"')
        else:
            parts.append(f"{colored_key}={colored_value}")
    return " ".join(parts)


def should_use_color(force: Optional[bool] = None, stream=None) -> bool:
    """Determine whether to emit ANSI codes."""
    if force is not None:
        return force
    import sys
    target = stream or sys.stdout
    return hasattr(target, "isatty") and target.isatty()
