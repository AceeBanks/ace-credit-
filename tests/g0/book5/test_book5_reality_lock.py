"""B5.C26 tests — Book 5 Reality Lock.

Proves the lock is DERIVED from evidence: the clean package passes; injecting
a defect — a broken evidence law, a missing edge family rule, an unknown
decision type, a broken contradiction config, a missing bake-off result, an
unratified storage ADR, a missing eval rule, a failing test run, or an open
P0 — flips readiness to FAIL. Behavioral predicates require BOTH valid
configs AND a green live test run. Also proves the committed lock equals a
fresh regeneration (stale-lock guard).
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

from tools.g0._common import load_yaml  # noqa: E402
from tools.g0.build_book5_reality_lock import (  # noqa: E402
    COMMITTED_LOCK_PATH,
    CONFIG_STEMS,
    EVIDENCE_CONFIG_DIR,
    build_live_lock,
    compute_lock,
)

PASSING_TESTS = {"exit_code": 0, "passed": 202, "failed": 0,
                 "summary": "202 passed"}
FAILING_TESTS = {"exit_code": 1, "passed": 199, "failed": 3,
                 "summary": "199 passed, 3 failed"}
PASSING_ADV = {"exit_code": 0, "passed": 90, "failed": 0,
               "summary": "90 passed"}
FAILING_ADV = {"exit_code": 1, "passed": 80, "failed": 10,
               "summary": "80 passed, 10 failed"}

GOOD_BAKEOFF = {"semantica_correct": 9, "baseline_correct": 9,
                "workloads": [
                    {"workload": "W7_rebuild_exit", "candidate": "semantica",
                     "correct": True}]}
GOOD_ADR = "Status: RATIFIED ... Pattern A — Relational canonical ..."


def _configs() -> dict:
    return {stem.removesuffix(".yaml"): load_yaml(EVIDENCE_CONFIG_DIR / stem)
            for stem in CONFIG_STEMS}


def _lock(configs: dict | None = None, **kw) -> dict:
    kw.setdefault("test_results", PASSING_TESTS)
    kw.setdefault("adversarial_results", PASSING_ADV)
    kw.setdefault("bakeoff", GOOD_BAKEOFF)
    kw.setdefault("adr_text", GOOD_ADR)
    return compute_lock(configs or _configs(), **kw)


TRUE_PREDICATES = (
    "evidence_constitution_complete", "provenance_model_pass",
    "evidence_graph_semantics_pass", "decision_record_pass",
    "historical_replay_pass", "contradiction_retention_pass",
    "dependency_invalidation_pass", "retrieval_authority_pass",
    "graph_rebuild_exit_pass", "vector_rebuild_exit_pass",
    "semantica_bakeoff_complete", "storage_adr_ratified",
    "tenant_isolation_pass", "claim_ledger_pass", "client_explanation_pass",
    "audit_evidence_linkage_pass", "eval_lineage_pass",
    "d0_d1_evidence_ready", "adversarial_p0_pass",
)


def test_live_lock_passes():
    lock = _lock()
    assert lock["status"] == "PASS", lock["evidence"]
    assert lock["ready_for_book6"] is True
    for key in TRUE_PREDICATES:
        assert lock[key] is True, key
    assert lock["p0_open"] == 0


def test_tests_not_run_blocks_readiness():
    lock = compute_lock(_configs(), test_results=None,
                        adversarial_results=None, bakeoff=GOOD_BAKEOFF,
                        adr_text=GOOD_ADR)
    assert lock["status"] == "FAIL"
    assert lock["ready_for_book6"] is False
    assert lock["adversarial_p0_pass"] is None
    assert lock["historical_replay_pass"] is False
    assert lock["dependency_invalidation_pass"] is False
    assert lock["vector_rebuild_exit_pass"] is False
    assert lock["tenant_isolation_pass"] is False


def test_failing_tests_block_readiness():
    lock = _lock(test_results=FAILING_TESTS)
    assert lock["status"] == "FAIL"
    assert lock["ready_for_book6"] is False
    for key in ("historical_replay_pass", "dependency_invalidation_pass",
                "vector_rebuild_exit_pass", "tenant_isolation_pass"):
        assert lock[key] is False, key


def test_failing_adversarial_suite_blocks_readiness():
    lock = _lock(adversarial_results=FAILING_ADV)
    assert lock["status"] == "FAIL"
    assert lock["adversarial_p0_pass"] is False


def test_broken_evidence_constitution_flips_fail():
    cfg = _configs()
    bad = copy.deepcopy(cfg["evidence_constitution"])
    bad["laws"] = [l for l in bad["laws"] if not str(l.get("id")).startswith("EVID-LAW-")]
    lock = _lock({**_configs(), "evidence_constitution": bad})
    assert lock["evidence_constitution_complete"] is False
    assert lock["status"] == "FAIL"


def test_missing_provenance_rule_flips_fail():
    cfg = _configs()
    bad = copy.deepcopy(cfg["evidence_edge_types"])
    bad["hard_rules"] = [h for h in bad.get("hard_rules", [])
                         if h.get("id") != "GRAPH-002"]
    lock = _lock({**cfg, "evidence_edge_types": bad})
    assert lock["provenance_model_pass"] is False
    assert lock["status"] == "FAIL"


def test_unknown_decision_type_flips_fail():
    cfg = _configs()
    bad = copy.deepcopy(cfg["decision_types"])
    bad["decision_types"].append({"id": "INVENTED_TYPE",
                                   "replay_mode": "DETERMINISTIC"})
    lock = _lock({**cfg, "decision_types": bad})
    assert lock["decision_record_pass"] is False
    assert lock["status"] == "FAIL"


def test_broken_contradiction_config_flips_fail():
    cfg = _configs()
    bad = copy.deepcopy(cfg["contradiction_types"])
    bad["contradiction_types"][0] = {"id": "NOT_A_REAL_TYPE", "text": "x"}
    lock = _lock({**cfg, "contradiction_types": bad})
    assert lock["contradiction_retention_pass"] is False
    assert lock["status"] == "FAIL"


def test_missing_bakeoff_blocks_graph_rebuild_and_complete():
    lock = _lock(bakeoff=None)
    assert lock["semantica_bakeoff_complete"] is False
    assert lock["graph_rebuild_exit_pass"] is False
    assert lock["status"] == "FAIL"


def test_unratified_adr_blocks_readiness():
    lock = _lock(adr_text="DRAFT — no decision recorded")
    assert lock["storage_adr_ratified"] is False
    assert lock["status"] == "FAIL"


def test_missing_eval_rule_flips_fail():
    cfg = _configs()
    bad = copy.deepcopy(cfg["eval_lineage_policy"])
    bad["rules"] = [r for r in bad.get("rules", []) if r.get("id") != "EVAL-005"]
    lock = _lock({**cfg, "eval_lineage_policy": bad})
    assert lock["eval_lineage_pass"] is False
    assert lock["status"] == "FAIL"


def test_broken_explanation_policy_flips_fail():
    cfg = _configs()
    bad = copy.deepcopy(cfg["explanation_policy"])
    bad["citation_rules"] = [r for r in bad.get("citation_rules", [])
                             if r.get("id") != "EXPL-002"]
    lock = _lock({**cfg, "explanation_policy": bad})
    assert lock["client_explanation_pass"] is False
    assert lock["status"] == "FAIL"


@pytest.mark.skipif(os.environ.get("G0_SKIP_LOCK_FRESHNESS") == "1",
                    reason="recursion guard for the lock builder's inner run")
def test_committed_lock_matches_fresh_regeneration():
    """Stale-lock guard: the committed lock must equal an honest fresh
    regeneration from live repository evidence; PASS cannot be faked by
    hand-editing the JSON."""
    committed = json.loads(COMMITTED_LOCK_PATH.read_text(encoding="utf-8"))
    fresh = build_live_lock()

    def normalize(lock: dict) -> dict:
        lock = copy.deepcopy(lock)
        lock.get("evidence", {}).get("test_results", {}).pop("summary", None)
        lock.get("evidence", {}).get("adversarial_results", {})\
            .pop("summary", None)
        return lock

    assert normalize(committed) == normalize(fresh), (
        "Committed G0_B5_REALITY_LOCK.json is stale or hand-edited; "
        "regenerate with python tools/g0/build_book5_reality_lock.py")
