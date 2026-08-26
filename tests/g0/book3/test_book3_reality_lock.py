"""B3.C27 tests — Book 3 Reality Lock.

Proves the lock is DERIVED from evidence: the clean package passes; injecting
a missing critical precedence chain, a broken D0 packet, a Georgia profile
without the crawled-state rule, an enabled source missing its adapter version,
an open P0, or failing tests flips readiness to FAIL. Also proves readiness
cannot be true while any predicate is not explicitly True, and that the
committed lock equals a fresh regeneration (stale-lock attack guard).
"""
from __future__ import annotations

import copy
import json
import os
from pathlib import Path

import pytest

from tools.g0.build_book3_reality_lock import (
    COMMITTED_LOCK_PATH,
    STEMS,
    build_live_lock,
    compute_lock,
)
from tools.g0._common import SOURCE_CONFIG_DIR, load_yaml

_ROOT = Path(__file__).resolve().parents[3]
PASSING_TESTS = {"exit_code": 0, "passed": 233, "failed": 0, "summary": "233 passed"}


def _configs() -> dict:
    return {stem.removesuffix(".yaml"): load_yaml(SOURCE_CONFIG_DIR / stem)
            for stem in STEMS}


def _lock(configs: dict | None = None, test_results: dict | None = None) -> dict:
    return compute_lock(configs or _configs(),
                        test_results=test_results or PASSING_TESTS)


def test_live_lock_passes():
    lock = _lock()
    assert lock["status"] == "PASS", lock["evidence"]
    assert lock["ready_for_d0"] is True
    assert lock["ready_for_book4"] is True
    assert lock["data_constitution_complete"] is True
    assert lock["enabled_sources_registered"] == 1.0
    assert lock["critical_facts_with_snapshot_lineage"] == 1.0
    for key in ("snapshot_immutability_tests_pass", "capture_replay_tests_pass",
                "extraction_lineage_tests_pass", "precedence_tests_pass",
                "freshness_tests_pass", "promotion_tests_pass",
                "conflict_tests_pass", "material_change_tests_pass",
                "dependency_invalidation_tests_pass",
                "identifier_verification_tests_pass",
                "statistic_semantics_tests_pass", "source_security_tests_pass",
                "retention_tests_pass", "provenance_chain_tests_pass",
                "federal_fixture_tests_pass", "georgia_fixture_tests_pass",
                "private_source_fixture_tests_pass", "d0_data_packet_ready",
                "d0_shadow_draft_allowed", "adversarial_p0_pass"):
        assert lock[key] is True, key
    assert lock["p0_open"] == 0


def test_tests_not_run_blocks_readiness():
    lock = compute_lock(_configs(), test_results=None)
    assert lock["status"] == "FAIL"
    assert lock["ready_for_book4"] is False
    assert lock["adversarial_p0_pass"] is None


def test_failing_tests_block_readiness():
    lock = compute_lock(_configs(),
                        test_results={"exit_code": 1, "passed": 230, "failed": 3,
                                      "summary": "230 passed, 3 failed"})
    assert lock["status"] == "FAIL"
    assert lock["adversarial_p0_pass"] is False


def test_missing_critical_precedence_chain_fails_lock():
    configs = _configs()
    del configs["precedence_matrix"]["precedence_matrix"]["legal_organization_name"]
    lock = _lock(configs)
    assert lock["status"] == "FAIL"
    assert lock["critical_facts_with_snapshot_lineage"] < 1.0
    assert lock["ready_for_book4"] is False


def test_broken_d0_packet_fails_lock():
    configs = _configs()
    configs["d0_data_packet"]["packet_sections"] = configs["d0_data_packet"]["packet_sections"][:-1]
    lock = _lock(configs)
    assert lock["status"] == "FAIL"
    assert lock["d0_data_packet_ready"] is False
    assert lock["d0_shadow_draft_allowed"] is False


def test_georgia_without_crawled_state_rule_fails_lock():
    configs = _configs()
    configs["georgia_profiles"].pop("crawled_state_rule", None)
    lock = _lock(configs)
    assert lock["status"] == "FAIL"
    assert lock["georgia_fixture_tests_pass"] is False


def test_enabled_source_without_adapter_version_fails_lock():
    configs = _configs()
    for s in configs["source_registry"]["sources"]:
        if s.get("enabled") is True:
            s["adapter_version"] = ""
            break
    lock = _lock(configs)
    assert lock["status"] == "FAIL"
    assert lock["enabled_sources_registered"] < 1.0


def test_injected_open_p0_fails_lock():
    configs = _configs()
    ledger = load_yaml(_ROOT / "config/g0/ratification/contradiction_ledger.yaml")
    ledger = copy.deepcopy(ledger)
    p1 = next(c for c in ledger["contradictions"] if c["severity"] == "P1")
    p1["severity"] = "P0"
    p1["status"] = "OPEN"
    p1.pop("resolution", None)
    lock = compute_lock(configs, test_results=PASSING_TESTS, ledger=ledger)
    assert lock["p0_open"] >= 1
    assert lock["status"] == "FAIL"
    assert lock["ready_for_book4"] is False


def test_readiness_is_conjunction():
    """Every boolean predicate must be explicitly True for readiness."""
    lock = _lock()
    for key in ("data_constitution_complete", "snapshot_immutability_tests_pass",
                "capture_replay_tests_pass", "extraction_lineage_tests_pass",
                "precedence_tests_pass", "freshness_tests_pass",
                "promotion_tests_pass", "conflict_tests_pass",
                "material_change_tests_pass", "dependency_invalidation_tests_pass",
                "identifier_verification_tests_pass",
                "statistic_semantics_tests_pass", "source_security_tests_pass",
                "retention_tests_pass", "provenance_chain_tests_pass",
                "federal_fixture_tests_pass", "georgia_fixture_tests_pass",
                "private_source_fixture_tests_pass", "d0_data_packet_ready",
                "d0_shadow_draft_allowed", "adversarial_p0_pass"):
        assert lock[key] is True, key
    assert lock["enabled_sources_registered"] >= 1.0
    assert lock["critical_facts_with_snapshot_lineage"] >= 1.0
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
        "Committed G0_B3_REALITY_LOCK.json is stale or hand-edited; "
        "regenerate it with tools/g0/build_book3_reality_lock.py"
    )
    assert committed["status"] == "PASS"
    assert committed["ready_for_book4"] is True
