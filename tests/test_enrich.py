"""Tests for logslice.enrich."""

from __future__ import annotations

import csv
import json
import os
import tempfile
from typing import Dict

import pytest

from logslice.enrich import enrich_record, enrich_records, load_mapping


def write_csv(path: str, rows: list, fieldnames: list) -> None:
    with open(path, "w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def write_json(path: str, data) -> None:
    with open(path, "w", encoding="utf-8") as fh:
        json.dump(data, fh)


@pytest.fixture()
def csv_mapping_file(tmp_path):
    p = tmp_path / "map.csv"
    write_csv(str(p), [{"key": "200", "value": "OK"}, {"key": "404", "value": "Not Found"}], ["key", "value"])
    return str(p)


@pytest.fixture()
def json_mapping_file(tmp_path):
    p = tmp_path / "map.json"
    write_json(str(p), [{"code": "200", "label": "OK"}, {"code": "500", "label": "Error"}])
    return str(p)


def test_load_mapping_csv(csv_mapping_file):
    m = load_mapping(csv_mapping_file, "key", "value")
    assert m == {"200": "OK", "404": "Not Found"}


def test_load_mapping_json_list(json_mapping_file):
    m = load_mapping(json_mapping_file, "code", "label")
    assert m == {"200": "OK", "500": "Error"}


def test_load_mapping_json_dict(tmp_path):
    p = tmp_path / "flat.json"
    write_json(str(p), {"a": "alpha", "b": "beta"})
    m = load_mapping(str(p), "unused", "unused")
    assert m == {"a": "alpha", "b": "beta"}


def test_enrich_record_hit():
    mapping = {"200": "OK", "404": "Not Found"}
    rec = {"status": "200", "msg": "hello", "_raw": "x"}
    result = enrich_record(rec, "status", mapping, "status_label")
    assert result["status_label"] == "OK"
    assert result["status"] == "200"
    assert result["_raw"] == "x"


def test_enrich_record_miss_uses_default():
    mapping = {"200": "OK"}
    rec = {"status": "999"}
    result = enrich_record(rec, "status", mapping, "label", default="unknown")
    assert result["label"] == "unknown"


def test_enrich_record_miss_no_default_gives_none():
    rec = {"status": "999"}
    result = enrich_record(rec, "status", {}, "label")
    assert result["label"] is None


def test_enrich_record_does_not_mutate_original():
    rec = {"status": "200"}
    enrich_record(rec, "status", {"200": "OK"}, "label")
    assert "label" not in rec


def test_enrich_records_all_enriched():
    mapping = {"a": "alpha", "b": "beta"}
    records = [{"k": "a"}, {"k": "b"}, {"k": "c"}]
    result = list(enrich_records(records, "k", mapping, "k_label", default="?"))
    assert [r["k_label"] for r in result] == ["alpha", "beta", "?"]


def test_enrich_records_skip_missing():
    mapping = {"a": "alpha"}
    records = [{"k": "a"}, {"k": "b"}, {"k": "a"}]
    result = list(enrich_records(records, "k", mapping, "k_label", skip_missing=True))
    assert len(result) == 2
    assert all(r["k_label"] == "alpha" for r in result)


def test_enrich_records_missing_lookup_field_uses_default():
    records = [{"other": "x"}]
    result = list(enrich_records(records, "k", {}, "k_label", default="N/A"))
    assert result[0]["k_label"] == "N/A"
