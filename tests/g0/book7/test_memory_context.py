"""B7.C14 — Memory & context evaluation tests."""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

_ROOT = Path(__file__).resolve().parents[3]
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from prototype.g0.evaluation.agent_eval import (  # noqa: E402
    bounded_context_bundle,
    cold_restart_reconstruction,
    memory_context_eval,
)


def test_memory_context_clean_pass():
    r = memory_context_eval(
        mandatory_anchor_retained=True,
        relevant_recall_rate=0.95,
        irrelevant_context_rate=0.05,
        cross_project_bleed=False,
        cross_tenant_bleed=False,
        stale_memory_used=False,
        token_footprint=12000,
        question_repetition=0)
    assert r["all_pass"] is True


def test_cross_tenant_bleed_p0_fail():
    r = memory_context_eval(
        mandatory_anchor_retained=True,
        relevant_recall_rate=0.95,
        irrelevant_context_rate=0.05,
        cross_project_bleed=False,
        cross_tenant_bleed=True,
        stale_memory_used=False,
        token_footprint=12000,
        question_repetition=0)
    assert r["all_pass"] is False
    assert any(x["metric_id"] == "M5_no_cross_tenant" and not x["passed"]
               for x in r["results"])


def test_cross_project_bleed_fails():
    r = memory_context_eval(
        mandatory_anchor_retained=True,
        relevant_recall_rate=0.95,
        irrelevant_context_rate=0.05,
        cross_project_bleed=True,
        cross_tenant_bleed=False,
        stale_memory_used=False,
        token_footprint=12000,
        question_repetition=0)
    assert r["all_pass"] is False


def test_stale_memory_use_fails():
    r = memory_context_eval(
        mandatory_anchor_retained=True,
        relevant_recall_rate=0.95,
        irrelevant_context_rate=0.05,
        cross_project_bleed=False,
        cross_tenant_bleed=False,
        stale_memory_used=True,
        token_footprint=12000,
        question_repetition=0)
    assert r["all_pass"] is False


def test_missing_anchor_fails_cold_restart():
    r = memory_context_eval(
        mandatory_anchor_retained=False,
        relevant_recall_rate=0.95,
        irrelevant_context_rate=0.05,
        cross_project_bleed=False,
        cross_tenant_bleed=False,
        stale_memory_used=False,
        token_footprint=12000,
        question_repetition=0)
    assert r["all_pass"] is False


def test_token_footprint_over_budget_fails():
    r = memory_context_eval(
        mandatory_anchor_retained=True,
        relevant_recall_rate=0.95,
        irrelevant_context_rate=0.05,
        cross_project_bleed=False,
        cross_tenant_bleed=False,
        stale_memory_used=False,
        token_footprint=90000,
        question_repetition=0)
    assert r["all_pass"] is False


def test_cold_restart_reconstruction():
    required = {"tenant_id": "tenant-a", "project_id": "proj-1",
                "revision_id": "opp_rev_ga_501_1",
                "decision": "ELIGIBLE"}
    ok = cold_restart_reconstruction(
        reconstructed=dict(required), required=required)
    assert ok["pass"] is True
    missing = cold_restart_reconstruction(
        reconstructed={"tenant_id": "tenant-a"},
        required=required)
    assert missing["pass"] is False
    assert set(missing["missing"]) == {"project_id", "revision_id", "decision"}


def test_bounded_context_bundle_tenant_bound():
    ok = bounded_context_bundle(
        bundle_tenant_id="tenant-a",
        bundle_project_ids=["proj-1"],
        evidence_tenant_ids=["tenant-a", "tenant-a"])
    assert ok.passed
    bad = bounded_context_bundle(
        bundle_tenant_id="tenant-a",
        bundle_project_ids=["proj-1"],
        evidence_tenant_ids=["tenant-a", "tenant-b"])
    assert not bad.passed
    assert "tenant-b" in bad.detail
