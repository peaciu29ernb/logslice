"""Tests for logslice.tail and logslice.cli_tail."""

from __future__ import annotations

import argparse
import os
import tempfile
import time
import threading

import pytest

from logslice.tail import tail_records, follow_file
from logslice.cli_tail import register_tail_args, extract_tail_kwargs


def make_records(n: int) -> list[dict]:
    return [{"index": i, "raw": f'{{"index": {i}}}'} for i in range(n)]


# ---------------------------------------------------------------------------
# tail_records
# ---------------------------------------------------------------------------

def test_tail_returns_last_n():
    records = make_records(10)
    result = tail_records(records, 3)
    assert len(result) == 3
    assert result[0]["index"] == 7
    assert result[-1]["index"] == 9


def test_tail_fewer_than_n():
    records = make_records(2)
    result = tail_records(records, 5)
    assert len(result) == 2


def test_tail_empty():
    assert tail_records([], 10) == []


def test_tail_zero():
    assert tail_records(make_records(5), 0) == []


# ---------------------------------------------------------------------------
# follow_file
# ---------------------------------------------------------------------------

def test_follow_file_yields_new_lines():
    with tempfile.NamedTemporaryFile(mode="w", suffix=".log", delete=False) as fh:
        path = fh.name

    collected: list[dict] = []
    stop = threading.Event()

    def _write():
        time.sleep(0.1)
        with open(path, "a") as f:
            f.write('{"msg": "hello"}\n')
            f.write('{"msg": "world"}\n')
        time.sleep(0.2)
        stop.set()

    writer = threading.Thread(target=_write, daemon=True)
    writer.start()

    gen = follow_file(path, poll_interval=0.05)
    deadline = time.time() + 2.0
    while not stop.is_set() or len(collected) < 2:
        if time.time() > deadline:
            break
        try:
            record = next(gen)
            collected.append(record)
        except StopIteration:
            break

    os.unlink(path)
    assert any(r.get("msg") == "hello" for r in collected)
    assert any(r.get("msg") == "world" for r in collected)


# ---------------------------------------------------------------------------
# cli_tail helpers
# ---------------------------------------------------------------------------

def make_parser():
    p = argparse.ArgumentParser()
    register_tail_args(p)
    return p


def test_register_adds_tail_flag():
    p = make_parser()
    args = p.parse_args(["-n", "20"])
    assert args.tail == 20


def test_register_adds_follow_flag():
    p = make_parser()
    args = p.parse_args(["--follow"])
    assert args.follow is True


def test_extract_defaults():
    p = make_parser()
    args = p.parse_args([])
    kwargs = extract_tail_kwargs(args)
    assert kwargs == {"tail": None, "follow": False}


def test_extract_values():
    p = make_parser()
    args = p.parse_args(["--tail", "5", "--follow"])
    kwargs = extract_tail_kwargs(args)
    assert kwargs["tail"] == 5
    assert kwargs["follow"] is True
