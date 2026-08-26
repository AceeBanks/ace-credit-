"""G0-B1-REPAIR-02 — approval integrity adversarial tests.

Proves the executable approval contract (models.ApprovalRef +
evaluator._find_valid_approval) aligns with approval_policy.schema.json and
fails closed on every class-substitution, scope, and time attack:

  - AP1 can never satisfy AP2/AP3 (no implicit privilege inheritance)
  - AP2 can never satisfy AP3 unless the constitution explicitly says so
  - approvals are capability-, tenant-, and project-exact
  - expired timestamps fail even when status is still VALID
  - revoked approvals never satisfy
  - AP3 needs two DISTINCT human principals
  - agent principals are rejected at the contract boundary
"""
from __future__ import annotations

import json
from pathlib import Path

import jsonschema
import pytest

from prototype.g0.policy.evaluator import evaluate
from prototype.g0.policy.models import (
    Actor,
    ApprovalRef,
    AuthorityLevel,
    Decision,
    PolicyContext,
    Reason,
)
from prototype.g0.policy.registry import PolicyRegistry

_ROOT = Path(__file__).resolve().parents[3]
SCHEMA = json.loads(
    (_ROOT / "schemas/g0/policy/approval_policy.schema.json").read_text(encoding="utf-8")
)

_PAST = "2026-08-01T00:00:00Z"      # decided in the past — valid
_PAST_EXPIRY = "2026-01-01T00:00:00Z"  # already expired at eval time
_FUTURE = "2099-01-01T00:00:00Z"    # still valid at eval time
_FUTURE_DECIDED = "2099-06-01T00:00:00Z"  # decided in the future — untrustworthy

SCHEMA_VALID_RECORD = {
    "approval_id": "ap-1",
    "approver_principal": "human-owner",
    "approver_role": "HUMAN_CLIENT_APPROVER",
    "approval_class": "AP2",
    "scope_tenant_id": "tenant-alpha",
    "scope_project_id": "proj-1",
    "subject_capability_id": "evidence.propose_promotion",
    "decided_at": _PAST,
    "expires_at": None,
    "status": "VALID",
}


@pytest.fixture(scope="module")
def reg() -> PolicyRegistry:
    return PolicyRegistry.load()


def ceo() -> Actor:
    return Actor("ceo-1", "ACTOR-HERMES-CEO", ("tenant-alpha",), AuthorityLevel.L2)


def admin() -> Actor:
    return Actor("admin-1", "ACTOR-HUMAN-ADMIN", (), AuthorityLevel.L5)


def ap2_ctx(*refs: ApprovalRef) -> PolicyContext:
    return PolicyContext(tenant_id="tenant-alpha", project_id="proj-1",
                         resource_type="evidence_record", approval_refs=tuple(refs))


def ap3_ctx(*refs: ApprovalRef) -> PolicyContext:
    return PolicyContext(tenant_id="tenant-alpha", project_id=None,
                         resource_type="system_state", approval_refs=tuple(refs))


def ap2(cap="evidence.propose_promotion", **kw) -> ApprovalRef:
    base = dict(approval_id="ap-1", approver_principal="human-owner",
                approver_role="HUMAN_CLIENT_APPROVER", approval_class="AP2",
                scope_tenant_id="tenant-alpha", subject_capability_id=cap,
                decided_at=_PAST)
    base.update(kw)
    return ApprovalRef(**base)


# --- class substitution ------------------------------------------------------

def test_ap1_cannot_satisfy_ap2(reg):
    ref = ap2(approval_class="AP1")          # an AP1 review-after record
    r = evaluate(reg, ceo(), "evidence.propose_promotion", ap2_ctx(ref))
    assert (r.decision, r.reason_code) == (Decision.REQUIRE_APPROVAL, Reason.APPROVAL_REQUIRED)


def test_ap1_cannot_satisfy_ap3(reg):
    ref = ApprovalRef("a1", "human-owner", "HUMAN_CLIENT_APPROVER", "AP1",
                      "tenant-alpha", "system.promote_change", decided_at=_PAST)
    r = evaluate(reg, admin(), "system.promote_change", ap3_ctx(ref))
    assert (r.decision, r.reason_code) == (Decision.REQUIRE_APPROVAL, Reason.APPROVAL_REQUIRED)


def test_ap2_cannot_satisfy_ap3_without_explicit_rule(reg):
    # Two DISTINCT AP2 principals — still not AP3: class matching is exact.
    refs = (ApprovalRef("a", "owner-1", "HUMAN_CLIENT_APPROVER", "AP2",
                        "tenant-alpha", "system.promote_change", decided_at=_PAST),
            ApprovalRef("b", "admin-2", "HUMAN_ADMIN_APPROVER", "AP2",
                        "tenant-alpha", "system.promote_change", decided_at=_PAST))
    r = evaluate(reg, admin(), "system.promote_change", ap3_ctx(*refs))
    assert (r.decision, r.reason_code) == (Decision.REQUIRE_APPROVAL, Reason.APPROVAL_REQUIRED)


def test_ap3_with_two_distinct_humans_allows(reg):
    refs = (ApprovalRef("a", "owner-1", "DUAL_OWNER_PLUS_ADMIN", "AP3",
                        "tenant-alpha", "system.promote_change", decided_at=_PAST),
            ApprovalRef("c", "admin-2", "HUMAN_ADMIN_APPROVER", "AP3",
                        "tenant-alpha", "system.promote_change", decided_at=_PAST))
    r = evaluate(reg, admin(), "system.promote_change", ap3_ctx(*refs))
    assert r.decision is Decision.ALLOW


# --- scope exactness ----------------------------------------------------------

def test_wrong_project_approval_rejected(reg):
    ref = ap2(scope_project_id="proj-9")     # approved for a different project
    r = evaluate(reg, ceo(), "evidence.propose_promotion", ap2_ctx(ref))
    assert (r.decision, r.reason_code) == (Decision.REQUIRE_APPROVAL, Reason.APPROVAL_REQUIRED)


def test_project_scoped_approval_cannot_authorize_other_project(reg):
    ref = ap2(scope_project_id="proj-1")
    other = PolicyContext(tenant_id="tenant-alpha", project_id="proj-2",
                          resource_type="evidence_record", approval_refs=(ref,))
    r = evaluate(reg, ceo(), "evidence.propose_promotion", other)
    assert (r.decision, r.reason_code) == (Decision.REQUIRE_APPROVAL, Reason.APPROVAL_REQUIRED)


def test_wrong_capability_approval_rejected(reg):
    # AP2 approval for evidence.resolve_conflict cannot satisfy propose_promotion
    ref = ap2(cap="evidence.resolve_conflict")
    r = evaluate(reg, ceo(), "evidence.propose_promotion", ap2_ctx(ref))
    assert (r.decision, r.reason_code) == (Decision.REQUIRE_APPROVAL, Reason.APPROVAL_REQUIRED)


# --- time integrity -----------------------------------------------------------

def test_expired_timestamp_with_status_valid_rejected(reg):
    ref = ap2(expires_at=_PAST_EXPIRY, status="VALID")   # stale timestamp, VALID status
    r = evaluate(reg, ceo(), "evidence.propose_promotion", ap2_ctx(ref))
    assert (r.decision, r.reason_code) == (Decision.REQUIRE_APPROVAL, Reason.APPROVAL_REQUIRED)


def test_valid_timestamp_with_future_expiry_allows(reg):
    ref = ap2(expires_at=_FUTURE)
    r = evaluate(reg, ceo(), "evidence.propose_promotion", ap2_ctx(ref))
    assert r.decision is Decision.ALLOW


def test_future_decided_at_rejected(reg):
    ref = ap2(decided_at=_FUTURE_DECIDED)    # decided in the future — untrustworthy
    r = evaluate(reg, ceo(), "evidence.propose_promotion", ap2_ctx(ref))
    assert (r.decision, r.reason_code) == (Decision.REQUIRE_APPROVAL, Reason.APPROVAL_REQUIRED)


def test_revoked_approval_rejected(reg):
    ref = ap2(status="REVOKED")
    r = evaluate(reg, ceo(), "evidence.propose_promotion", ap2_ctx(ref))
    assert (r.decision, r.reason_code) == (Decision.REQUIRE_APPROVAL, Reason.APPROVAL_REQUIRED)


# --- AP3 principal distinctness ------------------------------------------------

def test_duplicate_principal_cannot_satisfy_ap3(reg):
    refs = (ApprovalRef("a", "owner-1", "DUAL_OWNER_PLUS_ADMIN", "AP3",
                        "tenant-alpha", "system.promote_change", decided_at=_PAST),
            ApprovalRef("b", "owner-1", "HUMAN_ADMIN_APPROVER", "AP3",
                        "tenant-alpha", "system.promote_change", decided_at=_PAST))
    r = evaluate(reg, admin(), "system.promote_change", ap3_ctx(*refs))
    assert (r.decision, r.reason_code) == (Decision.REQUIRE_APPROVAL, Reason.APPROVAL_REQUIRED)


# --- contract boundary ---------------------------------------------------------

def test_agent_principal_rejected_at_contract(reg):
    with pytest.raises(ValueError):
        ap2(approver_principal="agent-ceo-self")


# --- schema contract -----------------------------------------------------------

def test_schema_rejects_missing_subject_capability():
    rec = {**SCHEMA_VALID_RECORD}
    del rec["subject_capability_id"]
    with pytest.raises(jsonschema.ValidationError):
        jsonschema.validate(rec, SCHEMA)


def test_schema_accepts_full_valid_record():
    jsonschema.validate(SCHEMA_VALID_RECORD, SCHEMA)   # no raise


def test_schema_declares_datetime_format():
    # The schema keeps date-time validation on both timestamps (declarative);
    # behavioral enforcement is the evaluator's _parse_dt, proven by the time
    # integrity tests above (rfc3339_validator is not installed, so a
    # FormatChecker-based raise test is not available).
    assert SCHEMA["properties"]["decided_at"]["format"] == "date-time"
    assert SCHEMA["properties"]["expires_at"]["format"] == "date-time"
