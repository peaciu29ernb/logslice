"""Tests for logslice.rate and logslice.cli_rate."""

from __future__ import annotations

import argparse
from datetime import datetime, timezone

import pytest

from logslice.rate import floor_to_second, format_rate_summary, rate_limit_records
from logslice.cli_rate import (
    extract_rate_kwargs,
    is_rate_active,
    register_rate_args,
    validate_rate_args,
)


def make_record(ts: str, msg: str = "hello") -> dict:
    return {"timestamp": ts, "msg": msg, "_raw": f'timestamp={ts} msg={msg}'}


# --- floor_to_second ---

def test_floor_to_second_aligns_down():
    dt = datetime(2024, 1, 1, 12, 0, 37, tzinfo=timezone.utc)
    result = floor_to_second(dt, 10)
    assert result == datetime(2024, 1, 1, 12, 0, 30, tzinfo=timezone.utc)


def test_floor_to_second_already_aligned():
    dt = datetime(2024, 1, 1, 12, 0, 30, tzinfo=timezone.utc)
    result = floor_to_second(dt, 10)
    assert result == dt


def test_floor_to_second_one_second_interval():
    dt = datetime(2024, 1, 1, 0, 0, 5, 999999, tzinfo=timezone.utc)
    result = floor_to_second(dt, 1)
    assert result == datetime(2024, 1, 1, 0, 0, 5, tzinfo=timezone.utc)


# --- rate_limit_records ---

def test_rate_limit_allows_up_to_max():
    records = [make_record("2024-01-01T00:00:01Z") for _ in range(5)]
    result = list(rate_limit_records(iter(records), max_per_bucket=3))
    assert len(result) == 3


def test_rate_limit_passes_through_no_timestamp():
    records = [{"msg": "no time", "_raw": "msg=no time"} for _ in range(5)]
    result = list(rate_limit_records(iter(records), max_per_bucket=2))
    assert len(result) == 5


def test_rate_limit_passes_through_unparseable_timestamp():
    records = [{"timestamp": "not-a-date", "_raw": "x"} for _ in range(4)]
    result = list(rate_limit_records(iter(records), max_per_bucket=1))
    assert len(result) == 4


def test_rate_limit_separate_buckets():
    records = [
        make_record("2024-01-01T00:00:01Z"),
        make_record("2024-01-01T00:00:01Z"),
        make_record("2024-01-01T00:00:02Z"),
        make_record("2024-01-01T00:00:02Z"),
    ]
    result = list(rate_limit_records(iter(records), max_per_bucket=1, interval=1))
    assert len(result) == 2


def test_rate_limit_zero_max_yields_nothing():
    records = [make_record("2024-01-01T00:00:01Z") for _ in range(3)]
    result = list(rate_limit_records(iter(records), max_per_bucket=0))
    assert result == []


def test_rate_limit_custom_time_field():
    records = [
        {"ts": "2024-01-01T00:00:01Z", "_raw": "x"},
        {"ts": "2024-01-01T00:00:01Z", "_raw": "y"},
    ]
    result = list(
        rate_limit_records(iter(records), max_per_bucket=1, time_field="ts")
    )
    assert len(result) == 1


# --- format_rate_summary ---

def test_format_rate_summary_empty():
    assert format_rate_summary({}) == "(no data)"


def test_format_rate_summary_has_header():
    bucket = datetime(2024, 1, 1, 0, 0, 0, tzinfo=timezone.utc)
    output = format_rate_summary({bucket: 7})
    assert "bucket" in output
    assert "7" in output


# --- CLI helpers ---

def make_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser()
    register_rate_args(p)
    return p


def test_register_adds_rate_limit():
    p = make_parser()
    args = p.parse_args(["--rate-limit", "5"])
    assert args.rate_limit == 5


def test_register_defaults():
    p = make_parser()
    args = p.parse_args([])
    assert args.rate_limit is None
    assert args.rate_interval == 1
    assert args.rate_field == "timestamp"


def test_is_rate_active_false_when_none():
    p = make_parser()
    args = p.parse_args([])
    assert not is_rate_active(args)


def test_is_rate_active_true_when_set():
    p = make_parser()
    args = p.parse_args(["--rate-limit", "10"])
    assert is_rate_active(args)


def test_extract_rate_kwargs():
    p = make_parser()
    args = p.parse_args(["--rate-limit", "3", "--rate-interval", "5", "--rate-field", "ts"])
    kwargs = extract_rate_kwargs(args)
    assert kwargs == {"max_per_bucket": 3, "interval": 5, "time_field": "ts"}


def test_validate_rate_args_negative_limit():
    p = make_parser()
    args = p.parse_args(["--rate-limit", "-1"])
    errors = validate_rate_args(args)
    assert any("rate-limit" in e for e in errors)


def test_validate_rate_args_zero_interval():
    p = make_parser()
    args = p.parse_args(["--rate-limit", "1", "--rate-interval", "0"])
    errors = validate_rate_args(args)
    assert any("rate-interval" in e for e in errors)


def test_validate_rate_args_valid():
    p = make_parser()
    args = p.parse_args(["--rate-limit", "10", "--rate-interval", "60"])
    assert validate_rate_args(args) == []
