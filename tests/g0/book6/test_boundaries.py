"""G0-B6-C12-C15 — Integration, egress, data classification & PII tests.

Required coverage (plan):
- workflow platform outage does not erase accepted task state;
- connector cannot mutate unrelated resource;
- automation created outside platform does not gain canonical authority;
- connector result validated before state promotion;
- SSRF to cloud metadata blocked;
- redirect to attacker host blocked;
- unknown host blocked;
- sensitive tenant file upload to unapproved destination blocked;
- proposal containing client private financials classified appropriately;
- public source + private annotations results in tenant-private derived object;
- secret can never downgrade to INTERNAL by summarization;
- unrelated worker does not receive founder PII;
- sensitive values redacted from sidechain preview;
- public explanation packet omits restricted fields;
- tenant-private data cannot enter global eval without governance.
"""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

_ROOT = Path(__file__).resolve().parents[3]
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from prototype.g0.security.boundaries import (  # noqa: E402
    BoundaryError,
    ClassificationEngine,
    EgressController,
    IntegrationExecutor,
    PIIFilter,
)


def test_platform_outage_does_not_erase_task_state():
    ex = IntegrationExecutor()
    ex.execute(action="write_file_to_approved_storage",
               target_resource="storage:approved-1",
               connector_result={"resource_id": "storage:approved-1",
                                 "validated": True})
    # platform outage: canonical state lives in the governed store
    assert ex.outage_does_not_erase_state("storage:approved-1") is True


def test_connector_cannot_mutate_unrelated_resource():
    ex = IntegrationExecutor()
    with pytest.raises(BoundaryError):
        ex.execute(action="write_file_to_approved_storage",
                   target_resource="storage:approved-1",
                   connector_result={"resource_id": "storage:other-file",
                                     "validated": True})


def test_outside_automation_gains_no_canonical_authority():
    ex = IntegrationExecutor()
    with pytest.raises(BoundaryError):
        ex.execute(action="own_canonical_application_project_state",
                   target_resource="canonical:project-1",
                   connector_result={"resource_id": "canonical:project-1",
                                     "validated": True})


def test_connector_result_validated_before_promotion():
    ex = IntegrationExecutor()
    with pytest.raises(BoundaryError):
        ex.execute(action="sync_approved_crm_fields",
                   target_resource="crm:contact-1",
                   connector_result={"resource_id": "crm:contact-1",
                                     "validated": False})


def test_ssrf_to_cloud_metadata_blocked():
    egress = EgressController()
    with pytest.raises(BoundaryError):
        egress.check(host="169.254.169.254", egress_class="REGISTERED_SOURCE_READ")
    with pytest.raises(BoundaryError):
        egress.check(host="localhost", egress_class="REGISTERED_SOURCE_READ")
    with pytest.raises(BoundaryError):
        egress.check(host="file://etc/passwd", egress_class="REGISTERED_SOURCE_READ")
    with pytest.raises(BoundaryError):
        egress.check(host="10.0.0.5", egress_class="REGISTERED_SOURCE_READ")


def test_redirect_to_attacker_host_blocked():
    egress = EgressController()
    egress.allow("trusted.example", "APPROVED_API")
    with pytest.raises(BoundaryError):
        egress.revalidate_redirect(original_host="trusted.example",
                                   redirect_host="attacker.example",
                                   egress_class="APPROVED_API")
    assert egress.revalidate_redirect(original_host="trusted.example",
                                      redirect_host="trusted.example",
                                      egress_class="APPROVED_API") == \
        "trusted.example"


def test_unknown_host_blocked():
    egress = EgressController()
    egress.allow("api.example", "APPROVED_API")
    with pytest.raises(BoundaryError):
        egress.check(host="unknown.example", egress_class="APPROVED_API")
    assert egress.check(host="api.example", egress_class="APPROVED_API") is True


def test_sensitive_upload_to_unapproved_destination_blocked():
    egress = EgressController()
    egress.allow("storage.example", "APPROVED_INTEGRATION")
    with pytest.raises(BoundaryError):
        egress.check(host="storage.example", egress_class="APPROVED_INTEGRATION",
                     data_class="FINANCIAL_SENSITIVE")


def test_submission_egress_disabled_phase1():
    egress = EgressController()
    egress.allow("portal.example", "SUBMISSION_PORTAL")
    with pytest.raises(BoundaryError):
        egress.check(host="portal.example", egress_class="SUBMISSION_PORTAL")


def test_proposal_with_client_financials_classified_appropriately():
    cls = ClassificationEngine()
    derived = cls.derive("PUBLIC", "FINANCIAL_SENSITIVE")
    assert derived == "FINANCIAL_SENSITIVE"


def test_public_source_plus_private_annotations_tenant_private():
    cls = ClassificationEngine()
    derived = cls.derive("PUBLIC", "TENANT_CONFIDENTIAL")
    assert derived == "TENANT_CONFIDENTIAL"


def test_secret_never_downgrades_by_summarization():
    cls = ClassificationEngine()
    with pytest.raises(BoundaryError):
        cls.summarize("CREDENTIAL_SECRET", "INTERNAL")
    assert cls.summarize("INTERNAL", "INTERNAL") == "INTERNAL"
    assert cls.summarize("PII", "PII") == "PII"


def test_unrelated_worker_does_not_receive_founder_pii():
    filt = PIIFilter()
    fields = {"org_name": "ACME", "founder_email": "jane@acme.com",
              "tax_id": "123456789", "mission": "youth workforce"}
    context = filt.context_for_worker(worker_task="draft.requirements",
                                      all_fields=fields,
                                      allowed_fields=[
                                          "org_name", "mission", "founder_email"])
    assert "founder_email" not in context  # PII excluded for unrelated task
    assert context["org_name"] == "ACME"


def test_sensitive_values_redacted_from_sidechain_preview():
    filt = PIIFilter()
    preview = "founder jane@acme.com, ssn 123-45-6789, tax 123456789"
    redacted = filt.redact_preview(preview)
    assert "jane@acme.com" not in redacted
    assert "123-45-6789" not in redacted


def test_public_explanation_omits_restricted_fields():
    filt = PIIFilter()
    fields = {"summary": "eligible", "bank_account": "111122223333",
              "founder_email": "jane@acme.com", "match": "strong"}
    public = filt.public_explanation_fields(fields)
    assert "bank_account" not in public
    assert "founder_email" not in public
    assert public["summary"] == "eligible"


def test_tenant_private_data_gated_from_global_eval():
    filt = PIIFilter()
    assert filt.eval_gate(data_class="PII") is False
    assert filt.eval_gate(data_class="PII",
                          governance_approval="gov:consent-1") is True
    assert filt.eval_gate(data_class="PUBLIC") is True
