"""Structured log line parser supporting JSON and logfmt formats."""

import json
from typing import Optional


def parse_json_line(line: str) -> Optional[dict]:
    """Attempt to parse a line as JSON. Returns dict or None."""
    line = line.strip()
    if not line:
        return None
    try:
        obj = json.loads(line)
        if isinstance(obj, dict):
            return obj
    except json.JSONDecodeError:
        pass
    return None


def parse_logfmt_line(line: str) -> Optional[dict]:
    """Attempt to parse a line in logfmt key=value format. Returns dict or None."""
    line = line.strip()
    if not line:
        return None
    result = {}
    i = 0
    while i < len(line):
        # skip spaces
        while i < len(line) and line[i] == ' ':
            i += 1
        if i >= len(line):
            break
        # read key
        eq = line.find('=', i)
        if eq == -1:
            break
        key = line[i:eq]
        i = eq + 1
        # read value
        if i < len(line) and line[i] == '"':
            end = line.find('"', i + 1)
            if end == -1:
                value = line[i + 1:]
                i = len(line)
            else:
                value = line[i + 1:end]
                i = end + 1
        else:
            space = line.find(' ', i)
            if space == -1:
                value = line[i:]
                i = len(line)
            else:
                value = line[i:space]
                i = space
        result[key] = value
    return result if result else None


def parse_line(line: str) -> Optional[dict]:
    """Auto-detect format and parse a log line."""
    stripped = line.strip()
    if stripped.startswith('{'):
        return parse_json_line(stripped)
    return parse_logfmt_line(stripped)
