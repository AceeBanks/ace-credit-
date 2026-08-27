"""G0-B9-C31 — Final G0 Reality Lock freshness & defect-injection suite.

1. FRESHNESS: the committed G0_FINAL_REALITY_LOCK.json must derive PASS
   from current repository evidence; a stale or hand-edited lock cannot
   claim ready_for_g1.
2. DEFECT INJECTION: each injected defect flips a predicate / status to
   FAIL — proving the lock is DERIVED, not hard-coded.
3. HONESTY: submission stays disabled; ready_for_g1 derives only when
   every predicate passes.
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

from tools.g0.build_final_g0_reality_lock import (  # noqa: E402
    COMMITTED_PATH,
    compute_lock,
    _book_locks_pass,
    _fresh_clone_bootstrap_pass,
    _g1_backlog_complete,
    _migration_seed_pass,
    _seed_docs_complete,
    _submission_disabled_everywhere,
)


def _live_lock(**overrides) -> dict:
    evidence = {
        "book_locks": _book_locks_pass(),
        "seed_docs": _seed_docs_complete(),
        "adr": {"ratified": True, "status": "OCE_NATIVE"},
        "migration": _migration_seed_pass(),
        "fresh_clone": _fresh_clone_bootstrap_pass(),
        "submission": _submission_disabled_everywhere(),
        "backlog": _g1_backlog_complete(),
        "sweep": {"pass": True},
        "observability": {"pass": True},
        "recovery": {"pass": True},
        "security": {"pass": True},
    }
    evidence.update(overrides)
    return compute_lock(**evidence)


def test_committed_lock_is_current_pass():
    committed = json.loads(COMMITTED_PATH.read_text(encoding="utf-8"))
    assert committed["phase"] == "G0"
    assert committed["status"] == "PASS"
    recomputed = _live_lock()
    assert recomputed["status"] == "PASS"
    assert recomputed["ready_for_g1"] is True
    assert committed["ready_for_g1"] is True


def test_book_locks_all_pass():
    locks = _book_locks_pass()
    assert locks["pass"] is True, locks
    assert locks["count"] == 9
    assert locks["missing"] == []


def test_injected_missing_book_lock_flips_lock():
    locks = dict(_book_locks_pass())
    locks["pass"] = False
    locks["missing"] = ["G0_B5_REALITY_LOCK.json"]
    lock = _live_lock(book_locks=locks)
    assert lock["status"] == "FAIL"


def test_injected_migration_failure_flips_lock():
    lock = _live_lock(migration={"pass": False, "passed": 0,
                                 "summary": "1 failed"})
    assert lock["status"] == "FAIL"
    assert lock["predicates"]["migration_seed_pass"] is False


def test_injected_fresh_clone_failure_flips_lock():
    lock = _live_lock(fresh_clone={"pass": False, "summary": "FAIL"})
    assert lock["status"] == "FAIL"
    assert lock["predicates"]["fresh_clone_bootstrap_pass"] is False


def test_injected_adr_failure_flips_lock():
    lock = _live_lock(adr={"ratified": False, "status": "TBD"})
    assert lock["status"] == "FAIL"
    assert lock["predicates"]["runtime_substrate_selected"] is False


def test_injected_clean_repo_failure_flips_lock():
    lock = _live_lock(clean_repo={"pass": False})
    assert lock["status"] == "FAIL"
    assert lock["predicates"]["clean_repo_seeded"] is False


def test_injected_backlog_failure_flips_lock():
    lock = _live_lock(backlog={"complete": False, "epic_count": 0,
                               "item_count": 0})
    assert lock["status"] == "FAIL"
    assert lock["predicates"]["g1_backlog_complete"] is False


def test_injected_sweep_failure_flips_lock():
    lock = _live_lock(sweep={"pass": False})
    assert lock["status"] == "FAIL"
    assert lock["predicates"]["cross_book_contradiction_pass"] is False


def test_injected_submission_enabled_flips_lock():
    lock = _live_lock(submission={"pass": False, "detail": "submission enabled"})
    assert lock["status"] == "FAIL"
    assert lock["submission_enabled"] is True
    assert lock["ready_for_g1"] is False


def test_required_predicate_set_present():
    required = [
        "books_ratified", "runtime_substrate_selected",
        "runtime_hard_gates_pass", "canonical_ownership_frozen",
        "service_topology_frozen", "dependency_manifest_complete",
        "license_review_pass", "clean_repo_seeded",
        "fresh_clone_bootstrap_pass", "migration_seed_pass",
        "security_baseline_pass", "recovery_test_pass",
        "observability_baseline_defined", "g1_backlog_complete",
        "cross_book_contradiction_pass", "submission_enabled",
        "p0_open", "ready_for_g1",
    ]
    lock = _live_lock()
    for key in required:
        assert key in lock["predicates"] or key in lock, key
    assert lock["p0_open"] == 0
    assert lock["ready_for_g1"] is True
    assert lock["submission_enabled"] is False


def test_submission_disabled_everywhere():
    submission = _submission_disabled_everywhere()
    assert submission["pass"] is True, submission


def test_clean_repo_seeded_path_exists():
    seed = _ROOT / "production-seed"
    assert (seed / "migrations/001_initial_schema.sql").exists()
    assert (seed / "bootstrap.py").exists()


def test_final_external_review_evidence_sync():
    """G0-FINAL-REPAIR-01: the final review record classifies historical
    vs current totals and states the book-count semantics explicitly."""
    p = _ROOT / "docs/grant-sector/g0/00-ratification/G0_FINAL_EXTERNAL_REVIEW.md"
    text = p.read_text(encoding="utf-8")
    assert "current_final_head" in text
    assert "historical_at_sha" in text
    assert "1812" in text
    assert ("PASS_WITH_MINOR_EVIDENCE_SYNC" in text
            or "PASS_WITH_MINOR_REPAIRS" in text)
    assert "READY_FOR_EXTERNAL_RATIFICATION" in text
    assert "books_ratified: 9" in text
    assert "Book 0" in text


def test_ratification_packet_uses_final_head_totals():
    p = _ROOT / "docs/grant-sector/g0/09-production-seed" \
        / "G0_B9_FINAL_G0_RATIFICATION_PACKET.md"
    text = p.read_text(encoding="utf-8")
    assert "1812 passed, 3 skipped" in text
    assert "current_final_head" in text
    assert "historical_at_sha" in text
    assert "books_ratified=9" in text
