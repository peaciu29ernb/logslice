"""Tests for logslice.label."""

import pytest
from logslice.label import (
    _matches_rule,
    parse_label_rule,
    label_record,
    label_records,
)


# ---------------------------------------------------------------------------
# parse_label_rule
# ---------------------------------------------------------------------------

def test_parse_label_rule_valid():
    assert parse_label_rule("level:eq:error=bad") == ("level", "eq", "error", "bad")


def test_parse_label_rule_no_equals_returns_none():
    assert parse_label_rule("level:eq:error") is None


def test_parse_label_rule_too_few_colons_returns_none():
    assert parse_label_rule("level:eq=label") is None


def test_parse_label_rule_empty_label_returns_none():
    assert parse_label_rule("level:eq:error=") is None


# ---------------------------------------------------------------------------
# _matches_rule
# ---------------------------------------------------------------------------

def test_matches_eq_true():
    assert _matches_rule({"level": "error"}, "level", "eq", "error") is True


def test_matches_eq_false():
    assert _matches_rule({"level": "info"}, "level", "eq", "error") is False


def test_matches_neq():
    assert _matches_rule({"level": "info"}, "level", "neq", "error") is True


def test_matches_contains():
    assert _matches_rule({"msg": "connection refused"}, "msg", "contains", "refused") is True


def test_matches_startswith():
    assert _matches_rule({"msg": "ERROR: disk full"}, "msg", "startswith", "ERROR") is True


def test_matches_endswith():
    assert _matches_rule({"path": "/var/log/app.log"}, "path", "endswith", ".log") is True


def test_matches_regex():
    assert _matches_rule({"code": "404"}, "code", "regex", r"^4\d{2}$") is True


def test_matches_invalid_regex_returns_false():
    assert _matches_rule({"code": "404"}, "code", "regex", "[invalid") is False


def test_matches_gt_numeric():
    assert _matches_rule({"latency": "150"}, "latency", "gt", "100") is True


def test_matches_lt_numeric():
    assert _matches_rule({"latency": "50"}, "latency", "lt", "100") is True


def test_matches_gt_non_numeric_returns_false():
    assert _matches_rule({"latency": "fast"}, "latency", "gt", "100") is False


def test_matches_missing_field_returns_false():
    assert _matches_rule({}, "level", "eq", "error") is False


# ---------------------------------------------------------------------------
# label_record
# ---------------------------------------------------------------------------

def test_label_record_first_match_wins():
    rules = [("level", "eq", "error", "bad"), ("level", "eq", "error", "also-bad")]
    result = label_record({"level": "error"}, rules)
    assert result["label"] == "bad"


def test_label_record_no_match_no_default():
    rules = [("level", "eq", "error", "bad")]
    result = label_record({"level": "info"}, rules)
    assert "label" not in result


def test_label_record_no_match_with_default():
    rules = [("level", "eq", "error", "bad")]
    result = label_record({"level": "info"}, rules, default="ok")
    assert result["label"] == "ok"


def test_label_record_multi_collects_all():
    rules = [
        ("level", "eq", "error", "bad"),
        ("msg", "contains", "timeout", "slow"),
    ]
    result = label_record({"level": "error", "msg": "timeout occurred"}, rules, multi=True)
    assert result["label"] == "bad|slow"


def test_label_record_custom_dest():
    rules = [("level", "eq", "warn", "warning")]
    result = label_record({"level": "warn"}, rules, dest="category")
    assert "category" in result
    assert result["category"] == "warning"


def test_label_record_does_not_mutate_original():
    original = {"level": "error"}
    rules = [("level", "eq", "error", "bad")]
    label_record(original, rules)
    assert "label" not in original


# ---------------------------------------------------------------------------
# label_records
# ---------------------------------------------------------------------------

def test_label_records_yields_all():
    records = [{"level": "error"}, {"level": "info"}, {"level": "warn"}]
    rules = [("level", "eq", "error", "bad")]
    result = list(label_records(records, rules, default="ok"))
    assert len(result) == 3
    assert result[0]["label"] == "bad"
    assert result[1]["label"] == "ok"
    assert result[2]["label"] == "ok"
