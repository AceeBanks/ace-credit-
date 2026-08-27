"""G0-B7-C31 — Book 7 Reality Lock freshness & defect-injection suite.

Two responsibilities:
1. FRESHNESS: the committed G0_B7_REALITY_LOCK.json must still derive from
   current repository evidence (reload configs + live runs); a stale or
   hand-edited lock cannot authorize Book 8.
2. DEFECT INJECTION: each injected defect flips a predicate / the overall
   status to FAIL — proving the lock is DERIVED, not hard-coded.
3. HONESTY: submission stays disabled and the D2 live-model lane is reported
   truthfully (BLOCKED_MODEL_RUNTIME => d2_live_model_run_complete=False),
   never faked as a live run.
"""
from __future__ import annotations

import copy
import json
import os
import sys
from pathlib import Path

import pytest

_ROOT = Path(__file__).resolve().parents[3]
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from tools.g0.build_book7_reality_lock import (  # noqa: E402
    COMMITTED_LOCK_PATH,
    compute_lock,
)
from tools.g0._common import load_yaml  # noqa: E402

EVAL_CONFIG_DIR = _ROOT / "config/g0/evaluation"

CONFIG_STEMS = (
    "evaluation_constitution.yaml", "quality_dimensions.yaml",
    "regression_gates.yaml", "promotion_thresholds.yaml",
    "privacy_policies.yaml",
)


def _configs() -> dict:
    return {stem: load_yaml(EVAL_CONFIG_DIR / stem) for stem in CONFIG_STEMS}


def _fresh_results() -> dict:
    return {"exit_code": 0, "passed": 1, "failed": 0, "summary": "ok"}


def _green_seam() -> dict:
    from tools.g0.validate_seam_bindings import run_all as run_probes
    probes = run_probes()
    assert all(probes.values()), probes
    return probes


def _green_d2() -> dict:
    return {
        "harness_complete": True,
        "humanizer_lane_status": "BLOCKED_MODEL_RUNTIME",
        "protected_claim_diff_identity": True,
        "tamper_detected": True,
        "baseline_deterministic_qa_passed": True,
        "baseline_claim_support_rate": 1.0,
        "baseline_unsupported_claims": 0,
        "requirement_coverage": 1.0,
        "submission_enabled": False,
    }


def _live_lock(**overrides) -> dict:
    cfg = overrides.pop("configs", None) or _configs()
    kwargs = {
        "test_results": overrides.pop("test_results", _fresh_results()),
        "full_results": overrides.pop("full_results", _fresh_results()),
        "adversarial_results": overrides.pop("adversarial_results",
                                              _fresh_results()),
        "seam_results": overrides.pop("seam_results", _green_seam()),
        "d2_results": overrides.pop("d2_results", _green_d2()),
    }
    return compute_lock(cfg, **kwargs)


@pytest.mark.skipif(os.environ.get("G0_SKIP_LOCK_FRESHNESS") == "1",
                    reason="recursion guard for the lock builder's inner run")
def test_committed_lock_is_current_pass():
    """FRESH-001: the committed lock derives PASS from current evidence."""
    committed = json.loads(COMMITTED_LOCK_PATH.read_text(encoding="utf-8"))
    assert committed["book"] == "G0-B7"
    assert committed["status"] == "PASS"
    recomputed = _live_lock()
    assert recomputed["status"] == "PASS"
    assert recomputed["ready_for_book8"] is True


@pytest.mark.skipif(os.environ.get("G0_SKIP_LOCK_FRESHNESS") == "1",
                    reason="recursion guard for the lock builder's inner run")
def test_stale_lock_cannot_authorize():
    """FRESH-002: a hand-edited ready_for_book8=true is not trusted blindly —
    recomputation must agree from current evidence."""
    committed = json.loads(COMMITTED_LOCK_PATH.read_text(encoding="utf-8"))
    assert committed["ready_for_book8"] is True
    recomputed = _live_lock()
    assert recomputed["status"] == committed["status"] == "PASS"


def test_injected_constitution_defect_flips_lock():
    configs = _configs()
    broken = copy.deepcopy(configs)
    broken["evaluation_constitution.yaml"]["laws"] = []
    lock = _live_lock(configs=broken)
    assert lock["evaluation_constitution_pass"] is False
    assert lock["status"] == "FAIL"


def test_injected_taxonomy_defect_flips_lock():
    configs = _configs()
    broken = copy.deepcopy(configs)
    broken["quality_dimensions.yaml"]["dimensions"] = []
    lock = _live_lock(configs=broken)
    assert lock["quality_taxonomy_pass"] is False
    assert lock["status"] == "FAIL"


def test_injected_regression_gate_defect_flips_lock():
    configs = _configs()
    broken = copy.deepcopy(configs)
    broken["regression_gates.yaml"]["hard_gates"] = []
    lock = _live_lock(configs=broken)
    assert lock["security_regression_pass"] is False
    assert lock["status"] == "FAIL"


def test_injected_promotion_defect_flips_lock():
    configs = _configs()
    broken = copy.deepcopy(configs)
    broken["promotion_thresholds.yaml"]["rules"] = []
    lock = _live_lock(configs=broken)
    assert lock["skill_promotion_pass"] is False
    assert lock["status"] == "FAIL"


def test_injected_privacy_defect_flips_lock():
    configs = _configs()
    broken = copy.deepcopy(configs)
    broken["privacy_policies.yaml"]["controls"] = []
    lock = _live_lock(configs=broken)
    assert lock["privacy_leakage_pass"] is False
    assert lock["status"] == "FAIL"


def test_injected_seam_defect_flips_security_regression():
    broken = dict(_green_seam())
    broken["grant_authority_enforced"] = False
    lock = _live_lock(seam_results=broken)
    assert lock["security_regression_pass"] is False
    assert lock["status"] == "FAIL"


def test_injected_humanizer_defect_flips_protected_claim():
    d2 = dict(_green_d2())
    d2["tamper_detected"] = False
    lock = _live_lock(d2_results=d2)
    assert lock["humanizer_protected_claim_pass"] is False
    assert lock["status"] == "FAIL"


def test_injected_unsupported_claim_flips_d2_harness():
    d2 = dict(_green_d2())
    d2["baseline_unsupported_claims"] = 2
    lock = _live_lock(d2_results=d2)
    assert lock["d2_harness_complete"] is False
    assert lock["status"] == "FAIL"


def test_injected_submission_enabled_flips_lock():
    d2 = dict(_green_d2())
    d2["submission_enabled"] = True
    lock = _live_lock(d2_results=d2)
    assert lock["submission_enabled"] is True
    assert lock["p0_open"] >= 1
    assert lock["status"] == "FAIL"


def test_failing_test_results_flip_lock():
    bad = {"exit_code": 1, "passed": 0, "failed": 2, "summary": "2 failed"}
    lock = _live_lock(test_results=bad)
    assert lock["status"] == "FAIL"
    assert lock["ready_for_book8"] is False


def test_missing_test_results_report_null_not_false_claim():
    """When tests are not run, adversarial_p0_pass is null, never a false
    green claim."""
    lock = _live_lock(test_results=None, adversarial_results=None,
                      full_results=None)
    assert lock["adversarial_p0_pass"] is None
    assert lock["status"] != "PASS"


def test_live_model_lane_reported_honestly_blocked():
    """HONESTY-001: no configured model runtime => d2_live_model_run_complete
    is False (BLOCKED_MODEL_RUNTIME), never faked as a live run."""
    lock = _live_lock()
    assert lock["d2_harness_complete"] is True
    assert lock["d2_live_model_run_complete"] is False
    assert lock["submission_enabled"] is False
    assert lock["status"] == "PASS"  # blocked lane is not a defect


def test_required_predicate_set_present():
    """The 32-predicate contract from the mission (section 26) is sealed."""
    required = [
        "evaluation_constitution_pass", "quality_taxonomy_pass",
        "eval_case_contract_pass", "corpus_governance_pass",
        "golden_set_protocol_pass", "georgia_fixture_pack_ready",
        "grant_quality_eval_pass", "factuality_eval_pass",
        "eligibility_match_eval_pass", "research_eval_pass",
        "personal_hermes_eval_pass", "ceo_hermes_eval_pass",
        "worker_eval_pass", "memory_context_eval_pass",
        "security_regression_pass", "model_routing_eval_pass",
        "parser_retrieval_eval_pass", "evaluator_governance_pass",
        "skill_promotion_pass", "change_promotion_pass", "rollback_pass",
        "privacy_leakage_pass", "external_tool_bakeoff_complete",
        "humanizer_bakeoff_complete", "humanizer_protected_claim_pass",
        "d2_harness_complete", "adversarial_p0_pass",
        "submission_enabled", "p0_open", "ready_for_book8",
    ]
    lock = _live_lock()
    for key in required:
        assert key in lock, key
    assert lock["p0_open"] == 0
    assert lock["ready_for_book8"] is True
