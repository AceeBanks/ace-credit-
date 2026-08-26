"""B1.C15 tests — Book Integration Tests (plan §18).

The fifteen mandatory assertions of the Book 1 constitution, evaluated
together against the live registers + executable policy prototype, plus the
coverage targets (100% policy metadata, P0 blocked, no submission path).
"""
from __future__ import annotations

from pathlib import Path

import pytest
import yaml

from prototype.g0.policy.evaluator import evaluate
from prototype.g0.policy.models import (
    Actor,
    AuthorityLevel,
    Decision,
    PolicyContext,
    Reason,
    TaskScope,
)
from prototype.g0.policy.registry import PolicyRegistry
from tools.g0.validate_constitution import validate as validate_constitution
from tools.g0.validate_policy_package import load_package, validate as validate_package
from tests.g0.book1.test_client_vision_coverage import CLIENT_REQUIREMENTS

_ROOT = Path(__file__).resolve().parents[3]
POLICY = _ROOT / "config/g0/policy"
TENANT = "tenant-alpha"


def _ceo() -> Actor:
    return Actor("ceo-1", "ACTOR-HERMES-CEO", (TENANT,), AuthorityLevel.L2)


def _ctx(resource_type: str) -> PolicyContext:
    return PolicyContext(tenant_id=TENANT, project_id="proj-1",
                         resource_type=resource_type)


@pytest.fixture(scope="module")
def reg() -> PolicyRegistry:
    return PolicyRegistry.load()


def _caps_raw() -> dict:
    data = load_package()
    return {c["capability_id"]: c for c in data["capabilities"]["capabilities"]}


def _actors_raw() -> dict:
    data = load_package()
    return {a["actor_type"]: a for a in data["actors"]["actors"]}


# --- 1-2. ceilings / minimum authority ---------------------------------------
def test_1_every_actor_has_authority_ceiling():
    for actor in _actors_raw().values():
        assert actor.get("default_authority_ceiling"), actor["actor_type"]


def test_2_every_capability_has_minimum_authority():
    for cap in _caps_raw().values():
        assert cap.get("minimum_level"), cap["capability_id"]


# --- 3. client deliverables -> legal capabilities ------------------------------
def test_3_phase1_deliverables_map_to_legal_capabilities():
    reg = PolicyRegistry.load()
    caps = {c.capability_id: c for c in reg._capabilities.values()}
    for req in CLIENT_REQUIREMENTS:
        if not req["constitution_allows"]:
            continue  # CR-13 submission is deliberately blocked
        assert req["capability_ids"], req["client_requirement_id"]
        for cid in req["capability_ids"]:
            assert cid in caps, f"{req['client_requirement_id']}: {cid} missing"


# --- 4. submission disabled -----------------------------------------------------
def test_4_submission_remains_disabled():
    caps = _caps_raw()
    for cid in ("application.submit", "submission.prepare", "submission.execute",
                "submission.certify", "submission.sign"):
        assert caps[cid]["phase_status"] == "DISABLED", cid
        assert caps[cid]["approval_policy"] == "APX", cid


# --- 5. drafting enabled at L2 ---------------------------------------------------
def test_5_drafting_enabled_at_l2(reg):
    caps = _caps_raw()
    for cid in ("application.draft_full_proposal", "application.draft_business_plan",
                "application.draft_pitch_deck", "application.draft_goal_sheet",
                "application.draft_section"):
        assert caps[cid]["phase_status"] == "ENABLED", cid
        assert caps[cid]["minimum_level"] == "L2", cid
        r = evaluate(reg, _ceo(), cid, _ctx(caps[cid]["resource_types"][0]))
        assert r.decision in (Decision.ALLOW, Decision.REQUIRE_APPROVAL), cid


# --- 6. unknown defaults deny -----------------------------------------------------
def test_6_unknown_actor_and_capability_default_deny(reg):
    r1 = evaluate(reg, None, "opportunity.search", _ctx("opportunity"))
    assert (r1.decision, r1.reason_code) == (Decision.DENY, Reason.UNKNOWN_ACTOR)
    r2 = evaluate(reg, _ceo(), "grant.auto_apply_all", _ctx("opportunity"))
    assert (r2.decision, r2.reason_code) == (Decision.DENY, Reason.UNKNOWN_CAPABILITY)


# --- 7. tenant scope required ------------------------------------------------------
def test_7_tenant_scope_required_for_tenant_resources(reg):
    caps = _caps_raw()
    for cid, cap in caps.items():
        if not cap["requires_tenant_scope"]:
            continue
        r = evaluate(reg, _ceo(), cid,
                     PolicyContext(tenant_id=None, project_id="proj-1",
                                   resource_type=cap["resource_types"][0]))
        assert r.decision is Decision.DENY, cid
        assert r.reason_code in (Reason.TENANT_SCOPE_MISSING, Reason.ACTOR_TYPE_DENIED)


# --- 8. workers cannot inherit broad parent authority --------------------------------
def test_8_workers_cannot_inherit_parent_authority(reg):
    actors = _actors_raw()
    assert actors["ACTOR-WORKER"]["allowed_capability_families"] == []
    task = TaskScope("t1", frozenset({"research.winner"}), TENANT, "proj-1",
                     AuthorityLevel.L2)
    w = Actor("worker-9", "ACTOR-WORKER", (TENANT,), AuthorityLevel.L2)
    ok = evaluate(reg, w, "research.winner", PolicyContext(
        tenant_id=TENANT, project_id="proj-1", resource_type="research_pack",
        task_scope=task))
    assert ok.decision is Decision.ALLOW  # in-task, bounded
    bad = evaluate(reg, w, "system.promote_change",
                   PolicyContext(tenant_id=TENANT, project_id=None,
                                 resource_type="system_state", task_scope=task))
    assert bad.decision is Decision.DENY  # out of worker authority entirely


# --- 9. Personal Hermes cannot bypass CEO/control plane -------------------------------
def test_9_personal_hermes_cannot_bypass_control_plane(reg):
    personal = Actor("personal-1", "ACTOR-HERMES-PERSONAL", (TENANT,),
                     AuthorityLevel.L1)
    for cid in ("system.promote_change", "system.propose_change",
                "organization.accept_verified_update", "application.submit"):
        r = evaluate(reg, personal, cid,
                     _ctx(_caps_raw()[cid]["resource_types"][0]))
        assert r.decision is Decision.DENY, cid


# --- 10. agent memory cannot be canonical truth ----------------------------------------
def test_10_agent_memory_is_not_canonical_truth():
    # No ENABLED canonical-mutation capability is reachable by a conversational
    # actor without a human approval gate.
    for cap in _caps_raw().values():
        if cap["side_effect_class"] == "CANONICAL_MUTATION" and \
                cap["phase_status"] == "ENABLED":
            for at in cap["allowed_actor_types"]:
                assert "HERMES" not in at or cap["approval_policy"] in ("AP2", "AP3")


# --- 11. secrets cannot live in conversational memory ------------------------------------
def test_11_secrets_not_in_conversational_memory():
    for actor in _actors_raw().values():
        if actor["actor_type"].startswith("ACTOR-HERMES") or \
                actor["actor_type"] == "ACTOR-WORKER":
            assert not actor["may_hold_credentials"], actor["actor_type"]


# --- 12. self-improvement cannot self-ratify ----------------------------------------------
def test_12_self_improvement_cannot_self_ratify_authority():
    gov = yaml.safe_load((POLICY / "self_improvement.yaml").read_text(encoding="utf-8"))
    ceo = gov["actor_permissions"]["ACTOR-HERMES-CEO"]
    assert "promote_own_authority_increase" in ceo["may_not"]
    assert "promote_change" not in [m.lower() for m in ceo["may"]]
    assert any("OTHER than any agent" in r for r in gov["hard_rules"])


# --- 13. audit requirements for consequential actions --------------------------------------
def test_13_audit_requirements_exist_for_consequential_actions():
    caps = _caps_raw()
    for cid, cap in caps.items():
        if cap["side_effect_class"] in ("CANONICAL_MUTATION", "EXTERNAL_ACTION",
                                        "LEGALLY_MATERIAL"):
            assert cap["audit_class"] in ("A2", "A3", "A4"), cid
    valid = {"A0", "A1", "A2", "A3", "A4"}   # A0 telemetry-only (B1.C9)
    assert all(cap["audit_class"] in valid for cap in caps.values())


# --- 14. failure behavior specified for all capability families -----------------------------
def test_14_failure_behavior_specified_for_all_families():
    fm = yaml.safe_load((POLICY / "failure_matrix.yaml").read_text(encoding="utf-8"))
    valid = {f["class_id"] for f in fm["failure_classes"]}
    for cap in _caps_raw().values():
        assert cap["failure_mode"] in valid, cap["capability_id"]
    families = {cap["family"] for cap in _caps_raw().values()}
    used = {cap["failure_mode"] for cap in _caps_raw().values()}
    assert len(families) >= 12  # all plan families present
    assert "F-AUTH" in used and "F-EVIDENCE" in used


# --- 15. constitutional changes require amendment/ADR ----------------------------------------
def test_15_constitutional_changes_require_amendment():
    laws = yaml.safe_load((POLICY / "constitutional_laws.yaml").read_text(encoding="utf-8"))
    assert all(law["amendment_status"] in ("FROZEN", "AMENDABLE_BY_MINOR",
                                           "AMENDABLE_BY_MAJOR") for law in laws["laws"])
    ok, report = validate_constitution(laws)
    assert ok, report["errors"]
    assert report["law_count"] == 30
    # amendment protocol referenced in constitution docs
    protocol = (_ROOT / "docs/grant-sector/g0/01-constitution"
                / "G0_B1_PRODUCT_CONSTITUTION_v1.0.md").read_text(encoding="utf-8")
    assert "AMENDMENT" in protocol.upper()


# --- coverage targets -----------------------------------------------------------------------
def test_coverage_100_percent_policy_metadata():
    ok, report = validate_package(load_package())
    assert ok, report["errors"]
    assert report["capability_count"] >= 55
    assert report["enabled_capability_count"] + report["disabled_capability_count"] \
        == report["capability_count"]


def test_coverage_zero_submission_paths_enabled():
    for cap in _caps_raw().values():
        if cap["family"] == "submission" or cap["capability_id"] == "application.submit":
            assert cap["phase_status"] == "DISABLED"
            assert cap["approval_policy"] == "APX"


def test_coverage_no_unresolved_p0_in_ledger():
    ledger = yaml.safe_load(
        (_ROOT / "config/g0/ratification/contradiction_ledger.yaml").read_text(encoding="utf-8"))
    p0_open = [c for c in ledger["contradictions"]
               if c["severity"] == "P0" and c["status"] != "RESOLVED"]
    assert p0_open == []
