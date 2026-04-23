"""Tests for logslice.join and logslice.cli_join."""

import argparse
import pytest

from logslice.join import index_by_key, inner_join, left_join, join_records
from logslice.cli_join import register_join_args, extract_join_kwargs


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

LEFT = [
    {"id": "1", "msg": "hello", "__raw__": "id=1 msg=hello"},
    {"id": "2", "msg": "world", "__raw__": "id=2 msg=world"},
    {"id": "3", "msg": "orphan", "__raw__": "id=3 msg=orphan"},
]

RIGHT = [
    {"id": "1", "env": "prod"},
    {"id": "2", "env": "staging"},
    {"id": "4", "env": "dev"},
]


# ---------------------------------------------------------------------------
# index_by_key
# ---------------------------------------------------------------------------

def test_index_by_key_basic():
    idx = index_by_key(RIGHT, "id")
    assert "1" in idx
    assert idx["1"] == [{"id": "1", "env": "prod"}]


def test_index_by_key_missing_field_skipped():
    records = [{"id": "1"}, {"env": "prod"}]  # second has no 'id'
    idx = index_by_key(records, "id")
    assert list(idx.keys()) == ["1"]


def test_index_by_key_multiple_matches():
    records = [{"id": "1", "v": "a"}, {"id": "1", "v": "b"}]
    idx = index_by_key(records, "id")
    assert len(idx["1"]) == 2


# ---------------------------------------------------------------------------
# inner_join
# ---------------------------------------------------------------------------

def test_inner_join_returns_only_matched():
    idx = index_by_key(RIGHT, "id")
    results = list(inner_join(LEFT, idx, "id"))
    assert len(results) == 2  # id=3 has no match


def test_inner_join_merges_fields():
    idx = index_by_key(RIGHT, "id")
    results = list(inner_join(LEFT, idx, "id"))
    assert results[0]["right_env"] == "prod"
    assert results[1]["right_env"] == "staging"


def test_inner_join_preserves_raw():
    idx = index_by_key(RIGHT, "id")
    results = list(inner_join(LEFT, idx, "id"))
    assert results[0]["__raw__"] == "id=1 msg=hello"


def test_inner_join_does_not_duplicate_key():
    idx = index_by_key(RIGHT, "id")
    results = list(inner_join(LEFT, idx, "id"))
    # 'id' field from right should not appear as right_id
    assert "right_id" not in results[0]


# ---------------------------------------------------------------------------
# left_join
# ---------------------------------------------------------------------------

def test_left_join_keeps_unmatched():
    idx = index_by_key(RIGHT, "id")
    results = list(left_join(LEFT, idx, "id"))
    assert len(results) == 3  # id=3 passes through


def test_left_join_unmatched_has_no_prefix_fields():
    idx = index_by_key(RIGHT, "id")
    results = list(left_join(LEFT, idx, "id"))
    orphan = next(r for r in results if r["id"] == "3")
    assert "right_env" not in orphan


# ---------------------------------------------------------------------------
# join_records
# ---------------------------------------------------------------------------

def test_join_records_inner():
    results = list(join_records(LEFT, RIGHT, key="id", how="inner"))
    assert len(results) == 2


def test_join_records_left():
    results = list(join_records(LEFT, RIGHT, key="id", how="left"))
    assert len(results) == 3


def test_join_records_custom_prefix():
    results = list(join_records(LEFT, RIGHT, key="id", how="inner", prefix="r_"))
    assert "r_env" in results[0]


# ---------------------------------------------------------------------------
# cli_join
# ---------------------------------------------------------------------------

def make_parser():
    p = argparse.ArgumentParser()
    register_join_args(p)
    return p


def test_register_adds_join_file():
    p = make_parser()
    args = p.parse_args(["--join-file", "other.log"])
    assert args.join_file == "other.log"


def test_register_adds_join_key():
    p = make_parser()
    args = p.parse_args(["--join-key", "request_id"])
    assert args.join_key == "request_id"


def test_extract_join_kwargs_empty_when_no_file():
    p = make_parser()
    args = p.parse_args([])
    assert extract_join_kwargs(args) == {}


def test_extract_join_kwargs_raises_without_key():
    p = make_parser()
    args = p.parse_args(["--join-file", "other.log"])
    with pytest.raises(ValueError, match="--join-key"):
        extract_join_kwargs(args)


def test_extract_join_kwargs_full():
    p = make_parser()
    args = p.parse_args(["--join-file", "f.log", "--join-key", "id", "--join-how", "left", "--join-prefix", "r_"])
    kwargs = extract_join_kwargs(args)
    assert kwargs["key"] == "id"
    assert kwargs["how"] == "left"
    assert kwargs["prefix"] == "r_"
