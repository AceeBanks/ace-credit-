"""B7.C28 — Statistical discipline tests."""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

_ROOT = Path(__file__).resolve().parents[3]
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from prototype.g0.evaluation.statistics import (  # noqa: E402
    confusion_matrix,
    meaningful_improvement,
    severity_failure_counts,
    summarize_metric,
)


def test_summarize_empty_is_null_not_zero():
    r = summarize_metric(values=[], name="quality")
    assert r["sample_size"] == 0
    assert r["mean"] is None
    assert r["ci95"] is None


def test_summarize_single_sample_no_distribution_claim():
    r = summarize_metric(values=[0.8], name="quality")
    assert r["sample_size"] == 1
    assert r["std"] is None
    assert "no distribution claim" in r["note"]


def test_summarize_reports_ci():
    r = summarize_metric(values=[0.7, 0.75, 0.8, 0.85, 0.9, 0.8, 0.78, 0.82,
                                 0.79, 0.81, 0.77, 0.83], name="q")
    assert r["sample_size"] == 12
    assert r["mean"] is not None
    assert r["ci95"] is not None


def test_meaningful_improvement_requires_sample_size():
    r = meaningful_improvement(baseline_mean=0.5, candidate_mean=0.9,
                               sample_size=5, noise=0.05)
    assert r["meaningful"] is False
    assert "sample size" in r["reason"]


def test_meaningful_improvement_within_noise():
    r = meaningful_improvement(baseline_mean=0.5, candidate_mean=0.52,
                               sample_size=50, noise=0.05)
    assert r["meaningful"] is False


def test_meaningful_improvement_beyond_noise():
    r = meaningful_improvement(baseline_mean=0.5, candidate_mean=0.7,
                               sample_size=50, noise=0.05)
    assert r["meaningful"] is True


def test_confusion_matrix():
    cases = [
        {"exp": True, "pred": True},
        {"exp": True, "pred": False},   # false negative
        {"exp": False, "pred": True},   # false positive (false eligible)
        {"exp": False, "pred": False},
    ]
    m = confusion_matrix(cases=cases, expected_key="exp", predicted_key="pred")
    assert m["true_positive"] == 1
    assert m["false_positive"] == 1
    assert m["false_negative"] == 1
    assert m["true_negative"] == 1
    assert m["accuracy"] == 0.5
    assert "false_positive" in m["highest_severity_class"]


def test_severity_failure_counts():
    failures = [{"severity": "P0"}, {"severity": "P1"}, {"severity": "P1"},
                {"severity": "P2"}, {"severity": "UNKNOWN"}]
    r = severity_failure_counts(failures=failures)
    assert r["P0"] == 1
    assert r["P1"] == 2
    assert r["P2"] == 1
    assert r["total"] == 4
