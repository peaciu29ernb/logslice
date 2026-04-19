"""Tests for logslice.reader module."""

import io
import pytest
from unittest.mock import patch, mock_open
from logslice.reader import iter_records


SAMPLE_LOGS = (
    '{"level": "info", "msg": "boot"}\n'
    'level=warn msg="disk low"\n'
    'this is not a parseable line without equals\n'
    '{"level": "error", "msg": "crash"}\n'
)


def test_iter_records_from_file(tmp_path):
    log_file = tmp_path / "app.log"
    log_file.write_text(SAMPLE_LOGS, encoding='utf-8')

    records = list(iter_records(str(log_file)))
    assert len(records) == 3
    assert records[0]['level'] == 'info'
    assert records[1]['level'] == 'warn'
    assert records[2]['level'] == 'error'


def test_iter_records_raw_preserved(tmp_path):
    log_file = tmp_path / "app.log"
    log_file.write_text('{"level": "info"}\n', encoding='utf-8')

    records = list(iter_records(str(log_file)))
    assert records[0]['_raw'] == '{"level": "info"}'


def test_iter_records_skips_unparseable(tmp_path):
    log_file = tmp_path / "app.log"
    log_file.write_text('garbage line\n{"ok": true}\n', encoding='utf-8')

    records = list(iter_records(str(log_file)))
    assert len(records) == 1
    assert records[0]['ok'] is True


def test_iter_records_stdin():
    fake_stdin = io.StringIO('{"source": "stdin"}\n')
    with patch('logslice.reader.sys.stdin', fake_stdin):
        records = list(iter_records('-'))
    assert len(records) == 1
    assert records[0]['source'] == 'stdin'
