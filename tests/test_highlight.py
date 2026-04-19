import pytest
from logslice.highlight import (
    colorize,
    highlight_key,
    highlight_value,
    highlight_record,
    should_use_color,
    ANSI_RESET,
    ANSI_YELLOW,
    ANSI_BOLD,
    ANSI_CYAN,
    ANSI_RED,
)


def test_colorize_wraps_text():
    result = colorize("hello", ANSI_CYAN)
    assert result.startswith(ANSI_CYAN)
    assert "hello" in result
    assert result.endswith(ANSI_RESET)


def test_highlight_key_uses_bold_yellow():
    result = highlight_key("level")
    assert ANSI_YELLOW in result
    assert ANSI_BOLD in result
    assert "level" in result


def test_highlight_value_no_pattern():
    result = highlight_value("error")
    assert ANSI_CYAN in result
    assert "error" in result


def test_highlight_value_with_pattern_marks_match():
    result = highlight_value("some error occurred", pattern="error")
    assert ANSI_RED in result
    assert "error" in result


def test_highlight_value_invalid_pattern_fallback():
    result = highlight_value("value", pattern="[invalid")
    assert "value" in result


def test_highlight_record_basic():
    record = {"level": "info", "msg": "started"}
    result = highlight_record(record)
    assert "level" in result
    assert "info" in result
    assert "msg" in result
    assert "started" in result


def test_highlight_record_skips_raw():
    record = {"level": "info", "_raw": "level=info"}
    result = highlight_record(record)
    assert "_raw" not in result


def test_highlight_record_quotes_spaces():
    record = {"msg": "hello world"}
    result = highlight_record(record)
    assert '"' in result


def test_should_use_color_force_true():
    assert should_use_color(force=True) is True


def test_should_use_color_force_false():
    assert should_use_color(force=False) is False


def test_should_use_color_non_tty_stream():
    import io
    stream = io.StringIO()
    assert should_use_color(stream=stream) is False
