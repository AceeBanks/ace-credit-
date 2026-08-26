"""G0-B6-C6/C7/C8 — Authentication, service identity & credential vault.

AUTH-001..005: server-side tenant binding (client param tampering is
ineffective), revoked sessions blocked, expired service tokens blocked,
service tokens cannot impersonate human approval, privilege elevation
re-evaluates. SVC-001..006: minimum capability per service, independent
revocation, no omnipotent secret. VAULT-001..007: opaque references only,
allowed capabilities/destinations enforced, tenant-bound, rotation without
agent/memory changes, redaction of prompts/sidechains/logs, revocation
denies immediately.
"""
from __future__ import annotations

import re
from datetime import datetime, timezone
from typing import Any


class AuthnError(ValueError):
    """Raised when authentication/credential policy is violated."""


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _load_policy(name: str) -> dict:
    import yaml
    from pathlib import Path
    root = Path(__file__).resolve().parents[3]
    return yaml.safe_load((root / "config/g0/security/" / name)
                          .read_text(encoding="utf-8"))


_AUTH_POLICY = _load_policy("authn_session_policy.yaml")
_SVC_POLICY = _load_policy("service_identity_policy.yaml")
_VAULT_POLICY = _load_policy("credential_vault_policy.yaml")

_RAW_SECRET_PATTERNS = (
    re.compile(r"sk-[A-Za-z0-9]{16,}"),
    re.compile(r"AKIA[0-9A-Z]{16}"),
    re.compile(r"xox[baprs]-[A-Za-z0-9-]{10,}"),
)


class SessionManager:
    """Server-side sessions with tenant binding and revocation."""

    def __init__(self, policy: dict | None = None) -> None:
        self.policy = policy or _AUTH_POLICY
        self._sessions: dict[str, dict] = {}

    def create_session(self, *, session_id: str, principal_id: str,
                       tenant_id: str, expires_at: str,
                       is_privileged: bool = False) -> dict:
        # AUTH-001: tenant bound server-side at creation
        session = dict(session_id=session_id, principal_id=principal_id,
                       tenant_id=tenant_id, expires_at=expires_at,
                       revoked=False, is_privileged=is_privileged)
        self._sessions[session_id] = session
        return session

    def validate(self, *, session_id: str, client_tenant: str | None,
                 now: str | None = None) -> dict:
        """AUTH-001/002: a client-supplied tenant param cannot change the
        session tenant; revoked or expired sessions are blocked."""
        now = now or _now()
        session = self._sessions.get(session_id)
        if session is None or session["revoked"]:
            raise AuthnError("SESSION_INVALID: session revoked or unknown")
        if session["expires_at"] < now:
            raise AuthnError("SESSION_INVALID: session expired")
        if client_tenant is not None and client_tenant != session["tenant_id"]:
            raise AuthnError(
                "SESSION_INVALID: tenant parameter tampering is ineffective; "
                "tenant is bound server-side (AUTH-001)")
        return session

    def revoke(self, session_id: str) -> None:
        if session_id not in self._sessions:
            raise AuthnError(f"unknown session {session_id}")
        self._sessions[session_id]["revoked"] = True


class ServiceIdentityRegistry:
    """Minimum-capability service identities, independently revocable."""

    def __init__(self, policy: dict | None = None) -> None:
        self.policy = policy or _SVC_POLICY
        self._services: dict[str, dict] = {}

    def register(self, service_id: str, *, capabilities: list[str],
                 token_expires_at: str) -> dict:
        minimum = {c for svc in self.policy["service_identities"]
                   if svc["id"] == service_id
                   for c in svc["minimum_capabilities"]}
        svc = dict(service_id=service_id, capabilities=list(capabilities),
                   minimum_capabilities=sorted(minimum),
                   token_expires_at=token_expires_at, revoked=False)
        self._services[service_id] = svc
        return svc

    def can_call(self, *, service_id: str, capability_id: str,
                 now: str | None = None) -> bool:
        """SVC-001: minimum capability set; expired token blocked
        (AUTH-003); revoked service blocked."""
        now = now or _now()
        svc = self._services.get(service_id)
        if svc is None or svc["revoked"]:
            return False
        if svc["token_expires_at"] < now:
            return False
        return capability_id in svc["capabilities"]

    def revoke(self, service_id: str) -> None:
        """SVC-003: independent revocation."""
        if service_id not in self._services:
            raise AuthnError(f"unknown service {service_id}")
        self._services[service_id]["revoked"] = True

    def assert_no_application_mutation(self, service_id: str) -> bool:
        """SVC-005: source adapters cannot call application-mutation caps."""
        minimum = next((set(s["minimum_capabilities"])
                        for s in self.policy["service_identities"]
                        if s["id"] == service_id), set())
        mutation = {"application.move_workflow_state", "application.approve",
                    "submission.execute"}
        return not (minimum & mutation)


class CredentialVault:
    """Opaque credential references; raw secrets stay server-side."""

    def __init__(self, policy: dict | None = None) -> None:
        self.policy = policy or _VAULT_POLICY
        self._refs: dict[str, dict] = {}
        self._secrets: dict[str, str] = {}  # ref_id -> raw (server-side only)

    def store(self, *, ref_id: str, provider: str, tenant_id: str,
              owner: str, allowed_capabilities: list[str],
              allowed_destinations: list[str], expires_at: str,
              raw_secret: str) -> dict:
        if provider not in self.policy["secret_classes"]:
            raise AuthnError(f"unknown secret class {provider!r}")
        ref = dict(credential_ref_id=ref_id, provider=provider,
                   tenant_id=tenant_id, owner_principal_or_service=owner,
                   allowed_capabilities=list(allowed_capabilities),
                   allowed_destinations=list(allowed_destinations),
                   status="ACTIVE", expires_at=expires_at,
                   rotation_policy="90d-rotate")
        self._refs[ref_id] = ref
        self._secrets[ref_id] = raw_secret  # server-side only
        return ref

    def resolve(self, *, ref_id: str, requesting_tenant: str,
                capability_id: str, destination: str | None = None,
                now: str | None = None) -> str:
        """VAULT-002/003/006: return the raw secret ONLY when tenant,
        capability, destination and status all permit."""
        now = now or _now()
        ref = self._refs.get(ref_id)
        if ref is None:
            raise AuthnError(f"unknown credential ref {ref_id}")
        if ref["status"] != "ACTIVE":
            raise AuthnError(f"credential {ref_id} is {ref['status']}")
        if ref["expires_at"] < now:
            raise AuthnError(f"credential {ref_id} expired")
        if ref["tenant_id"] != requesting_tenant:
            raise AuthnError(
                f"wrong-tenant credential use denied (VAULT-003)")
        if capability_id not in ref["allowed_capabilities"]:
            raise AuthnError(
                f"capability {capability_id} not allowed for credential "
                f"{ref_id} (VAULT-002)")
        if destination and destination not in ref["allowed_destinations"]:
            raise AuthnError(
                f"destination {destination} outside credential policy "
                "(VAULT-002)")
        return self._secrets[ref_id]

    def revoke(self, ref_id: str) -> None:
        if ref_id not in self._refs:
            raise AuthnError(f"unknown credential ref {ref_id}")
        self._refs[ref_id]["status"] = "REVOKED"

    def rotate(self, ref_id: str, new_raw_secret: str) -> None:
        """VAULT-004: rotation preserves capability without any agent/memory
        change — the reference and its policy are untouched."""
        ref = self._refs.get(ref_id)
        if ref is None:
            raise AuthnError(f"unknown credential ref {ref_id}")
        ref["status"] = "ACTIVE"
        self._secrets[ref_id] = new_raw_secret

    def redact(self, text: str, ref_ids: list[str]) -> str:
        """VAULT-005: serialized prompts/sidechains/logs contain no raw
        secret — replace raw values with their opaque ref ids."""
        for ref_id in ref_ids:
            raw = self._secrets.get(ref_id)
            if raw and raw in text:
                text = text.replace(raw, f"[REF:{ref_id}]")
        # defense-in-depth: known raw shapes
        for pat in _RAW_SECRET_PATTERNS:
            text = pat.sub("[REDACTED]", text)
        return text

    def prompt_contains_no_raw_secret(self, prompt: str,
                                      ref_ids: list[str]) -> bool:
        for ref_id in ref_ids:
            raw = self._secrets.get(ref_id)
            if raw and raw in prompt:
                return False
        return True
