"""B7-D2 — First grounded grant-writing quality experiment tests.

The harness must be honest: no fabricated model generation, no invented
human-review scores, BLOCKED_MODEL_RUNTIME reported truthfully, protected
claims preserved, submission disabled, deterministic baseline metrics real.
"""
from __future__ import annotations

import json
import sys
from decimal import Decimal
from pathlib import Path

import pytest

_ROOT = Path(__file__).resolve().parents[3]
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from prototype.g0.evaluation.fixtures import (  # noqa: E402
    D2_FIXTURE,
    d2_budget_total,
)
from tools.g0.d2_harness import (  # noqa: E402
    _model_runtime_available,
    build_d2_report,
    build_humanized_lane_status,
    run_claim_ledger_eval,
    run_deterministic_qa,
    run_humanizer_protected_claim_diff,
    run_requirement_eval,
)


def test_d2_report_never_fabricates_humanized_draft():
    report = build_d2_report()
    assert report["humanized_draft"] is None  # never invented
    status = report["humanizer_lane"]["status"]
    assert status in ("BLOCKED_MODEL_RUNTIME", "AVAILABLE")


def test_d2_report_submission_disabled():
    report = build_d2_report()
    assert report["label"] == "MOCK_NON_SUBMISSION"
    assert report["submission_enabled"] is False


def test_d2_report_binds_exact_fixture_and_revision():
    report = build_d2_report()
    f = report["fixture"]
    assert f["opportunity_revision_id"] == "opp_rev_ga_501_1"
    assert f["revision_deadline"] == "2026-10-15"
    assert f["revision_ceiling"] == "50000.00"
    assert f["eligibility"] == "ELIGIBLE"
    assert f["organization"] == "Community Youth Works, Inc."


def test_d2_baseline_deterministic_qa_all_pass():
    report = build_d2_report()
    qa = report["baseline_metrics"]["deterministic_qa"]
    assert qa["total"] == 8
    assert qa["failed"] == 0
    assert qa["all_pass"] is True


def test_d2_baseline_claim_support_full():
    report = build_d2_report()
    claims = report["baseline_metrics"]["claim_support"]
    assert claims["unsupported"] == 0
    assert claims["material_claim_support_rate"] == 1.0


def test_d2_requirement_coverage_complete():
    report = build_d2_report()
    cov = report["baseline_metrics"]["requirement_coverage"]
    assert cov["coverage"] == 1.0
    assert cov["missing"] == []


def test_d2_budget_within_ceiling():
    report = build_d2_report()
    assert Decimal(report["baseline_metrics"]["budget_total"]) <= Decimal(
        report["baseline_metrics"]["funding_ceiling"])


def test_d2_no_fabricated_d2_fail_conditions():
    report = build_d2_report()
    fc = report["d2_fail_conditions"]
    for key, value in fc.items():
        if key != "humanizer_changed_protected_fact":
            assert value is False, key


def test_d2_humanizer_diff_validator_live():
    diff = run_humanizer_protected_claim_diff("")
    assert diff["identity_transform_preserves_protected_facts"] is True
    assert diff["tampered_amount_and_deadline_detected"] is True


def test_d2_human_review_not_invented():
    report = build_d2_report()
    assert report["human_review"]["status"] == "NOT_PERFORMED"


def test_d2_artifacts_exist_and_are_reviewable():
    d2_dir = _ROOT / "docs/grant-sector/g0/07-evaluation/d2"
    for name in ("D2_INPUT_MANIFEST.json", "D2_BASELINE_DRAFT.md",
                 "D2_BASELINE_EVAL.json", "D2_COMPARISON_REPORT.md",
                 "D2_DECISION.json", "D2_REPRODUCTION_MANIFEST.json"):
        assert (d2_dir / name).exists(), name
    decision = json.loads((d2_dir / "D2_DECISION.json").read_text(
        encoding="utf-8"))
    assert decision["submission"] == "DISABLED"
    # honest live-runtime awareness: when a governed runtime exists the
    # harness must report it (AVAILABLE) instead of a stale BLOCKED
    if _model_runtime_available():
        assert decision["live_model_runtime"] == "AVAILABLE"
    else:
        assert decision["live_model_runtime"] == "BLOCKED_MODEL_RUNTIME"


def test_d2_baseline_draft_uses_only_governed_values():
    report = build_d2_report()
    joined = " ".join(report["baseline_grounded_draft"]["sections"].values())
    for protected in ("Community Youth Works", "18.2 percent",
                      "October 15, 2026", "$50,000"):
        assert protected in joined, protected


def test_d2_humanizer_disposition_is_defer_not_promote():
    decision = json.loads(
        (_ROOT / "docs/grant-sector/g0/07-evaluation/d2/D2_DECISION.json")
        .read_text(encoding="utf-8"))
    # never a PROMOTE from the harness alone; the live Humanizer decision
    # lives in d2-live and is REVISE/REJECT/QUARANTINE/DEFER, never auto-
    # PROMOTE (C28: one fixture is weak evidence)
    assert decision["humanizer_disposition"] != "PROMOTE"
    if _model_runtime_available():
        live = json.loads(
            (_ROOT / "docs/grant-sector/g0/07-evaluation/d2-live/"
             "D2_LIVE_HUMANIZER_DECISION.json")
            .read_text(encoding="utf-8"))
        assert live["disposition"] != "PROMOTE"


def test_d2_standalone_functions_agree_with_report():
    qa = run_deterministic_qa({
        "community_impact": "x", "organization": "y",
        "budget_narrative": "z", "deadline": "w"})
    assert qa["total"] == 8
    claims = run_claim_ledger_eval([
        {"claim_id": "c", "support_status": "SUPPORTED", "material": True}])
    assert claims["supported"] == 1
    assert run_requirement_eval()["coverage"] == 1.0
    assert build_humanized_lane_status()["status"] in (
        "BLOCKED_MODEL_RUNTIME", "AVAILABLE")
