"""B4.C28 tests — Book 4 Reality Lock.

Proves the lock is DERIVED from evidence: the clean package passes; injecting
a CEO-only capability into Personal's boundary, a canonical-mutation role
contract, a missing never-inject class, a broken intent schema, a missing
memory class, a missing compaction anchor, a broken D1 label, a missing
secret-scan schema, failing tests, or an open P0 flips readiness to FAIL.
Behavioral predicates (cold reconstruction, multi-project/tenant isolation,
secret memory) require BOTH valid configs AND a green live test run. Also
proves the committed lock equals a fresh regeneration (stale-lock guard).
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

from tools.g0._common import AGENTS_CONFIG_DIR, load_yaml  # noqa: E402
from tools.g0.build_book4_reality_lock import (  # noqa: E402
    COMMITTED_LOCK_PATH,
    STEMS,
    build_live_lock,
    compute_lock,
)

PASSING_TESTS = {"exit_code": 0, "passed": 202, "failed": 0,
                 "summary": "202 passed"}
FAILING_TESTS = {"exit_code": 1, "passed": 199, "failed": 3,
                 "summary": "199 passed, 3 failed"}


def _configs() -> dict:
    return {stem.removesuffix(".yaml"): load_yaml(AGENTS_CONFIG_DIR / stem)
            for stem in STEMS}


def _lock(configs: dict | None = None, test_results: dict | None = None) -> dict:
    return compute_lock(configs or _configs(),
                        test_results=test_results or PASSING_TESTS)


TRUE_PREDICATES = (
    "dual_hermes_boundary_ratified", "personal_contract_complete",
    "ceo_contract_complete", "intent_contract_tests_pass",
    "clarification_protocol_pass", "task_contract_tests_pass",
    "sidechain_isolation_pass", "outcome_explanation_separation_pass",
    "personal_memory_policy_pass", "ceo_memory_policy_pass",
    "worker_stateless_default", "promotion_supersession_tests_pass",
    "compaction_anchor_tests_pass", "cold_reconstruction_pass",
    "multi_project_isolation_pass", "multi_tenant_memory_isolation_pass",
    "secret_memory_tests_pass", "d1_mock_draft_ready",
    "adversarial_p0_pass",
)


def test_live_lock_passes():
    lock = _lock()
    assert lock["status"] == "PASS", lock["evidence"]
    assert lock["ready_for_book5"] is True
    assert lock["d1_mock_draft_unlocked"] is True
    for key in TRUE_PREDICATES:
        assert lock[key] is True, key
    assert lock["p0_open"] == 0


def test_tests_not_run_blocks_readiness():
    lock = compute_lock(_configs(), test_results=None)
    assert lock["status"] == "FAIL"
    assert lock["ready_for_book5"] is False
    assert lock["adversarial_p0_pass"] is None
    # behavioral predicates also must not claim True without test evidence
    assert lock["cold_reconstruction_pass"] is False
    assert lock["multi_project_isolation_pass"] is False
    assert lock["multi_tenant_memory_isolation_pass"] is False
    assert lock["secret_memory_tests_pass"] is False


def test_failing_tests_block_readiness():
    lock = compute_lock(_configs(), test_results=FAILING_TESTS)
    assert lock["status"] == "FAIL"
    assert lock["adversarial_p0_pass"] is False
    assert lock["ready_for_book5"] is False


def test_boundary_defect_fails_lock():
    configs = _configs()
    personal = next(r for r in configs["dual_hermes_boundary"]["roles"]
                    if r["role_id"] == "PERSONAL_HERMES")
    personal["capabilities"].append("research.funder")  # CEO-only
    lock = _lock(configs)
    assert lock["status"] == "FAIL"
    assert lock["dual_hermes_boundary_ratified"] is False
    assert lock["ready_for_book5"] is False


def test_role_contract_defect_fails_lock():
    configs = _configs()
    configs["role_contracts"]["personal_contract"]["canonical_mutation_allowed"] = True
    lock = _lock(configs)
    assert lock["personal_contract_complete"] is False
    assert lock["status"] == "FAIL"


def test_worker_context_defect_fails_lock():
    configs = _configs()
    configs["worker_context_policy"]["never_inject"] = [
        c for c in configs["worker_context_policy"]["never_inject"]
        if c != "RAW_SECRETS"]
    lock = _lock(configs)
    assert lock["task_contract_tests_pass"] is False
    assert lock["secret_memory_tests_pass"] is False
    assert lock["status"] == "FAIL"


def test_memory_class_defect_fails_lock():
    configs = _configs()
    configs["personal_memory_classes"]["classes"] = [
        c for c in configs["personal_memory_classes"]["classes"]
        if c["class_id"] != "PM-PREFERENCE"]
    lock = _lock(configs)
    assert lock["personal_memory_policy_pass"] is False
    assert lock["status"] == "FAIL"


def test_compaction_anchor_defect_fails_lock():
    configs = _configs()
    configs["compaction_policy"]["mandatory_anchors"].remove(
        "EXACT_ACTIVE_OPPORTUNITY_REVISION")
    lock = _lock(configs)
    assert lock["compaction_anchor_tests_pass"] is False
    assert lock["status"] == "FAIL"


def test_d1_label_defect_fails_lock():
    configs = _configs()
    configs["d1_mock_draft_contract"]["label"] = "REAL_SUBMISSION"
    lock = _lock(configs)
    assert lock["d1_mock_draft_ready"] is False
    assert lock["status"] == "FAIL"


def test_intent_schema_defect_fails_lock(monkeypatch, tmp_path):
    import tools.g0.validate_intent_clarification as mod
    broken = json.loads(
        (Path(_ROOT) / "schemas/g0/agents/intent_contract.schema.json")
        .read_text(encoding="utf-8"))
    # weaken the ASSERTION-only constraint — a schema that allows canonical
    # user assertions must fail the lock
    broken["properties"]["user_assertions"]["items"]["properties"]["status"] = \
        {"type": "string"}
    (tmp_path / "intent_contract.schema.json").write_text(
        json.dumps(broken), encoding="utf-8")
    (tmp_path / "clarification_request.schema.json").write_text(
        (Path(_ROOT) / "schemas/g0/agents/clarification_request.schema.json")
        .read_text(encoding="utf-8"), encoding="utf-8")
    monkeypatch.setattr(mod, "SCHEMAS_DIR", tmp_path)
    lock = _lock()
    assert lock["intent_contract_tests_pass"] is False
    assert lock["status"] == "FAIL"


def test_sidechain_schema_defect_fails_lock(monkeypatch, tmp_path):
    import tools.g0.validate_sidechain_synthesis as mod
    # remove secret_scan from the sidechain manifest schema
    broken = json.loads(
        (Path(_ROOT) / "schemas/g0/agents/sidechain_manifest.schema.json")
        .read_text(encoding="utf-8"))
    del broken["properties"]["secret_scan"]
    (tmp_path / "sidechain_manifest.schema.json").write_text(
        json.dumps(broken), encoding="utf-8")
    for name in ("worker_result.schema.json", "outcome_artifact.schema.json"):
        (tmp_path / name).write_text(
            (Path(_ROOT) / "schemas/g0/agents" / name)
            .read_text(encoding="utf-8"), encoding="utf-8")
    monkeypatch.setattr(mod, "SCHEMAS_DIR", tmp_path)
    lock = _lock()
    assert lock["sidechain_isolation_pass"] is False
    assert lock["status"] == "FAIL"


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
    assert lock["ready_for_book5"] is False


def test_readiness_is_conjunction():
    """Every boolean predicate must be explicitly True for readiness."""
    lock = _lock()
    for key in TRUE_PREDICATES:
        assert lock[key] is True, key
    assert lock["p0_open"] == 0


def test_behavioral_predicates_require_green_tests():
    """Cold reconstruction / isolation / secret-memory claims are not true
    merely because the configs are valid — the live suite must be green."""
    lock = _lock()
    assert lock["cold_reconstruction_pass"] is True
    assert lock["multi_project_isolation_pass"] is True
    assert lock["multi_tenant_memory_isolation_pass"] is True
    assert lock["secret_memory_tests_pass"] is True
    blocked = compute_lock(_configs(), test_results=FAILING_TESTS)
    assert blocked["cold_reconstruction_pass"] is False


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
        lock.get("evidence", {}).get("adversarial_results", {}).pop("summary", None)
        return lock

    assert normalize(committed) == normalize(fresh), (
        "Committed G0_B4_REALITY_LOCK.json is stale or hand-edited; "
        "regenerate it with tools/g0/build_book4_reality_lock.py"
    )
    assert committed["status"] == "PASS"
    assert committed["ready_for_book5"] is True
