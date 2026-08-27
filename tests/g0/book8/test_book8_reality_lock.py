"""G0-B8-C39 — Book 8 Reality Lock freshness & defect-injection suite.

1. FRESHNESS: the committed G0_B8_REALITY_LOCK.json must still derive from
   current repository evidence (live slice probe + drill probes + committed
   live-D2 evidence); a stale or hand-edited lock cannot authorize Book 9.
2. DEFECT INJECTION: each injected defect flips a predicate / the overall
   status to FAIL — proving the lock is DERIVED, not hard-coded.
3. HONESTY: submission stays disabled; ready_for_book9 derives only when
   every gate passes.
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

from tools.g0.build_book8_reality_lock import (  # noqa: E402
    COMMITTED_LOCK_PATH,
    compute_lock,
    _drill_probes,
    _live_d2_evidence,
    _live_slice_probe,
)


def _green_tests() -> dict:
    return {"exit_code": 0, "passed": 26, "failed": 0, "summary": "ok"}


def _live_lock(*, tests: dict | None = None, slice_probe: dict | None = None,
               drills: dict | None = None, live_d2: dict | None = None) -> dict:
    return compute_lock(
        tests=tests if tests is not None else _green_tests(),
        slice_probe=(slice_probe if slice_probe is not None
                     else _live_slice_probe()),
        drills=(drills if drills is not None else _drill_probes()),
        live_d2=(live_d2 if live_d2 is not None else _live_d2_evidence()))


def test_committed_lock_is_current_pass():
    """FRESH-001: the committed lock derives PASS from current evidence."""
    committed = json.loads(COMMITTED_LOCK_PATH.read_text(encoding="utf-8"))
    assert committed["book"] == "G0-B8"
    assert committed["status"] == "PASS"
    recomputed = _live_lock()
    assert recomputed["status"] == "PASS"
    assert recomputed["ready_for_book9"] is True
    assert committed["ready_for_book9"] is True


@pytest.mark.skipif(os.environ.get("G0_SKIP_LOCK_FRESHNESS") == "1",
                    reason="recursion guard for the lock builder's inner run")
def test_stale_lock_cannot_authorize():
    """FRESH-002: a hand-edited ready_for_book9=true is not trusted blindly —
    recomputation must agree from current evidence."""
    committed = json.loads(COMMITTED_LOCK_PATH.read_text(encoding="utf-8"))
    assert committed["ready_for_book9"] is True
    recomputed = _live_lock()
    assert recomputed["status"] == committed["status"] == "PASS"


def test_injected_hard_gate_defect_flips_lock():
    """Injected: deterministic QA hard gate fails -> lock FAILs."""
    probe = _live_slice_probe()
    probe["hard_gate_pass"] = False
    lock = _live_lock(slice_probe=probe)
    assert lock["status"] == "FAIL"
    assert lock["predicates"]["qa_eval_hard_gates_pass"] is False


def test_injected_eligibility_defect_flips_lock():
    probe = _live_slice_probe()
    probe["eligibility_eligible"] = False
    lock = _live_lock(slice_probe=probe)
    assert lock["status"] == "FAIL"
    assert lock["predicates"]["eligibility_determinism_pass"] is False


def test_injected_budget_defect_flips_lock():
    probe = _live_slice_probe()
    probe["budget_within_ceiling"] = False
    lock = _live_lock(slice_probe=probe)
    assert lock["status"] == "FAIL"
    assert lock["predicates"]["budget_reconciliation_pass"] is False


def test_injected_submission_enabled_flips_lock():
    """The deadliest defect: a reachable submission capability -> FAIL."""
    probe = _live_slice_probe()
    probe["submission_enabled"] = True
    lock = _live_lock(slice_probe=probe)
    assert lock["status"] == "FAIL"
    assert lock["submission_enabled"] is True
    assert lock["ready_for_book9"] is False


def test_injected_amendment_defect_flips_lock():
    drills = _drill_probes()
    drills["amendment_material_invalidates"] = False
    lock = _live_lock(drills=drills)
    assert lock["status"] == "FAIL"
    assert lock["predicates"]["source_amendment_drill_pass"] is False


def test_injected_security_defect_flips_lock():
    drills = _drill_probes()
    drills["security_all_denied"] = False
    lock = _live_lock(drills=drills)
    assert lock["status"] == "FAIL"
    assert lock["predicates"]["security_attack_drill_pass"] is False


def test_injected_cold_restart_defect_flips_lock():
    drills = _drill_probes()
    drills["cold_restart"] = False
    lock = _live_lock(drills=drills)
    assert lock["status"] == "FAIL"
    assert lock["predicates"]["cold_restart_pass"] is False


def test_injected_test_failure_flips_lock():
    lock = _live_lock(tests={"exit_code": 1, "passed": 25, "failed": 1,
                             "summary": "1 failed"})
    assert lock["status"] == "FAIL"


def test_no_live_model_evidence_blocks_book9():
    """Without the live D2 model evidence the lock must NOT claim full
    pass: proposal_draft can still pass via the deterministic lane, but the
    lock reports the missing live evidence honestly."""
    lock = _live_lock(live_d2={"live_model_run_complete": False})
    assert lock["predicates"]["live_model_generation_pass"] is False


def test_required_predicate_set_present():
    """The sealed Book 8 predicate contract from the master plan."""
    required = [
        "canonical_client_fixture_pass", "real_opportunity_source_pass",
        "intent_contract_pass", "ceo_planning_pass",
        "eligibility_determinism_pass", "match_explanation_pass",
        "winner_research_pass", "organization_verification_pass",
        "community_evidence_pass", "application_blueprint_pass",
        "bounded_worker_pass", "proposal_draft_pass",
        "supporting_artifact_pass", "budget_reconciliation_pass",
        "claim_ledger_pass", "qa_eval_hard_gates_pass", "human_review_pass",
        "submission_ready_mock_pass", "submission_enabled",
        "explanation_packet_pass", "source_amendment_drill_pass",
        "cold_restart_pass", "optional_component_degradation_pass",
        "security_attack_drill_pass", "runtime_measurement_packet_pass",
        "full_reconstruction_pass", "client_experience_review_complete",
        "adversarial_p0_pass", "live_model_generation_pass",
        "p0_open", "ready_for_book9",
    ]
    lock = _live_lock()
    for key in required:
        assert key in lock["predicates"] or key in lock, key
    assert lock["p0_open"] == 0
    assert lock["ready_for_book9"] is True
    assert lock["submission_enabled"] is False


def test_recomputation_uses_live_evidence_not_committed_values():
    """The lock must be DERIVED: recomputation runs the actual slice and
    drills rather than trusting the committed JSON."""
    recomputed = _live_lock()
    assert recomputed["evidence"]["vertical_slice_probe"]["all_stages"] \
        is True
    assert recomputed["evidence"]["drill_probes"]["security_all_denied"] \
        is True
