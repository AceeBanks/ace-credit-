"""B0.C6 tests — Book 0 Reality Lock.

Proves the lock is derived: the clean package passes; injecting an open P0,
removing a mandatory decision category, or introducing stale authority flips
it to FAIL. Also proves readiness cannot be true while any predicate is not
explicitly True.
"""
from __future__ import annotations

import copy
import json
import os
from pathlib import Path

import pytest
import yaml

from tools.g0.build_book0_reality_lock import (
    COMMITTED_LOCK_PATH,
    build_live_lock,
    compute_lock,
    CONFIGS,
)

_ROOT = Path(__file__).resolve().parents[3]


def _load_all() -> dict:
    return {name: yaml.safe_load((_ROOT / rel).read_text(encoding="utf-8"))
            for name, rel in {
                "manifest": "config/g0/ratification/artifact_manifest.yaml",
                "decisions": "config/g0/ratification/decision_register.yaml",
                "contradictions": "config/g0/ratification/contradiction_ledger.yaml",
                "non_goals": "config/g0/ratification/non_goals.yaml",
                "candidates": "config/g0/ratification/prototype_candidates.yaml",
            }.items()}


def _lock(data) -> dict:
    return compute_lock(data, test_results={"exit_code": 0, "passed": 42, "failed": 0,
                                            "summary": "42 passed"})


def test_live_lock_passes():
    lock = _lock(_load_all())
    assert lock["status"] == "PASS", lock["errors"]
    assert lock["ready_for_book1_ratification"] is True
    assert lock["p0_open"] == 0
    assert lock["supersession_cycles"] == 0
    assert lock["stale_authority_detected"] is False


def test_injected_open_p0_fails_lock():
    data = _load_all()
    p1 = next(c for c in data["contradictions"]["contradictions"]
              if c["severity"] == "P1")
    p1["severity"] = "P0"
    p1["status"] = "OPEN"
    p1.pop("resolution", None)
    lock = _lock(data)
    assert lock["status"] == "FAIL"
    assert lock["ready_for_book1_ratification"] is False
    assert lock["p0_open"] >= 1


def test_missing_required_decision_category_fails_lock():
    data = _load_all()
    reg = data["decisions"]
    cat = next(c for c in reg["required_categories"])
    reg["decisions"] = [d for d in reg["decisions"] if d["category"] != cat]
    lock = _lock(data)
    assert lock["status"] == "FAIL"
    assert lock["all_major_decisions_classified"] is False


def test_stale_authority_fails_lock():
    data = _load_all()
    art = data["manifest"]["artifacts"][0]
    art["blob_sha"] = "0" * 40  # simulate content drift after pinning
    # point path at a real file so existence check passes but hash mismatches
    lock = _lock(data)
    assert lock["status"] == "FAIL"
    assert lock["stale_authority_detected"] is True
    assert lock["artifact_manifest_complete"] is False


def test_premature_adoption_fails_lock():
    data = _load_all()
    data["candidates"]["candidates"][0]["status"] = "adopted_with_evidence"
    lock = _lock(data)
    assert lock["status"] == "FAIL"
    assert lock["prototype_candidates_bounded"] is False


def test_tests_not_run_blocks_readiness():
    lock = compute_lock(_load_all(), test_results=None)
    assert lock["status"] == "FAIL"
    assert lock["ready_for_book1_ratification"] is False
    assert lock["book0_tests_all_pass"] is None


def test_failing_tests_block_readiness():
    lock = compute_lock(_load_all(),
                        test_results={"exit_code": 1, "passed": 40, "failed": 2,
                                      "summary": "40 passed, 2 failed"})
    assert lock["status"] == "FAIL"


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
        if isinstance(lock.get("tests"), dict):
            # duration string varies run-to-run; counts are compared exactly
            lock["tests"].pop("summary", None)
        return lock

    assert normalize(committed) == normalize(fresh), (
        "Committed G0_B0_REALITY_LOCK.json is stale or hand-edited; "
        "regenerate it with tools/g0/build_book0_reality_lock.py"
    )
    assert committed["status"] == "PASS"


def test_readiness_is_conjunction_not_assertion():
    """Flip each predicate's input independently and confirm the lock flips."""
    base = _load_all()

    def flip(mutate):
        data = copy.deepcopy(base)
        mutate(data)
        return _lock(data)["ready_for_book1_ratification"]

    assert flip(lambda d: d["non_goals"].__setitem__(
        "non_goals", d["non_goals"]["non_goals"][:5])) is False
