"""Tests for logslice.score and logslice.cli_score."""
from __future__ import annotations

import argparse
from typing import Any, Dict

import pytest

from logslice.score import parse_score_rules, score_record, score_records
from logslice.cli_score import (
    extract_score_kwargs,
    is_score_active,
    register_score_args,
)


def make_record(**kwargs: Any) -> Dict[str, Any]:
    return {"_raw": "", **kwargs}


# ---------------------------------------------------------------------------
# parse_score_rules
# ---------------------------------------------------------------------------

def test_parse_score_rules_basic():
    rules = parse_score_rules(["level:ERROR", "msg:timeout"])
    assert rules == [("level", "ERROR"), ("msg", "timeout")]


def test_parse_score_rules_skips_no_colon():
    rules = parse_score_rules(["no-colon", "level:WARN"])
    assert rules == [("level", "WARN")]


def test_parse_score_rules_empty_list():
    assert parse_score_rules([]) == []


def test_parse_score_rules_strips_whitespace():
    rules = parse_score_rules([" level : ERROR "])
    assert rules == [("level", "ERROR")]


# ---------------------------------------------------------------------------
# score_record
# ---------------------------------------------------------------------------

def test_score_record_all_match():
    rec = make_record(level="ERROR", msg="connection timeout")
    scored = score_record(rec, [("level", "ERROR"), ("msg", "timeout")])
    assert scored["_score"] == 2


def test_score_record_partial_match():
    rec = make_record(level="INFO", msg="connection timeout")
    scored = score_record(rec, [("level", "ERROR"), ("msg", "timeout")])
    assert scored["_score"] == 1


def test_score_record_no_match():
    rec = make_record(level="DEBUG", msg="all good")
    scored = score_record(rec, [("level", "ERROR")])
    assert scored["_score"] == 0


def test_score_record_missing_field_scores_zero():
    rec = make_record(msg="oops")
    scored = score_record(rec, [("level", "ERROR")])
    assert scored["_score"] == 0


def test_score_record_custom_field():
    rec = make_record(level="ERROR")
    scored = score_record(rec, [("level", "ERROR")], field="relevance")
    assert "relevance" in scored
    assert scored["relevance"] == 1


def test_score_record_does_not_mutate_original():
    rec = make_record(level="ERROR")
    score_record(rec, [("level", "ERROR")])
    assert "_score" not in rec


def test_score_record_invalid_pattern_skipped():
    rec = make_record(level="ERROR")
    scored = score_record(rec, [("level", "[invalid")])
    assert scored["_score"] == 0


# ---------------------------------------------------------------------------
# score_records
# ---------------------------------------------------------------------------

def test_score_records_yields_all_by_default():
    records = [make_record(level="ERROR"), make_record(level="INFO")]
    out = list(score_records(records, [("level", "ERROR")]))
    assert len(out) == 2


def test_score_records_min_score_filters():
    records = [make_record(level="ERROR"), make_record(level="INFO")]
    out = list(score_records(records, [("level", "ERROR")], min_score=1))
    assert len(out) == 1
    assert out[0]["level"] == "ERROR"


def test_score_records_empty_input():
    out = list(score_records([], [("level", "ERROR")]))
    assert out == []


# ---------------------------------------------------------------------------
# CLI helpers
# ---------------------------------------------------------------------------

def make_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser()
    register_score_args(p)
    return p


def test_register_adds_score_rule():
    p = make_parser()
    args = p.parse_args(["--score-rule", "level:ERROR"])
    assert args.score_rules == ["level:ERROR"]


def test_register_score_rule_repeatable():
    p = make_parser()
    args = p.parse_args(["--score-rule", "level:ERROR", "--score-rule", "msg:fail"])
    assert len(args.score_rules) == 2


def test_register_default_score_field():
    p = make_parser()
    args = p.parse_args([])
    assert args.score_field == "_score"


def test_register_custom_score_field():
    p = make_parser()
    args = p.parse_args(["--score-field", "relevance"])
    assert args.score_field == "relevance"


def test_register_default_min_score():
    p = make_parser()
    args = p.parse_args([])
    assert args.min_score == 0


def test_is_score_active_true():
    p = make_parser()
    args = p.parse_args(["--score-rule", "level:ERROR"])
    assert is_score_active(args) is True


def test_is_score_active_false():
    p = make_parser()
    args = p.parse_args([])
    assert is_score_active(args) is False


def test_extract_score_kwargs():
    p = make_parser()
    args = p.parse_args(
        ["--score-rule", "level:ERROR", "--score-field", "pts", "--min-score", "2"]
    )
    kwargs = extract_score_kwargs(args)
    assert kwargs["rules"] == [("level", "ERROR")]
    assert kwargs["field"] == "pts"
    assert kwargs["min_score"] == 2
