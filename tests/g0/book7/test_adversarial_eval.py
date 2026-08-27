"""B7.C29 — Adversarial evaluation suite.

Executes the 40 plan attacks (C29-01..40) and the 10 Humanizer attacks
(HZR-A..J) with hostile inputs; the system must BLOCK/DETECT every one.
All P0 cases must pass.
"""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

_ROOT = Path(__file__).resolve().parents[3]
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from prototype.g0.evaluation.adversarial import (  # noqa: E402
    HZR_ATTACKS,
    PLAN_ATTACKS,
    run_hzr_attacks,
    run_plan_attacks,
)


def _hostile_plan_inputs() -> dict:
    """Every attack attempted with the FAILING condition set."""
    return {
        "C29-01": {"generator_is_judge": True},
        "C29-02": {"judge_owner": "candidate-x", "candidate_id": "candidate-x"},
        "C29-03": {"style_up": True, "unsupported_up": True},
        "C29-04": {"cost_down": True, "coverage_down": True},
        "C29-05": {"faster": True, "table_lost": True},
        "C29-06": {"recall_up": True, "stale_returned": True},
        "C29-07": {"skill_expands_scope": True},
        "C29-08": {"unauthorized_tool_added": True},
        "C29-09": {"routed": True, "structured_reliable": False},
        "C29-10": {"anchor_dropped": True},
        "C29-11": {"leaked": True},
        "C29-12": {"did_ceo_work": True},
        "C29-13": {"accumulated": True},
        "C29-14": {"contacted": True},
        "C29-15": {"bypassed": True},
        "C29-16": {"enabled": True},
        "C29-17": {"injection_caused_pass": True},
        "C29-18": {"has_provenance": False},
        "C29-19": {"presented_as_human": True},
        "C29-20": {"entered_global": True},
        "C29-21": {"duplicated": True},
        "C29-22": {"duplicates": True},
        "C29-23": {"silent_mutation": True},
        "C29-24": {"verbosity_rewarded": True},
        "C29-25": {"concision_penalized": True},
        "C29-26": {"judge_overrode": True},
        "C29-27": {"disagreement_hidden": True},
        "C29-28": {"won_aggregate": True, "p0_failed": True},
        "C29-29": {"avg_ok": True, "deadline_wrong": True},
        "C29-30": {"rollback_missing": True},
        "C29-31": {"version_unclear": True},
        "C29-32": {"wrote_production": True},
        "C29-33": {"derived_without_approval": True},
        "C29-34": {"suppressed": True},
        "C29-35": {"changed_mid_benchmark": True},
        "C29-36": {"graceful_degrade": False},
        "C29-37": {"rebuild_impossible": True},
        "C29-38": {"reconstructable": False},
        "C29-39": {"used_as_label": True},
        "C29-40": {"claimed_without_baseline": True},
    }


def test_all_40_plan_attacks_blocked():
    r = run_plan_attacks(_hostile_plan_inputs())
    assert r["total"] == 40
    assert r["all_pass"] is True, [x for x in r["results"] if not x["pass"]]


def test_plan_attacks_are_red_green_provable():
    """With the defense disabled, every attempted attack succeeds — the
    suite is not vacuous (attacks genuinely catch defense regressions)."""
    r = run_plan_attacks(_hostile_plan_inputs(), defense_ok=False)
    assert r["failed"] >= 40
    assert r["all_pass"] is False


def test_hzr_attacks_are_red_green_provable():
    inputs = {"HZR-A": {"amount_changed": True}}
    r_off = run_hzr_attacks(inputs, defense_ok=False)
    assert r_off["all_pass"] is False
    r_on = run_hzr_attacks(inputs, defense_ok=True)
    assert r_on["all_pass"] is True


def test_all_10_humanizer_attacks_blocked():
    inputs = {
        "HZR-A": {"amount_changed": True},
        "HZR-B": {"deadline_changed": True},
        "HZR-C": {"name_replaced": True},
        "HZR-D": {"rewritten": True},
        "HZR-E": {"misclassified": True},
        "HZR-F": {"invented": True},
        "HZR-G": {"dropped": True},
        "HZR-H": {"removed": True},
        "HZR-I": {"converted": True},
        "HZR-J": {"prose_up": True, "factuality_down": True},
    }
    r = run_hzr_attacks(inputs)
    assert r["total"] == 10
    assert r["all_pass"] is True, [x for x in r["results"] if not x["pass"]]


def test_clean_inputs_pass_attacks():
    """When no attack condition is present, checks pass (system functional)."""
    clean = {k: {} for k in PLAN_ATTACKS}
    r = run_plan_attacks(clean)
    assert r["all_pass"] is True


def test_p0_security_attacks_all_blocked():
    """Security/submission/injection attacks are P0 and non-negotiable."""
    p0 = {
        "C29-11": {"leaked": True},
        "C29-15": {"bypassed": True},
        "C29-16": {"enabled": True},
        "C29-17": {"injection_caused_pass": True},
        "C29-20": {"entered_global": True},
        "C29-28": {"won_aggregate": True, "p0_failed": True},
    }
    r = run_plan_attacks(p0)
    assert r["all_pass"] is True


def test_each_attack_function_present_and_callable():
    from prototype.g0.evaluation import adversarial
    for attack_id, fn in PLAN_ATTACKS.items():
        assert callable(fn), attack_id
    for attack_id, fn in HZR_ATTACKS.items():
        assert callable(fn), attack_id


def test_attacks_detected_individually():
    """Each attack, run alone with its failing condition, must be blocked."""
    for attack_id, params in _hostile_plan_inputs().items():
        fn = PLAN_ATTACKS[attack_id]
        result = fn(**params)
        assert result.pass_ is True, f"{attack_id}: {result.detail}"
