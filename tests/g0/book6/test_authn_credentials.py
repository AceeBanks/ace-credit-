"""G0-B6-C6-C8 — Authentication, service identity & credential tests.

Required coverage (plan):
- revoked user session blocked;
- tenant parameter tampering ineffective;
- expired service token blocked;
- service token cannot impersonate human approval;
- source adapter cannot call application mutation capability;
- worker runtime cannot read arbitrary credential vault entries;
- revoked source service cannot fetch until restored;
- prompt serialization contains no raw secret;
- sidechain/log redaction;
- wrong-tenant credential reference denied;
- destination outside credential policy denied;
- rotation preserves capability without changing Hermes memory.
"""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

_ROOT = Path(__file__).resolve().parents[3]
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from prototype.g0.security.authn import (  # noqa: E402
    AuthnError,
    CredentialVault,
    ServiceIdentityRegistry,
    SessionManager,
)

T_FAR = "2027-12-31T00:00:00+00:00"
T0 = "2026-08-26T00:00:00+00:00"


def test_revoked_user_session_blocked():
    sm = SessionManager()
    sm.create_session(session_id="s1", principal_id="u1", tenant_id="tenant-a",
                      expires_at=T_FAR)
    assert sm.validate(session_id="s1", client_tenant="tenant-a")[
        "principal_id"] == "u1"
    sm.revoke("s1")
    with pytest.raises(AuthnError):
        sm.validate(session_id="s1", client_tenant="tenant-a")


def test_tenant_parameter_tampering_ineffective():
    sm = SessionManager()
    sm.create_session(session_id="s2", principal_id="u1", tenant_id="tenant-a",
                      expires_at=T_FAR)
    with pytest.raises(AuthnError):
        sm.validate(session_id="s2", client_tenant="tenant-b")


def test_expired_service_token_blocked():
    registry = ServiceIdentityRegistry()
    registry.register("svc-evidence", capabilities=["evidence.read"],
                      token_expires_at="2026-08-01T00:00:00+00:00")
    assert registry.can_call(service_id="svc-evidence",
                             capability_id="evidence.read",
                             now="2026-08-26T00:00:00+00:00") is False


def test_service_token_cannot_impersonate_human_approval():
    # service identities carry no human-approval capability by construction
    registry = ServiceIdentityRegistry()
    registry.register("svc-tool-gateway", capabilities=["tool.dispatch"],
                      token_expires_at=T_FAR)
    assert registry.can_call(service_id="svc-tool-gateway",
                             capability_id="application.approve") is False


def test_source_adapter_cannot_call_application_mutation():
    registry = ServiceIdentityRegistry()
    for svc in registry.policy["service_identities"]:
        if svc["id"].startswith("svc-source-"):
            assert registry.assert_no_application_mutation(svc["id"]) is True


def test_worker_runtime_cannot_read_arbitrary_vault_entries():
    vault = CredentialVault()
    vault.store(ref_id="cred:worker-scoped", provider="SERVICE_TOKEN",
                tenant_id="tenant-a", owner="svc-worker-runtime",
                allowed_capabilities=["worker.execute"],
                allowed_destinations=["https://worker.internal"],
                expires_at=T_FAR, raw_secret="worker-secret")
    vault.store(ref_id="cred:db", provider="DATABASE_CREDENTIAL",
                tenant_id="tenant-a", owner="svc-evidence",
                allowed_capabilities=["evidence.read"],
                allowed_destinations=["db.internal"], expires_at=T_FAR,
                raw_secret="db-secret")
    # worker can resolve its own scoped credential
    assert vault.resolve(ref_id="cred:worker-scoped",
                         requesting_tenant="tenant-a",
                         capability_id="worker.execute") == "worker-secret"
    # but not the database credential (capability not allowed)
    with pytest.raises(AuthnError):
        vault.resolve(ref_id="cred:db", requesting_tenant="tenant-a",
                      capability_id="worker.execute")


def test_revoked_source_service_cannot_fetch_until_restored():
    registry = ServiceIdentityRegistry()
    registry.register("svc-source-grants-gov",
                      capabilities=["evidence.ingest_snapshot", "source.read"],
                      token_expires_at=T_FAR)
    assert registry.can_call(service_id="svc-source-grants-gov",
                             capability_id="source.read") is True
    registry.revoke("svc-source-grants-gov")
    assert registry.can_call(service_id="svc-source-grants-gov",
                             capability_id="source.read") is False


def test_prompt_serialization_contains_no_raw_secret():
    vault = CredentialVault()
    vault.store(ref_id="cred:portal", provider="PORTAL_CREDENTIAL",
                tenant_id="tenant-a", owner="svc-source-georgia-opb",
                allowed_capabilities=["source.read"],
                allowed_destinations=["https://portal.example"],
                expires_at=T_FAR, raw_secret="super-secret-token-xyz")
    prompt = "fetch the portal using super-secret-token-xyz and save data"
    assert vault.prompt_contains_no_raw_secret(prompt, ["cred:portal"]) is False
    redacted = vault.redact(prompt, ["cred:portal"])
    assert "super-secret-token-xyz" not in redacted
    assert "[REF:cred:portal]" in redacted


def test_log_redaction_defense_in_depth():
    vault = CredentialVault()
    log = "request used sk-abc12345def67890ghi to reach api"
    redacted = vault.redact(log, [])
    assert "sk-abc12345def67890ghi" not in redacted
    assert "[REDACTED]" in redacted


def test_wrong_tenant_credential_reference_denied():
    vault = CredentialVault()
    vault.store(ref_id="cred:a", provider="API_KEY", tenant_id="tenant-a",
                owner="svc-evidence", allowed_capabilities=["evidence.read"],
                allowed_destinations=["https://api.example"], expires_at=T_FAR,
                raw_secret="secret-a")
    with pytest.raises(AuthnError):
        vault.resolve(ref_id="cred:a", requesting_tenant="tenant-b",
                      capability_id="evidence.read")


def test_destination_outside_credential_policy_denied():
    vault = CredentialVault()
    vault.store(ref_id="cred:d", provider="API_KEY", tenant_id="tenant-a",
                owner="svc-evidence", allowed_capabilities=["evidence.read"],
                allowed_destinations=["https://api.example"], expires_at=T_FAR,
                raw_secret="secret-d")
    with pytest.raises(AuthnError):
        vault.resolve(ref_id="cred:d", requesting_tenant="tenant-a",
                      capability_id="evidence.read",
                      destination="https://evil.example")


def test_rotation_preserves_capability_without_memory_change():
    vault = CredentialVault()
    vault.store(ref_id="cred:r", provider="OAUTH_ACCESS_TOKEN",
                tenant_id="tenant-a", owner="svc-source-grants-gov",
                allowed_capabilities=["source.read"],
                allowed_destinations=["https://grants.example"],
                expires_at=T_FAR, raw_secret="old-token")
    # rotation: same ref, new raw secret; no agent prompt/memory change
    vault.rotate("cred:r", "new-token")
    resolved = vault.resolve(ref_id="cred:r", requesting_tenant="tenant-a",
                             capability_id="source.read")
    assert resolved == "new-token"
    # the reference (what agents see) is unchanged
    ref = vault._refs["cred:r"]
    assert ref["credential_ref_id"] == "cred:r"
    assert ref["allowed_capabilities"] == ["source.read"]


def test_revoked_credential_cannot_fetch():
    vault = CredentialVault()
    vault.store(ref_id="cred:v", provider="SERVICE_TOKEN",
                tenant_id="tenant-a", owner="svc-evidence",
                allowed_capabilities=["evidence.read"],
                allowed_destinations=["https://api.example"], expires_at=T_FAR,
                raw_secret="secret-v")
    vault.revoke("cred:v")
    with pytest.raises(AuthnError):
        vault.resolve(ref_id="cred:v", requesting_tenant="tenant-a",
                      capability_id="evidence.read")
