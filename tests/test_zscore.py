"""Tests for logslice.zscore."""

import pytest
from logslice.zscore import compute_mean_stddev, zscore_records, _to_float


# --- _to_float ---

def test_to_float_numeric_string():
    assert _to_float("3.14") == pytest.approx(3.14)

def test_to_float_int():
    assert _to_float(42) == pytest.approx(42.0)

def test_to_float_none_returns_none():
    assert _to_float(None) is None

def test_to_float_non_numeric_returns_none():
    assert _to_float("error") is None


# --- compute_mean_stddev ---

def test_mean_stddev_basic():
    mean, std = compute_mean_stddev([2.0, 4.0, 4.0, 4.0, 5.0, 5.0, 7.0, 9.0])
    assert mean == pytest.approx(5.0)
    assert std == pytest.approx(2.0)

def test_mean_stddev_empty():
    mean, std = compute_mean_stddev([])
    assert mean == 0.0
    assert std == 0.0

def test_mean_stddev_single_value():
    mean, std = compute_mean_stddev([7.0])
    assert mean == pytest.approx(7.0)
    assert std == pytest.approx(0.0)


# --- zscore_records ---

def make_records(values):
    return [{"val": v, "_raw": f"val={v}"} for v in values]


def test_zscore_annotates_dest_field():
    recs = make_records([10, 10, 10])
    out = list(zscore_records(recs, field="val"))
    assert all("zscore" in r for r in out)

def test_zscore_zero_for_uniform_data():
    recs = make_records([5, 5, 5])
    out = list(zscore_records(recs, field="val"))
    # stddev is 0, so zscore should be None
    assert all(r["zscore"] is None for r in out)

def test_zscore_values_correct():
    recs = make_records([2, 4, 4, 4, 5, 5, 7, 9])
    out = list(zscore_records(recs, field="val"))
    # mean=5, std=2; first value: (2-5)/2 = -1.5
    assert out[0]["zscore"] == pytest.approx(-1.5)
    assert out[-1]["zscore"] == pytest.approx(2.0)

def test_zscore_custom_dest():
    recs = make_records([1, 2, 3])
    out = list(zscore_records(recs, field="val", dest="z"))
    assert "z" in out[0]
    assert "zscore" not in out[0]

def test_zscore_missing_field_gives_none():
    recs = [{"other": 1, "_raw": "other=1"}]
    out = list(zscore_records(recs, field="val"))
    assert out[0]["zscore"] is None

def test_zscore_threshold_flags_anomaly():
    recs = make_records([2, 4, 4, 4, 5, 5, 7, 9])
    out = list(zscore_records(recs, field="val", threshold=1.5))
    assert out[0]["anomaly"] is True   # z = -1.5
    assert out[-1]["anomaly"] is True  # z = 2.0
    assert out[1]["anomaly"] is False  # z = -0.5

def test_zscore_threshold_custom_flag_field():
    recs = make_records([1, 2, 3])
    out = list(zscore_records(recs, field="val", threshold=0.5, flag_field="is_outlier"))
    assert all("is_outlier" in r for r in out)

def test_zscore_does_not_mutate_original():
    recs = [{"val": 1, "_raw": "val=1"}]
    original = dict(recs[0])
    list(zscore_records(recs, field="val"))
    assert recs[0] == original

def test_zscore_preserves_raw():
    recs = [{"val": 10, "_raw": "val=10"}]
    out = list(zscore_records(recs, field="val"))
    assert out[0]["_raw"] == "val=10"
