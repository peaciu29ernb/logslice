"""Tests for logslice.countif."""

import pytest
from logslice.countif import (
    parse_countif_rule,
    countif_records,
    format_countif_table,
)


def make_record(**kwargs):
    return {"__raw__": "", **kwargs}


# --- parse_countif_rule ---

def test_parse_countif_rule_valid_eq():
    assert parse_countif_rule("level:eq:error") == ("level", "eq", "error")


def test_parse_countif_rule_valid_re():
    assert parse_countif_rule("msg:re:timeout") == ("msg", "re", "timeout")


def test_parse_countif_rule_valid_gte():
    assert parse_countif_rule("status:gte:500") == ("status", "gte", "500")


def test_parse_countif_rule_no_colons_returns_none():
    assert parse_countif_rule("levelEQerror") is None


def test_parse_countif_rule_unknown_op_returns_none():
    assert parse_countif_rule("level:contains:error") is None


def test_parse_countif_rule_empty_field_returns_none():
    assert parse_countif_rule(":eq:error") is None


# --- countif_records ---

RECORDS = [
    make_record(level="error", status="500", svc="auth"),
    make_record(level="warn",  status="200", svc="auth"),
    make_record(level="error", status="503", svc="api"),
    make_record(level="info",  status="200", svc="api"),
    make_record(level="error", status="200", svc="auth"),
]


def test_countif_single_rule_eq():
    rules = [("level", "eq", "error")]
    result = countif_records(RECORDS, rules)
    assert result == {"_all": 3}


def test_countif_multiple_rules_all_must_match():
    rules = [("level", "eq", "error"), ("status", "gte", "500")]
    result = countif_records(RECORDS, rules)
    assert result == {"_all": 2}


def test_countif_no_matches_returns_empty():
    rules = [("level", "eq", "critical")]
    result = countif_records(RECORDS, rules)
    assert result == {}


def test_countif_with_group_by():
    rules = [("level", "eq", "error")]
    result = countif_records(RECORDS, rules, group_by="svc")
    assert result == {"auth": 2, "api": 1}


def test_countif_regex_rule():
    rules = [("status", "re", "^5")]
    result = countif_records(RECORDS, rules)
    assert result == {"_all": 2}


def test_countif_missing_field_does_not_match():
    records = [make_record(msg="hello"), make_record(level="error")]
    rules = [("level", "eq", "error")]
    result = countif_records(records, rules)
    assert result == {"_all": 1}


def test_countif_empty_records():
    assert countif_records([], [("level", "eq", "error")]) == {}


# --- format_countif_table ---

def test_format_countif_table_empty():
    assert format_countif_table({}) == "(no matches)"


def test_format_countif_table_single_entry():
    output = format_countif_table({"_all": 42})
    assert "_all" in output
    assert "42" in output


def test_format_countif_table_sorted_by_count_desc():
    counts = {"auth": 3, "api": 10, "db": 1}
    lines = format_countif_table(counts).splitlines()
    data_lines = [l for l in lines if l.strip() and "---" not in l and "group" not in l]
    values = [int(l.split()[-1]) for l in data_lines]
    assert values == sorted(values, reverse=True)
