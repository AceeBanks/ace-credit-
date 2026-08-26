"""B2.C22 tests — Book 2 Reality Lock.

Proves the lock is DERIVED from evidence: the clean package passes; injecting
an uncovered client requirement, a broken relationship catalog, a LOSSY row
without loss notes, an open P0, or failing tests flips readiness to FAIL.
Also proves readiness cannot be true while any predicate is not explicitly
True, and that the committed lock equals a fresh regeneration (stale-lock
attack guard).
"""
from __future__ import annotations

import copy
import json
import os
from pathlib import Path

import pytest

from tools.g0.build_book2_reality_lock import (
    COMMITTED_LOCK_PATH,
    build_live_lock,
    compute_lock,
    CONFIG_NAMES,
)
from tools.g0._common import DOMAIN_CONFIG_DIR, load_yaml

_ROOT = Path(__file__).resolve().parents[3]
PASSING_TESTS = {"exit_code": 0, "passed": 246, "failed": 0, "summary": "246 passed"}


def _configs() -> dict:
    from tools.g0.build_book2_reality_lock import _STEM_MAP
    return {_STEM_MAP[stem]: load_yaml(DOMAIN_CONFIG_DIR / stem)
            for stem in CONFIG_NAMES}


def _lock(configs: dict | None = None, test_results: dict | None = None) -> dict:
    return compute_lock(configs or _configs(),
                        test_results=test_results or PASSING_TESTS)


def test_live_lock_passes():
    lock = _lock()
    assert lock["status"] == "PASS", lock["evidence"]
    assert lock["ready_for_book3"] is True
    assert lock["glossary_complete"] is True
    assert lock["entity_boundaries_ratified"] is True
    assert lock["root_entities_with_stable_identity"] == 1.0
    assert lock["external_ids_namespaced"] is True
    assert lock["relationship_catalog_complete"] is True
    assert lock["state_machine_tests_pass"] is True
    assert lock["revision_replay_tests_pass"] is True
    assert lock["fact_claim_evidence_tests_pass"] is True
    assert lock["eligibility_determinism_contract_pass"] is True
    assert lock["application_document_model_pass"] is True
    assert lock["common_grants_exact_roundtrip_pass"] is True
    assert lock["common_grants_loss_reporting_pass"] is True
    assert lock["client_phase1_domain_coverage"] == 1.0
    assert lock["georgia_federal_fixture_tests_pass"] is True
    assert lock["d0_draft_context_ready"] is True
    assert lock["adversarial_p0_pass"] is True
    assert lock["p0_open"] == 0


def test_tests_not_run_blocks_readiness():
    lock = compute_lock(_configs(), test_results=None)
    assert lock["status"] == "FAIL"
    assert lock["ready_for_book3"] is False
    assert lock["adversarial_p0_pass"] is None


def test_failing_tests_block_readiness():
    lock = compute_lock(_configs(),
                        test_results={"exit_code": 1, "passed": 240, "failed": 6,
                                      "summary": "240 passed, 6 failed"})
    assert lock["status"] == "FAIL"
    assert lock["adversarial_p0_pass"] is False


def test_uncovered_client_requirement_fails_lock():
    configs = _configs()
    configs["client_vision"]["coverage"][0]["covered"] = False
    lock = _lock(configs)
    assert lock["status"] == "FAIL"
    assert lock["client_phase1_domain_coverage"] < 1.0
    assert lock["ready_for_book3"] is False


def test_broken_relationship_catalog_fails_lock():
    configs = _configs()
    configs["relationships"]["relationship_types"][0]["cardinality"] = "NOPE"
    lock = _lock(configs)
    assert lock["status"] == "FAIL"
    assert lock["relationship_catalog_complete"] is False


def test_lossy_row_without_loss_notes_fails_lock():
    configs = _configs()
    for ent in configs["common_grants"]["entities"]:
        for row in ent.get("rows", []):
            if row["mapping_class"] == "LOSSY":
                row["loss_notes"] = ""
                break
    lock = _lock(configs)
    assert lock["status"] == "FAIL"
    assert lock["common_grants_loss_reporting_pass"] is False


def test_injected_open_p0_fails_lock():
    configs = _configs()
    ledger = load_yaml(_ROOT / "config/g0/ratification/contradiction_ledger.yaml")
    ledger = copy.deepcopy(ledger)
    p1 = next(c for c in ledger["contradictions"] if c["severity"] == "P1")
    p1["severity"] = "P0"
    p1["status"] = "OPEN"
    p1.pop("resolution", None)
    configs["ledger"] = ledger
    lock = _lock(configs)
    assert lock["p0_open"] >= 1
    assert lock["status"] == "FAIL"
    assert lock["ready_for_book3"] is False


def test_readiness_is_conjunction():
    """Every boolean predicate must be explicitly True for readiness."""
    lock = _lock()
    for key in ("glossary_complete", "entity_boundaries_ratified",
                "external_ids_namespaced", "relationship_catalog_complete",
                "state_machine_tests_pass", "revision_replay_tests_pass",
                "fact_claim_evidence_tests_pass",
                "eligibility_determinism_contract_pass",
                "application_document_model_pass",
                "common_grants_exact_roundtrip_pass",
                "common_grants_loss_reporting_pass",
                "georgia_federal_fixture_tests_pass", "d0_draft_context_ready",
                "adversarial_p0_pass"):
        assert lock[key] is True, key
    assert lock["client_phase1_domain_coverage"] >= 1.0
    assert lock["root_entities_with_stable_identity"] >= 1.0
    assert lock["p0_open"] == 0


@pytest.mark.skipif(
    os.environ.get("G0_SKIP_LOCK_FRESHNESS") == "1",
    reason="recursion guard: inner lock-build pytest runs skip this test",
)
def test_committed_lock_matches_regeneration():
    """The COMMITTED lock file must equal what an honest regeneration from live
    repository evidence produces right now. PASS cannot be faked by editing JSON."""
    committed = json.loads(COMMITTED_LOCK_PATH.read_text(encoding="utf-8"))
    fresh = build_live_lock()

    def normalize(lock: dict) -> dict:
        lock = copy.deepcopy(lock)
        lock.get("evidence", {}).get("test_results", {}).pop("summary", None)
        return lock

    assert normalize(committed) == normalize(fresh), (
        "Committed G0_B2_REALITY_LOCK.json is stale or hand-edited; "
        "regenerate it with tools/g0/build_book2_reality_lock.py"
    )
    assert committed["status"] == "PASS"
