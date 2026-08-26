"""B0.C4/C5 tests — non-goal freeze + prototype candidate register.

Live pass plus negatives: missing kind coverage, unknown enums, phantom
lineage, premature ADOPTED status, missing mandated candidate.
"""
from __future__ import annotations

from pathlib import Path

import yaml

from tools.g0.validate_freeze_registers import validate_candidates, validate_non_goals

_ROOT = Path(__file__).resolve().parents[3]


def _load(rel: str) -> dict:
    return yaml.safe_load((_ROOT / rel).read_text(encoding="utf-8"))


# ---------- C4 non-goals ----------

def test_live_non_goals_pass():
    ok, report = validate_non_goals(_load("config/g0/ratification/non_goals.yaml"))
    assert ok, report["errors"]
    assert report["non_goal_count"] >= 15


def test_all_three_kinds_represented():
    data = _load("config/g0/ratification/non_goals.yaml")
    kinds = {n["kind"] for n in data["non_goals"]}
    assert kinds == set(data["valid_kinds"])


def test_missing_kind_fails():
    def mutate(data):
        # remove every entry of one kind so coverage truly collapses
        data["non_goals"] = [n for n in data["non_goals"]
                             if n["kind"] != "future_extension_point"]
    data = _load("config/g0/ratification/non_goals.yaml")
    mutate(data)
    ok, report = validate_non_goals(data)
    assert not ok
    assert any("no non-goal of kind" in e for e in report["errors"])


def test_unknown_kind_fails():
    data = _load("config/g0/ratification/non_goals.yaml")
    data["non_goals"][0]["kind"] = "probably_fine"
    ok, _ = validate_non_goals(data)
    assert not ok


def test_phantom_source_in_non_goal_fails():
    data = _load("config/g0/ratification/non_goals.yaml")
    data["non_goals"][0]["source_artifact_ids"].append("GS-PHANTOM")
    ok, report = validate_non_goals(data)
    assert not ok
    assert any("phantom source artifact" in e for e in report["errors"])


# ---------- C5 candidates ----------

LIVE_CANDIDATES = "config/g0/ratification/prototype_candidates.yaml"


def test_live_candidates_pass():
    ok, report = validate_candidates(_load(LIVE_CANDIDATES))
    assert ok, report["errors"]
    assert not report["adopted_at_book0"]
    assert report["unique_ids"] == 10


def test_all_ten_mandated_candidates_present():
    data = _load(LIVE_CANDIDATES)
    ids = {c["candidate_id"] for c in data["candidates"]}
    assert ids == set(data["required_candidate_ids"])


def test_no_candidate_adopted_at_book0():
    for c in _load(LIVE_CANDIDATES)["candidates"]:
        assert c["status"] != "adopted_with_evidence", c["candidate_id"]


def test_premature_adoption_fails_gate():
    data = _load(LIVE_CANDIDATES)
    data["candidates"][0]["status"] = "adopted_with_evidence"
    ok, report = validate_candidates(data)
    assert not ok
    assert any("GATE VIOLATION" in e and "ADOPTED" in e for e in report["errors"])


def test_missing_mandated_candidate_fails():
    def mutate(data):
        data["candidates"] = [c for c in data["candidates"]
                              if c["candidate_id"] != "CAND-SEMANTICA"]
    data = _load(LIVE_CANDIDATES)
    mutate(data)
    ok, report = validate_candidates(data)
    assert not ok
    assert any("CAND-SEMANTICA" in e for e in report["errors"])


def test_unknown_status_fails():
    data = _load(LIVE_CANDIDATES)
    data["candidates"][0]["status"] = "sure_why_not"
    ok, _ = validate_candidates(data)
    assert not ok


def test_semantica_has_relational_baseline_counterpart():
    data = _load(LIVE_CANDIDATES)
    by_id = {c["candidate_id"]: c for c in data["candidates"]}
    sem = by_id["CAND-SEMANTICA"]
    base = by_id["CAND-RELATIONAL-BASELINE"]
    assert base["responsible_book"] == sem["responsible_book"], \
        "bake-off arms must share a responsible book for fair comparison"


def test_every_candidate_has_kill_criteria_and_license():
    for c in _load(LIVE_CANDIDATES)["candidates"]:
        assert len(c["kill_criteria"]) > 40, f"{c['candidate_id']} kill criteria too thin"
        status = c["license_status"].lower()
        assert any(kw in status for kw in ("license", "observed", "review",
                                           "no external dependency")), c["candidate_id"]
