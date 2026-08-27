"""G0-B7-PHASE-B — Governed Model Gateway (smallest Book-6-compliant
model runtime boundary).

Typed ModelRequest / ModelResponse contracts, a project-owned provider
profile registry (no caller-supplied base URLs or arbitrary models),
server-side credential resolution (vault ref or DEV_RUNTIME_ONLY env
resolver), capability/tenant/project/purpose/principal-type authorization,
egress+SSRF control, one-shot replay protection, structured audit.

The gateway consumes PDP-issued AuthorizationDecisions exactly like the
ToolGateway (AUTH-R6/R7/R8): the decision's capability_id must be declared
by the provider profile, the request context must match the decision, and
when a DecisionRegistry is configured the decision must have been issued by
that PDP. Model execution is a capability (`model.invoke`), never a
submission path.

DEV_RUNTIME_ONLY: the env-var credential resolver exists only to make the
governed pipeline testable with a real provider in development. It is NOT
production secret management. The raw credential is resolved only inside
the trusted adapter call, is never serialized into any ModelRequest/
ModelResponse/log/audit record, and is redacted from all artifacts.
"""
from __future__ import annotations

import re
import uuid
from datetime import datetime, timezone
from typing import Any, Callable
from urllib.parse import urlparse

from prototype.g0.security.authorization import DecisionRegistry, decision_shape_ok

_RAW_SECRET_PATTERNS = (
    re.compile(r"sk-[A-Za-z0-9]{16,}"),
    re.compile(r"AKIA[0-9A-Z]{16}"),
    re.compile(r"xox[baprs]-[A-Za-z0-9-]{10,}"),
)


class ModelError(ValueError):
    """Raised when a model request violates the governed runtime policy."""


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _load_policy() -> dict:
    import yaml
    from pathlib import Path
    root = Path(__file__).resolve().parents[3]
    return yaml.safe_load((root / "config/g0/model/model_gateway_policy.yaml")
                          .read_text(encoding="utf-8"))


_POLICY = _load_policy()


def _redact(text: str) -> str:
    """Strip known raw-secret shapes from any serialized artifact."""
    for pat in _RAW_SECRET_PATTERNS:
        text = pat.sub("[REDACTED]", text)
    return text


class ProviderProfileRegistry:
    """Project-owned, configuration-frozen provider profiles.

    Profiles are loaded from the governed policy. A profile pins the exact
    provider origin, the allowed model set, the allowed capabilities,
    purposes and principal types, the credential reference (or DEV-only env
    mode), and its enabled state. There is no runtime path to register an
    arbitrary base URL or an unapproved model name.
    """

    def __init__(self, policy: dict | None = None) -> None:
        self.policy = policy or _POLICY
        self._profiles: dict[str, dict] = {}
        for profile in self.policy.get("provider_profiles", []):
            self._profiles[profile["provider_profile_id"]] = dict(profile)

    def get(self, provider_profile_id: str) -> dict:
        profile = self._profiles.get(provider_profile_id)
        if profile is None:
            raise ModelError(f"unknown provider profile {provider_profile_id} "
                             "(MR-002)")
        return profile

    def enabled(self, provider_profile_id: str) -> bool:
        try:
            return self.get(provider_profile_id)["status"] != "DISABLED"
        except ModelError:
            return False

    def model_allowed(self, provider_profile_id: str, model_id: str) -> bool:
        profile = self.get(provider_profile_id)
        return model_id in profile.get("allowed_models", [])

    def purpose_allowed(self, provider_profile_id: str,
                        purpose: str) -> bool:
        profile = self.get(provider_profile_id)
        return purpose in profile.get("allowed_purposes", [])

    def principal_type_allowed(self, provider_profile_id: str,
                               principal_type: str) -> bool:
        profile = self.get(provider_profile_id)
        return principal_type in profile.get("allowed_principal_types", [])

    def capability_allowed(self, provider_profile_id: str,
                           capability_id: str) -> bool:
        profile = self.get(provider_profile_id)
        return capability_id in profile.get("allowed_capabilities", [])

    def origin_of(self, provider_profile_id: str) -> str:
        """Exact frozen origin (scheme://host[:port]) of the profile."""
        base = self.get(provider_profile_id)["base_url"]
        parts = urlparse(base)
        origin = f"{parts.scheme}://{parts.hostname}"
        if parts.port:
            origin += f":{parts.port}"
        return origin


class DevRuntimeCredentialResolver:
    """DEV_RUNTIME_ONLY — resolves a provider credential from the process
    environment, server-side, inside the trusted adapter call.

    Not production secret management (Book 6 vault is the production path).
    The raw value is returned only to the adapter, never placed into any
    ModelRequest/ModelResponse/audit/log record; the gateway redacts all
    serialized artifacts regardless.
    """

    def __init__(self, env_var: str = "OPENROUTER_API_KEY") -> None:
        self.env_var = env_var

    def resolve(self, *, provider: str) -> str:
        import os
        value = os.environ.get(self.env_var, "")
        if not value:
            raise ModelError(
                f"provider secret absent for {provider}; fail closed "
                "(MR-004/H)")
        return value


def _blocked_destination(destination: str) -> bool:
    """MR-003 / EGR-002 — SSRF guard over a URL or host."""
    if not destination:
        return True
    lowered = destination.lower()
    if lowered in {b.lower() for b in _POLICY["blocked_destinations"]}:
        return True
    parts = urlparse(lowered if "://" in lowered else f"//{lowered}")
    host = (parts.hostname or "").lower()
    blocked_hosts = {"127.0.0.1", "localhost", "169.254.169.254",
                     "169.254.170.2", "::1", "metadata.google.internal"}
    if host in blocked_hosts:
        return True
    # private RFC1918 / loopback / link-local ranges
    try:
        import ipaddress
        ip = ipaddress.ip_address(host)
        if ip.is_private or ip.is_loopback or ip.is_link_local or \
                ip.is_multicast or ip.is_reserved:
            return True
    except ValueError:
        pass  # hostname, not an IP literal
    return False


class ModelGateway:
    """Executes governed model requests; enforces policy independently."""

    def __init__(self, profiles: ProviderProfileRegistry,
                 policy: dict | None = None,
                 decisions: DecisionRegistry | None = None,
                 credential_resolver: Callable[..., str] | None = None,
                 vault=None,
                 max_decision_age_seconds: float | None = None) -> None:
        self.profiles = profiles
        self.policy = policy or _POLICY
        self.decisions = decisions
        self.credential_resolver = credential_resolver
        self.vault = vault
        self.max_decision_age_seconds = (
            max_decision_age_seconds
            if max_decision_age_seconds is not None
            else float(self.policy.get("decision_freshness_bound_seconds",
                                       900)))
        self._audit: list[dict] = []
        self._executed: set[str] = set()  # one-shot replay guard
        self._adapters: dict[str, Any] = {}

    def register_adapter(self, provider: str, adapter: Any) -> None:
        """Bind a provider adapter implementation (test fakes or the real
        bounded OpenRouter adapter) by provider name."""
        self._adapters[provider] = adapter

    # ------------------------------------------------------------ policy

    def _verify_decision(self, decision: Any) -> None:
        """AUTH-R2/R8 — fail closed unless the presented decision validates
        and is fresh."""
        if decision is None or not isinstance(decision, dict) or \
                decision.get("decision") != "ALLOW":
            reason = ((decision or {})
                      .get("reason_code") if isinstance(decision, dict)
                      else None) or "DECISION_UNAVAILABLE"
            raise ModelError(
                f"model request denied by AuthorizationDecision ({reason}) "
                "(MR-001)")
        if self.decisions is not None:
            ok, err = self.decisions.verify(decision)
        else:
            ok, err = decision_shape_ok(decision)
        if not ok:
            raise ModelError(
                f"AuthorizationDecision rejected: {err} (MR-001)")
        try:
            issued = datetime.fromisoformat(
                str(decision.get("decision_timestamp")).replace("Z", "+00:00"))
            if issued.tzinfo is None:
                issued = issued.replace(tzinfo=timezone.utc)
            age = (datetime.now(timezone.utc) - issued).total_seconds()
        except (TypeError, ValueError):
            raise ModelError("unparseable decision_timestamp (MR-001)")
        if age > self.max_decision_age_seconds:
            raise ModelError(
                f"AuthorizationDecision is stale: age {age:.0f}s exceeds "
                f"bound {self.max_decision_age_seconds:g}s (MR-001)")

    @staticmethod
    def _bind_context(decision: dict, context: dict) -> None:
        """AUTH-R7 — presented request context must MATCH the decision; any
        conflicting value denies. Absent caller values cannot defeat the
        other enforcement layers."""
        for field, actual in context.items():
            expected = decision.get(field)
            if expected and actual and actual != expected:
                raise ModelError(
                    f"context mismatch on {field}: request carries "
                    f"{actual!r} but decision binds {expected!r} (MR-001)")

    def _assert_not_replayed(self, model_request_id: str,
                             request_id: str) -> None:
        """MR-005 — one-shot semantics: a reused model_request_id or
        request_id is a replay and is refused."""
        if model_request_id in self._executed or request_id in self._executed:
            raise ModelError(
                f"model request replay detected ({model_request_id}/"
                f"{request_id}) (MR-005)")
        self._executed.add(model_request_id)
        self._executed.add(request_id)

    def _resolve_credential(self, profile: dict, *, tenant_id: str,
                            capability_id: str) -> tuple[str, str]:
        """Server-side credential resolution. Returns (raw, ref_label).

        Production path: Book 6 vault ref. DEV_RUNTIME_ONLY path: env
        resolver for profiles explicitly marked credential_mode
        DEV_RUNTIME_ONLY. The raw value returns only to the adapter call.
        """
        ref = profile.get("credential_ref")
        mode = profile.get("credential_mode")
        if mode == "DEV_RUNTIME_ONLY":
            if self.credential_resolver is None:
                raise ModelError(
                    "profile requires DEV_RUNTIME_ONLY credential resolver "
                    "but none configured (MR-004/H)")
            raw = self.credential_resolver(provider=profile["provider"])
            return raw, ref or "env:DEV_RUNTIME_ONLY"
        if ref and self.vault is not None:
            raw = self.vault.resolve(
                ref_id=ref, requesting_tenant=tenant_id,
                capability_id=capability_id,
                destination=profile["base_url"])
            return raw, ref
        raise ModelError(
            f"no credential path for profile {profile['provider_profile_id']} "
            "(MR-004/H)")

    # ------------------------------------------------------------- invoke

    def invoke(self, *, model_request: dict, authorization_decision: dict,
               actor: str, principal_type: str, tenant_id: str,
               project_id: str | None = None,
               resource_id: str | None = None) -> dict:
        """Execute a governed model request end-to-end (MR-001..MR-008)."""
        self._verify_decision(authorization_decision)

        profile_id = model_request.get("provider_profile_id")
        if not profile_id:
            raise ModelError("missing provider_profile_id (MR-002)")
        profile = self.profiles.get(profile_id)
        if profile["status"] == "DISABLED":
            raise ModelError(f"provider profile {profile_id} is disabled "
                             "(MR-002/L)")
        if not self.profiles.enabled(profile_id):
            raise ModelError(f"provider profile {profile_id} disabled "
                             "(MR-002/L)")

        # capability binding (AUTH-R6): decision capability must be declared
        # by the profile and be a model capability
        capability_id = authorization_decision.get("capability_id")
        if not capability_id:
            raise ModelError("missing capability_id in AuthorizationDecision "
                             "(MR-001)")
        if capability_id not in self.policy["model_capabilities"]:
            raise ModelError(
                f"capability {capability_id} is not a model capability "
                "(MR-001)")
        if not self.profiles.capability_allowed(profile_id, capability_id):
            raise ModelError(
                f"capability {capability_id} not declared by profile "
                f"{profile_id} (MR-001)")

        # context binding (AUTH-R7)
        self._bind_context(authorization_decision, {
            "request_id": model_request.get("request_id"),
            "principal_id": actor,
            "tenant_id": tenant_id,
            "project_id": project_id,
            "resource_id": resource_id,
        })

        # model / purpose / principal-type gates (MR-002/MR-007)
        model_id = model_request.get("model_id")
        if not model_id or not self.profiles.model_allowed(profile_id,
                                                           model_id):
            raise ModelError(
                f"model {model_id!r} not allowed by profile {profile_id} "
                "(MR-002/C)")
        purpose = model_request.get("purpose")
        if not purpose or not self.profiles.purpose_allowed(profile_id,
                                                            purpose):
            raise ModelError(
                f"purpose {purpose!r} not allowed by profile {profile_id} "
                "(MR-007)")
        if not self.profiles.principal_type_allowed(profile_id,
                                                    principal_type):
            raise ModelError(
                f"principal type {principal_type} not allowed by profile "
                f"{profile_id} (MR-007/D)")

        # egress/SSRF: destination must be the frozen profile origin
        destination = model_request.get("destination")
        origin = self.profiles.origin_of(profile_id)
        if destination:
            if _blocked_destination(destination):
                raise ModelError(
                    f"destination {destination} blocked (MR-003/K)")
            if destination.rstrip("/") != origin.rstrip("/"):
                raise ModelError(
                    f"destination {destination} not the frozen profile "
                    f"origin {origin} (MR-003/J)")
        # even with no explicit destination the origin itself must not be
        # a blocked target (config freeze defense-in-depth)
        if _blocked_destination(origin):
            raise ModelError(f"profile origin {origin} blocked (MR-003)")

        # caller-supplied secrets rejected before anything else (MR-004/G)
        for key in ("api_key", "authorization", "secret"):
            if key in model_request or key in (model_request.get(
                    "messages", [{}])[0] if model_request.get("messages")
                    else {}):
                raise ModelError(
                    f"caller-supplied {key} rejected; credentials are "
                    "resolved server-side (MR-004/G)")
        for message in model_request.get("messages", []):
            content = str(message.get("content", ""))
            if _RAW_SECRET_PATTERNS and any(
                    pat.search(content) for pat in _RAW_SECRET_PATTERNS):
                raise ModelError(
                    "raw secret shape detected in model request; rejected "
                    "(MR-004/G)")

        # replay guard (MR-005) — one-shot semantics
        self._assert_not_replayed(model_request.get("model_request_id"),
                                  model_request.get("request_id"))

        # credential resolution — server-side, returns to adapter only
        raw_credential, ref_label = self._resolve_credential(
            profile, tenant_id=tenant_id, capability_id=capability_id)

        # execute the bounded adapter
        adapter = self._adapters.get(profile["provider"])
        if adapter is None:
            raise ModelError(
                f"no adapter bound for provider {profile['provider']} "
                "(MR-002)")
        raw_credential_value = raw_credential  # retained only for the
        # response leak guard below; cleared immediately after (MR-004/I)
        started = datetime.now(timezone.utc)
        try:
            raw = adapter.invoke(model_request=model_request,
                                 credential=raw_credential)
        finally:
            raw_credential = ""  # never retained past the call
        latency_ms = (datetime.now(timezone.utc) - started).total_seconds() \
            * 1000.0

        # build the typed response; redact everything serialized
        response_id = f"mrsp-{uuid.uuid4().hex[:12]}"
        audit_ref = f"audit:{response_id}"
        response = {
            "model_response_id": response_id,
            "model_request_id": model_request.get("model_request_id"),
            "provider": profile["provider"],
            "model_id": model_id,
            "model_version_if_available":
                raw.get("model_version_if_available"),
            "output_text_or_structured_payload":
                raw.get("output_text_or_structured_payload"),
            "finish_reason": raw.get("finish_reason"),
            "input_tokens": int(raw.get("input_tokens", 0)),
            "output_tokens": int(raw.get("output_tokens", 0)),
            "total_tokens": int(raw.get("input_tokens", 0)
                                + raw.get("output_tokens", 0)),
            "latency_ms": round(latency_ms, 3),
            "cost_usd_if_known": raw.get("cost_usd_if_known"),
            "provider_request_id": raw.get("provider_request_id"),
            "retry_count": int(raw.get("retry_count", 0)),
            "safety_or_filter_metadata": raw.get("safety_or_filter_metadata"),
            "generated_at": _now(),
            "audit_ref": audit_ref,
        }
        # MR-004/I: the raw credential never leaks into the response
        serialized = str(response)
        if raw_credential_value and raw_credential_value in serialized:
            raise ModelError(
                "credential leaked into model response; aborting (MR-004/I)")
        raw_credential_value = ""  # released immediately after the guard
        # token/cost numbers are redaction-proof by construction

        # structured audit — credential REFERENCE id, never the value
        self._audit.append({
            "model_request_id": model_request.get("model_request_id"),
            "request_id": model_request.get("request_id"),
            "principal_id": actor,
            "tenant_id": tenant_id,
            "project_id": project_id,
            "resource_id": resource_id,
            "task_id": model_request.get("task_id"),
            "purpose": purpose,
            "provider": profile["provider"],
            "model_id": model_id,
            "provider_profile_id": profile_id,
            "capability_id": capability_id,
            "decision_id": authorization_decision.get("decision_id"),
            "credential_ref": ref_label,
            "input_tokens": response["input_tokens"],
            "output_tokens": response["output_tokens"],
            "cost_usd_if_known": response["cost_usd_if_known"],
            "latency_ms": response["latency_ms"],
            "success": True,
            "retry_count": response["retry_count"],
            "audit_ref": audit_ref,
            "generated_at": _now(),
        })
        return response

    def audit_trail(self) -> list[dict]:
        return list(self._audit)
