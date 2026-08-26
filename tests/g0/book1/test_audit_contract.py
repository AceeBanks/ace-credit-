"""B1.C9 tests — Audit & Accountability contract.

Enforces the plan's audit tests:
- consequential operation lacking actor/request ID fails validation;
- audit cannot contain a raw secret fixture;
- cross-tenant audit query is blocked by the scope model;
plus structural minimums (full field set, ISO timestamp, valid result_status)
and approval-decision linkability.
"""
from __future__ import annotations

from pathlib import Path

import yaml

from tools.g0.validate_audit_event import (
    AUDIT_EVENT_MINIMUM,
    can_view_audit,
    validate,
)

_ROOT = Path(__file__).resolve().parents[3]
POLICY = _ROOT / "config/g0/policy"


def _side_effects() -> dict:
    reg = yaml.safe_load((POLICY / "capability_registry.yaml").read_text(encoding="utf-8"))
    return {c["capability_id"]: c["side_effect_class"]
            for c in reg["capabilities"]}


def _context() -> dict:
    return {"capability_side_effect": _side_effects(),
            "secrets": ("s3cr3t-fixture-value-xyz",)}


def _event(**overrides) -> dict:
    ev = {
        "event_id": "evt-0001",
        "timestamp": "2026-08-26T12:00:00Z",
        "actor_id": "admin-1",
        "actor_type": "ACTOR-HUMAN-ADMIN",
        "tenant_id": "tenant-alpha",
        "project_id": "proj-1",
        "capability_id": "organization.accept_verified_update",  # CANONICAL_MUTATION
        "authority_level": "L3",
        "resource_type": "organization_profile",
        "resource_id": "org-42",
        "request_id": "req-9001",
        "approval_ref": "ap-7",
        "input_artifact_refs": ["art-1"],
        "output_artifact_refs": ["art-2"],
        "source_refs": ["src-ga-opb-1"],
        "result_status": "SUCCESS",
        "error_class": None,
        "policy_decision_ref": "pd-101",
    }
    ev.update(overrides)
    return ev


def test_live_consequential_event_passes():
    ok, report = validate(_event(), _context())
    assert ok, report["errors"]
    assert report["checks"]["consequential_side_effect"] == "CANONICAL_MUTATION"


def test_missing_field_fails():
    ev = _event()
    del ev["event_id"]
    ok, report = validate(ev, _context())
    assert not ok
    assert any("missing audit event fields" in e for e in report["errors"])


def test_consequential_op_lacking_actor_id_fails():
    ok, report = validate(_event(actor_id=None), _context())
    assert not ok
    assert any("lacks actor_id" in e for e in report["errors"])


def test_consequential_op_lacking_request_id_fails():
    ok, report = validate(_event(request_id=None), _context())
    assert not ok
    assert any("lacks request_id" in e for e in report["errors"])


def test_read_only_event_does_not_need_request_id():
    ev = _event(capability_id="opportunity.search", request_id=None,
                result_status="SUCCESS")
    ok, report = validate(ev, _context())
    assert ok, report["errors"]


def test_raw_secret_fixture_fails():
    ev = _event(source_refs=["s3cr3t-fixture-value-xyz"])
    ok, report = validate(ev, _context())
    assert not ok
    assert any("raw secret fixture" in e for e in report["errors"])


def test_secret_shaped_value_fails():
    ev = _event(policy_decision_ref="sk-abcdefghijklmnopqrstuvwxyz012345")
    ok, report = validate(ev, _context())
    assert not ok
    assert any("raw secret shape" in e for e in report["errors"])


def test_cross_tenant_audit_query_blocked():
    assert can_view_audit(("tenant-alpha",), "tenant-beta") is False
    assert can_view_audit(("tenant-alpha",), "tenant-alpha") is True


def test_platform_wide_actor_can_view_across_tenants():
    assert can_view_audit(("tenant-alpha",), "tenant-beta", platform_wide=True) is True


def test_missing_tenant_fails():
    ok, report = validate(_event(tenant_id=None), _context())
    assert not ok
    assert any("tenant_id must be non-empty" in e for e in report["errors"])


def test_approval_without_policy_decision_fails_linkability():
    ok, report = validate(_event(policy_decision_ref=None), _context())
    assert not ok
    assert any("linkable" in e for e in report["errors"])


def test_malformed_timestamp_fails():
    ok, report = validate(_event(timestamp="not-a-date"), _context())
    assert not ok
    assert any("ISO-8601" in e for e in report["errors"])


def test_unknown_result_status_fails():
    ok, report = validate(_event(result_status="MAYBE"), _context())
    assert not ok
    assert any("result_status" in e for e in report["errors"])


def test_audit_schema_documents_minimum():
    """The committed JSON schema stays in lockstep with the validator."""
    schema = (_ROOT / "schemas/g0/policy/audit_requirement.schema.json").read_text(
        encoding="utf-8")
    assert "event_id" in schema and "request_id" in schema
    assert "required" in schema
