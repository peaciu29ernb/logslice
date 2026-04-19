"""Tests for logslice.dedupe module."""

import pytest
from logslice.dedupe import make_key, dedupe_records


def records(*dicts):
    return list(dicts)


# --- make_key ---

def test_make_key_single_field():
    r = {"level": "error", "msg": "oops"}
    assert make_key(r, ["level"]) == ("error",)


def test_make_key_multiple_fields():
    r = {"host": "web1", "level": "warn", "msg": "slow"}
    assert make_key(r, ["host", "level"]) == ("web1", "warn")


def test_make_key_missing_field_is_none():
    r = {"level": "info"}
    assert make_key(r, ["level", "host"]) == ("info", None)


# --- dedupe_records keep=first ---

def test_dedupe_first_removes_duplicates():
    recs = [
        {"id": "1", "msg": "a"},
        {"id": "2", "msg": "b"},
        {"id": "1", "msg": "c"},
    ]
    result = list(dedupe_records(iter(recs), fields=["id"]))
    assert len(result) == 2
    assert result[0]["msg"] == "a"
    assert result[1]["msg"] == "b"


def test_dedupe_first_preserves_order():
    recs = [{"k": i % 3} for i in range(9)]
    result = list(dedupe_records(iter(recs), fields=["k"]))
    assert [r["k"] for r in result] == [0, 1, 2]


# --- dedupe_records keep=last ---

def test_dedupe_last_keeps_latest():
    recs = [
        {"id": "1", "msg": "first"},
        {"id": "2", "msg": "only"},
        {"id": "1", "msg": "last"},
    ]
    result = list(dedupe_records(iter(recs), fields=["id"], keep="last"))
    assert len(result) == 2
    msgs = {r["id"]: r["msg"] for r in result}
    assert msgs["1"] == "last"
    assert msgs["2"] == "only"


# --- no fields passthrough ---

def test_dedupe_no_fields_passes_all():
    recs = [{"a": 1}, {"a": 1}, {"a": 2}]
    result = list(dedupe_records(iter(recs), fields=[]))
    assert len(result) == 3


# --- invalid keep ---

def test_dedupe_invalid_keep_raises():
    with pytest.raises(ValueError, match="keep must be"):
        list(dedupe_records(iter([{"a": 1}]), fields=["a"], keep="middle"))


# --- max_seen cache eviction ---

def test_dedupe_max_seen_evicts_old_keys():
    # After eviction, an old key can appear again
    recs = [
        {"id": "1"},  # seen, cache: {1}
        {"id": "2"},  # seen, cache: {1,2} -> evict 1 (max_seen=2 means at 2 we evict before adding)
        {"id": "3"},  # evicts 1 from cache, cache: {2,3}
        {"id": "1"},  # 1 no longer in cache, emitted again
    ]
    result = list(dedupe_records(iter(recs), fields=["id"], keep="first", max_seen=2))
    ids = [r["id"] for r in result]
    assert ids.count("1") == 2
