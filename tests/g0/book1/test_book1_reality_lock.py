"""B1.C16 tests — Book 1 Reality Lock.

Proves the lock is DERIVED from evidence: the clean package passes; injecting
an enabled submission path, an open P0, missing audit metadata, or
self-ratifying self-improvement flips it to FAIL. Also proves readiness
cannot be true while any predicate is not explicitly True, and that the
committed lock equals a fresh regeneration (stale-lock attack guard).
"""
from __future__ import annotations

import copy
import json
import os
from pathlib import Path

import pytest
import yaml

from tools.g0.build_book1_reality_lock import (
    COMMITTED_LOCK_PATH,
    build_live_lock,
    compute_lock,
    CONFIGS,
)
from tools.g0._common import POLICY_CONFIG_DIR, load_yaml

_ROOT = Path(__file__).resolve().parents[3]
PASSING_TESTS = {"exit_code": 0, "passed": 42, "failed": 0, "summary": "42 passed"}


def _load_configs() -> dict:
    return {
        "constitution": load_yaml(CONFIGS["constitution"]),
        "package": {
            "actors": load_yaml(POLICY_CONFIG_DIR / "actor_catalog.yaml"),
            "ladder": load_yaml(POLICY_CONFIG_DIR / "authority_matrix.yaml"),
            "capabilities": load_yaml(POLICY_CONFIG_DIR / "capability_registry.yaml"),
            "approvals": load_yaml(POLICY_CONFIG_DIR / "approval_matrix.yaml"),
            "failures": load_yaml(POLICY_CONFIG_DIR / "failure_matrix.yaml"),
        },
        "policy_dir": str(POLICY_CONFIG_DIR),
        "ledger": load_yaml(_ROOT / "config/g0/ratification/contradiction_ledger.yaml"),
    }


def _lock(configs: dict | None = None, test_results: dict | None = None) -> dict:
    return compute_lock(configs or _load_configs(),
                        test_results=test_results or PASSING_TESTS)


def test_live_lock_passes():
    lock = _lock()
    assert lock["status"] == "PASS", lock["evidence"]
    assert lock["ready_for_book2"] is True
    assert lock["constitution_complete"] is True
    assert lock["client_phase1_coverage"] == 1.0
    assert lock["actors_with_authority_ceiling"] == 1.0
    assert lock["capabilities_with_policy_metadata"] == 1.0
    assert lock["unknown_defaults_deny"] is True
    assert lock["tenant_scope_tests_pass"] is True
    assert lock["submission_disabled"] is True
    assert lock["drafting_enabled_l2"] is True
    assert lock["self_improvement_tests_pass"] is True
    assert lock["secret_boundary_tests_pass"] is True
    assert lock["adversarial_p0_pass"] is True
    assert lock["p0_open"] == 0


def test_tests_not_run_blocks_readiness():
    lock = compute_lock(_load_configs(), test_results=None)
    assert lock["status"] == "FAIL"
    assert lock["ready_for_book2"] is False
    assert lock["adversarial_p0_pass"] is None


def test_failing_tests_block_readiness():
    lock = compute_lock(_load_configs(),
                        test_results={"exit_code": 1, "passed": 40, "failed": 2,
                                      "summary": "40 passed, 2 failed"})
    assert lock["status"] == "FAIL"
    assert lock["adversarial_p0_pass"] is False


def test_injected_open_p0_fails_lock():
    configs = _load_configs()
    ledger = copy.deepcopy(configs["ledger"])
    p1 = next(c for c in ledger["contradictions"] if c["severity"] == "P1")
    p1["severity"] = "P0"
    p1["status"] = "OPEN"
    p1.pop("resolution", None)
    configs["ledger"] = ledger
    lock = _lock(configs)
    assert lock["status"] == "FAIL"
    assert lock["p0_open"] >= 1
    assert lock["ready_for_book2"] is False


def test_missing_audit_metadata_fails_lock():
    configs = _load_configs()
    caps = configs["package"]["capabilities"]["capabilities"]
    next(c for c in caps if c["capability_id"] == "opportunity.search").pop("audit_class")
    lock = _lock(configs)
    assert lock["status"] == "FAIL"
    assert lock["capabilities_with_policy_metadata"] == 0.0
    assert lock["ready_for_book2"] is False


def test_enabled_submission_fails_lock(tmp_path):
    """CD-003: submission_disabled is derived from registry evidence."""
    configs = _load_configs()
    tmp = tmp_path / "policy"
    import shutil
    shutil.copytree(POLICY_CONFIG_DIR, tmp)
    reg = yaml.safe_load((tmp / "capability_registry.yaml").read_text(encoding="utf-8"))
    for cap in reg["capabilities"]:
        if cap["capability_id"] == "application.submit":
            cap["phase_status"] = "ENABLED"
            cap["approval_policy"] = "AP0"
    (tmp / "capability_registry.yaml").write_text(yaml.safe_dump(reg), encoding="utf-8")
    configs["policy_dir"] = str(tmp)
    lock = _lock(configs)
    assert lock["status"] == "FAIL"
    assert lock["submission_disabled"] is False
    assert lock["ready_for_book2"] is False


def test_self_ratification_fails_lock(tmp_path):
    configs = _load_configs()
    tmp = tmp_path / "policy"
    import shutil
    shutil.copytree(POLICY_CONFIG_DIR, tmp)
    gov = yaml.safe_load((tmp / "self_improvement.yaml").read_text(encoding="utf-8"))
    gov["actor_permissions"]["ACTOR-HERMES-CEO"]["may"].append("promote_change")
    (tmp / "self_improvement.yaml").write_text(yaml.safe_dump(gov), encoding="utf-8")
    configs["policy_dir"] = str(tmp)
    lock = _lock(configs)
    assert lock["status"] == "FAIL"
    assert lock["self_improvement_tests_pass"] is False
    assert lock["ready_for_book2"] is False


def test_readiness_is_conjunction():
    """Every boolean predicate must be explicitly True for readiness."""
    lock = _lock()
    for key in ("constitution_complete", "unknown_defaults_deny",
                "tenant_scope_tests_pass", "submission_disabled",
                "drafting_enabled_l2", "self_improvement_tests_pass",
                "secret_boundary_tests_pass", "adversarial_p0_pass"):
        assert lock[key] is True, key
    for key in ("client_phase1_coverage", "actors_with_authority_ceiling",
                "capabilities_with_policy_metadata"):
        assert lock[key] >= 1.0, key
    assert lock["p0_open"] == 0


@pytest.mark.skipif(
    os.environ.get("G0_SKIP_LOCK_FRESHNESS") == "1",
    reason="recursion guard: inner lock-build pytest runs skip this test",
)
def test_committed_lock_matches_regeneration():
    """REPAIR-01 (stale-lock attack): the COMMITTED lock file must equal what an
    honest regeneration from live repository evidence produces right now.
    A hand-edited or stale lock fails this test — PASS cannot be faked by
    editing JSON."""
    committed = json.loads(COMMITTED_LOCK_PATH.read_text(encoding="utf-8"))
    fresh = build_live_lock()

    def normalize(lock: dict) -> dict:
        lock = copy.deepcopy(lock)
        # the pytest summary string embeds a run-to-run duration; counts and
        # exit code are compared exactly
        lock.get("evidence", {}).get("test_results", {}).pop("summary", None)
        return lock

    assert normalize(committed) == normalize(fresh), (
        "Committed G0_B1_REALITY_LOCK.json is stale or hand-edited; "
        "regenerate it with tools/g0/build_book1_reality_lock.py"
    )
    assert committed["status"] == "PASS"
