"""Tests for logslice.filter module."""

from datetime import datetime

import pytest

from logslice.filter import (
    filter_records,
    parse_timestamp,
    record_in_time_range,
    record_matches_pattern,
)


def test_parse_timestamp_iso_utc():
    dt = parse_timestamp("2024-03-15T12:00:00Z")
    assert dt == datetime(2024, 3, 15, 12, 0, 0)


def test_parse_timestamp_with_microseconds():
    dt = parse_timestamp("2024-03-15T12:00:00.123456Z")
    assert dt == datetime(2024, 3, 15, 12, 0, 0, 123456)


def test_parse_timestamp_space_separated():
    dt = parse_timestamp("2024-03-15 12:00:00")
    assert dt == datetime(2024, 3, 15, 12, 0, 0)


def test_parse_timestamp_invalid_returns_none():
    assert parse_timestamp("not-a-date") is None


def test_parse_timestamp_empty_string_returns_none():
    assert parse_timestamp("") is None


def test_record_in_time_range_within():
    record = {"timestamp": "2024-03-15T12:00:00Z"}
    assert record_in_time_range(
        record, "timestamp",
        datetime(2024, 3, 15, 11, 0),
        datetime(2024, 3, 15, 13, 0),
    )


def test_record_in_time_range_before_start():
    record = {"timestamp": "2024-03-15T10:00:00Z"}
    assert not record_in_time_range(
        record, "timestamp", datetime(2024, 3, 15, 11, 0), None
    )


def test_record_in_time_range_after_end():
    record = {"timestamp": "2024-03-15T15:00:00Z"}
    assert not record_in_time_range(
        record, "timestamp", None, datetime(2024, 3, 15, 13, 0)
    )


def test_record_in_time_range_missing_field():
    assert not record_in_time_range(
        {}, "timestamp", datetime(2024, 1, 1), None
    )


def test_record_in_time_range_no_bounds():
    assert record_in_time_range({}, "timestamp", None, None)


def test_record_matches_pattern_found():
    assert record_matches_pattern({"level": "error"}, "level", "err")


def test_record_matches_pattern_not_found():
    assert not record_matches_pattern({"level": "info"}, "level", "err")


def test_record_matches_pattern_missing_field():
    assert not record_matches_pattern({}, "level", "err")


def test_filter_records_by_time():
    records = [
        {"timestamp": "2024-03-15T10:00:00Z", "msg": "early"},
        {"timestamp": "2024-03-15T12:00:00Z", "msg": "mid"},
        {"timestamp": "2024-03-15T14:00:00Z", "msg": "late"},
    ]
    result = list(filter_records(
        iter(records),
        start=datetime(2024, 3, 15, 11, 0),
        end=datetime(2024, 3, 15, 13, 0),
    ))
    assert len(result) == 1
    assert result[0]["msg"] == "mid"


def test_filter_records_by_field_pattern():
    records = [
        {"timestamp": "2024-03-15T12:00:00Z", "level": "info", "msg": "ok"},
        {"timestamp": "2024-03-15T12:01:00Z", "level": "error", "msg": "fail"},
    ]
    result = list(filter_records(
        iter(records), field_patterns={"level": "error"}
    ))
    assert len(result) == 1
    assert result[0]["msg"] == "fail"


def test_filter_records_combined():
    records = [
        {"timestamp": "2024-03-15T12:00:00Z", "level": "error", "svc": "auth"},
        {"timestamp": "2024-03-15T12:00:00Z", "level": "error", "svc": "api"},
        {"timestamp": "2024-03-15T14:00:00Z", "level": "error", "svc": "auth"},
    ]
    result = list(filter_records(
        iter(records),
