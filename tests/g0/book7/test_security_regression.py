"""B7.C15 — Security & authority regression tests.

Includes a live re-run of the Book 6 REPAIR-01 seam probes (grant authority
ladder, capability binding, tenant/project/resource binding, approval
registry, replay protection) plus the 12 hard gates.
"""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

_ROOT = Path(__file__).resolve().parents[3]
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from prototype.g0.evaluation.security_regression import (  # noqa: E402
    gate_audit_provenance_write_required,
    gate_cross_tenant_retrieval_absent,
    gate_egress_policy_enforced,
    gate_expired_approval_denied,
    gate_personal_to_ceo_escalation_denied,
    gate_prompt_injection_no_authority,
    gate_secret_exposure_absent,
    gate_submission_remains_disabled,
    gate_unknown_capability_denied,
    gate_worker_scope_escalation_denied,
    gate_wrong_project_denied,
    gate_wrong_tenant_denied,
    run_book6_seam_probes,
    security_regression_report,
)


def test_book6_seam_probes_all_green():
    """The Book 6 repair seams must be live and passing."""
    probes = run_book6_seam_probes()
    assert probes, "no seam probes returned"
    assert all(probes.values()), {
        k: v for k, v in probes.items() if not v}


def test_unknown_capability_gate():
    assert gate_unknown_capability_denied(decision="DENY").passed
    assert not gate_unknown_capability_denied(decision="ALLOW").passed


def test_tenant_and_project_gates():
    assert gate_wrong_tenant_denied(allowed=False).passed
    assert not gate_wrong_tenant_denied(allowed=True).passed
    assert gate_wrong_project_denied(allowed=False).passed
    assert not gate_wrong_project_denied(allowed=True).passed


def test_escalation_gates():
    assert gate_personal_to_ceo_escalation_denied(escalated=False).passed
    assert not gate_personal_to_ceo_escalation_denied(escalated=True).passed
    assert gate_worker_scope_escalation_denied(escalated=False).passed
    assert not gate_worker_scope_escalation_denied(escalated=True).passed


def test_approval_and_secret_gates():
    assert gate_expired_approval_denied(allowed=False).passed
    assert not gate_expired_approval_denied(allowed=True).passed
    assert gate_secret_exposure_absent(secrets_found=[]).passed
    assert not gate_secret_exposure_absent(
        secrets_found=["sk-live-123"]).passed


def test_egress_and_injection_gates():
    assert gate_egress_policy_enforced(allowed=True).passed
    assert not gate_egress_policy_enforced(allowed=False).passed
    assert gate_prompt_injection_no_authority(authority_granted=False).passed
    assert not gate_prompt_injection_no_authority(authority_granted=True).passed


def test_submission_and_audit_gates():
    assert gate_submission_remains_disabled(submission_capable=False).passed
    assert not gate_submission_remains_disabled(submission_capable=True).passed
    assert gate_audit_provenance_write_required(audited=True).passed
    assert not gate_audit_provenance_write_required(audited=False).passed


def test_cross_tenant_retrieval_gate():
    assert gate_cross_tenant_retrieval_absent(leaked=False).passed
    assert not gate_cross_tenant_retrieval_absent(leaked=True).passed


def test_regression_report_all_green():
    gates = [
        gate_unknown_capability_denied(decision="DENY"),
        gate_wrong_tenant_denied(allowed=False),
        gate_wrong_project_denied(allowed=False),
        gate_personal_to_ceo_escalation_denied(escalated=False),
        gate_worker_scope_escalation_denied(escalated=False),
        gate_expired_approval_denied(allowed=False),
        gate_secret_exposure_absent(secrets_found=[]),
        gate_egress_policy_enforced(allowed=True),
        gate_prompt_injection_no_authority(authority_granted=False),
        gate_submission_remains_disabled(submission_capable=False),
        gate_audit_provenance_write_required(audited=True),
        gate_cross_tenant_retrieval_absent(leaked=False),
    ]
    report = security_regression_report(gate_results=gates)
    assert report["all_pass"] is True
    assert report["seam_failures"] == []


def test_regression_report_vetoes_on_gate_failure():
    gates = [
        gate_unknown_capability_denied(decision="DENY"),
        gate_submission_remains_disabled(submission_capable=True),
    ]
    report = security_regression_report(gate_results=gates)
    assert report["all_pass"] is False
    assert report["failed"] == 1


def test_regression_report_vetoes_on_seam_failure():
    gates = [gate_unknown_capability_denied(decision="DENY")]
    report = security_regression_report(
        gate_results=gates,
        seam_results={"grant_authority_enforced": True,
                      "authorization_capability_binding": False})
    assert report["all_pass"] is False
    assert "authorization_capability_binding" in report["seam_failures"]
