"""Tests for logslice.parser module."""

import pytest
from logslice.parser import parse_json_line, parse_logfmt_line, parse_line


class TestParseJsonLine:
    def test_valid_json_object(self):
        result = parse_json_line('{"level": "info", "msg": "started"}')
        assert result == {'level': 'info', 'msg': 'started'}

    def test_invalid_json_returns_none(self):
        assert parse_json_line('not json') is None

    def test_json_array_returns_none(self):
        assert parse_json_line('[1, 2, 3]') is None

    def test_empty_line_returns_none(self):
        assert parse_json_line('') is None

    def test_whitespace_stripped(self):
        result = parse_json_line('  {"k": "v"}  ')
        assert result == {'k': 'v'}


class TestParseLogfmtLine:
    def test_simple_pairs(self):
        result = parse_logfmt_line('level=info msg=started')
        assert result == {'level': 'info', 'msg': 'started'}

    def test_quoted_value(self):
        result = parse_logfmt_line('msg="hello world" level=warn')
        assert result == {'msg': 'hello world', 'level': 'warn'}

    def test_empty_line_returns_none(self):
        assert parse_logfmt_line('') is None

    def test_no_equals_returns_none(self):
        assert parse_logfmt_line('just some text') is None


class TestParseLine:
    def test_detects_json(self):
        result = parse_line('{"ts": "2024-01-01", "level": "debug"}')
        assert result['level'] == 'debug'

    def test_detects_logfmt(self):
        result = parse_line('ts=2024-01-01 level=debug')
        assert result['level'] == 'debug'

    def test_blank_line_returns_none(self):
        assert parse_line('   ') is None
