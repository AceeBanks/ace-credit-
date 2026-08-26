"""B1.C3-C8 tests — actor catalog, authority ladder, capability registry,
approval policy, failure law, self-improvement governance.

Live registers pass the cross-checking validator; injected defects fail closed.
Also covers the plan's mandated scenario checks (draft allowed, submit denied,
worker non-inheritance, Personal-Hermes propose-not-promote).
"""
from __future__ import annotations

import copy
from pathlib import Path

import yaml

from tools.g0.validate_policy_package import load_package, validate

_ROOT = Path(__file__).resolve().parents[3]


def _live() -> dict:
    return load_package()


def _ok(data) -> tuple[bool, dict]:
    return validate(copy.deepcopy(data))


def test_live_policy_package_passes():
    ok, report = _ok(_live())
    assert ok, report["errors"]
    assert report["actor_count"] >= 13
    assert report["capability_count"] >= 55
    assert report["disabled_capability_count"] >= 5


def test_every_actor_has_authority_ceiling():
    for actor in _live()["actors"]["actors"]:
        assert actor.get("default_authority_ceiling"), actor["actor_type"]


def test_worker_does_not_inherit_ceo_capabilities():
    pkg = _live()
    actors = {a["actor_type"]: a for a in pkg["actors"]["actors"]}
    ceo = actors["ACTOR-HERMES-CEO"]
    worker = actors["ACTOR-WORKER"]
    # Worker's default allowed families are empty; grants are per-TaskContract.
    assert worker["allowed_capability_families"] == []
    assert "submission" in worker["forbidden_capability_families"]
    assert not worker["may_create_workers"]
    assert ceo["may_create_workers"]


def test_no_agent_is_canonical_data_authority():
    """No conversational agent may hold canonical mutation authority unilaterally."""
    for cap in _live()["capabilities"]["capabilities"]:
        if cap["side_effect_class"] == "CANONICAL_MUTATION" and \
                cap["phase_status"] == "ENABLED":
            for at in cap["allowed_actor_types"]:
                assert "HERMES" not in at or cap["approval_policy"] in ("AP2", "AP3"), \
                    f"{cap['capability_id']} lets {at} mutate canonically without approval"


def test_no_conversational_actor_holds_credentials():
    for actor in _live()["actors"]["actors"]:
        if actor["actor_type"].startswith("ACTOR-HERMES") or \
                actor["actor_type"] == "ACTOR-WORKER":
            assert not actor["may_hold_credentials"], actor["actor_type"]


def test_submission_disabled_and_drafting_enabled():
    caps = {c["capability_id"]: c for c in _live()["capabilities"]["capabilities"]}
    for cid in ("application.submit", "submission.execute", "submission.certify",
                "submission.sign"):
        assert caps[cid]["phase_status"] == "DISABLED"
        assert caps[cid]["approval_policy"] in ("APX",)
    for cid in ("application.draft_full_proposal", "application.draft_business_plan",
                "application.draft_pitch_deck"):
        assert caps[cid]["phase_status"] == "ENABLED"
        assert caps[cid]["minimum_level"] == "L2"


def test_email_send_denied_or_approval_gated_at_ceo_level():
    caps = {c["capability_id"]: c for c in _live()["capabilities"]["capabilities"]}
    send = caps["communication.send"]
    assert send["phase_status"] == "DISABLED" or "ACTOR-HERMES-CEO" not in send["allowed_actor_types"]


def test_personal_hermes_proposes_but_cannot_promote():
    caps = {c["capability_id"]: c for c in _live()["capabilities"]["capabilities"]}
    propose = caps["organization.propose_update"]
    accept = caps["organization.accept_verified_update"]
    assert "ACTOR-HERMES-PERSONAL" in propose["allowed_actor_types"]
    assert "ACTOR-HERMES-PERSONAL" not in accept["allowed_actor_types"]


def test_unknown_actor_reference_fails():
    data = _live()
    data["capabilities"]["capabilities"][0]["allowed_actor_types"].append("ACTOR-GHOST")
    ok, report = _ok(data)
    assert not ok
    assert any("ACTOR-GHOST" in e for e in report["errors"])


def test_ceiling_below_capability_fails():
    data = _live()
    for cap in data["capabilities"]["capabilities"]:
        if cap["capability_id"] == "budget.calculate":
            cap["allowed_actor_types"].append("ACTOR-WORKER")  # L2 < L3 required
            break
    ok, report = _ok(data)
    assert not ok
    assert any("below required" in e for e in report["errors"])


def test_enabling_l5_capability_fails_closed():
    data = _live()
    for cap in data["capabilities"]["capabilities"]:
        if cap["capability_id"] == "application.submit":
            cap["phase_status"] = "ENABLED"
    ok, report = _ok(data)
    assert not ok
    assert any("L5 capability must be DISABLED" in e for e in report["errors"])


def test_conversational_actor_with_credentials_fails():
    data = _live()
    for actor in data["actors"]["actors"]:
        if actor["actor_type"] == "ACTOR-HERMES-CEO":
            actor["may_hold_credentials"] = True
    ok, report = _ok(data)
    assert not ok
    assert any("credentials" in e for e in report["errors"])


def test_self_improvement_governance_blocks_self_ratification():
    gov = yaml.safe_load(
        (_ROOT / "config/g0/policy/self_improvement.yaml").read_text(encoding="utf-8"))
    ceo = gov["actor_permissions"]["ACTOR-HERMES-CEO"]
    assert "promote_own_authority_increase" in ceo["may_not"]
    assert "promote_change" not in [m.lower() for m in ceo["may"]]
    assert len(gov["promotion_lifecycle"]) == 11
    assert any("OTHER than any agent" in r for r in gov["hard_rules"])


def test_failure_matrix_fails_closed_for_security_classes():
    fm = yaml.safe_load(
        (_ROOT / "config/g0/policy/failure_matrix.yaml").read_text(encoding="utf-8"))
    by_id = {f["class_id"]: f for f in fm["failure_classes"]}
    assert by_id["F-AUTH"]["action"] == "FAIL_CLOSED"
    assert by_id["F-AUTH"]["degraded_modes"] == []
    assert by_id["F-TENANT"]["action"] == "FAIL_CLOSED"
    assert by_id["F-TENANT"]["degraded_modes"] == []


def test_all_capability_failure_modes_resolve():
    fm = yaml.safe_load(
        (_ROOT / "config/g0/policy/failure_matrix.yaml").read_text(encoding="utf-8"))
    valid = {f["class_id"] for f in fm["failure_classes"]}
    for cap in _live()["capabilities"]["capabilities"]:
        assert cap["failure_mode"] in valid, cap["capability_id"]
