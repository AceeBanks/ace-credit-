"""B1.C9 — Audit & Accountability contract validator.

Enforces the plan's audit-event minimum and hard requirements:

- every event carries the full minimum field set;
- consequential operations (capability side_effect_class CANONICAL_MUTATION /
  EXTERNAL_ACTION / LEGALLY_MATERIAL) MUST carry actor_id and request_id —
  an event for a consequential op lacking either fails validation;
- audit history stays separate from agent memory (the validator is the
  boundary check; the durable store is a Book 5+ concern);
- tenant filtering is mandatory — cross-tenant audit access is blocked by the
  scope model (can_view_audit);
- sensitive values are redacted — an event carrying a raw secret fixture
  fails validation;
- approval decisions stay linkable — an event that references an approval
  must also reference the policy decision.

Contract mirrors every other G0 validator:
    validate(event, context) -> (ok: bool, report: dict)
Fail closed: missing/malformed fields are hard failures, never warnings.
"""
from __future__ import annotations

import json
import re
import sys
from datetime import datetime
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[2]
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from tools.g0._common import finish  # noqa: E402

VALIDATOR = "audit_event"

# Plan B1.C9 "Audit event minimum" — all fields, in plan order.
AUDIT_EVENT_MINIMUM = (
    "event_id", "timestamp", "actor_id", "actor_type", "tenant_id",
    "project_id", "capability_id", "authority_level", "resource_type",
    "resource_id", "request_id", "approval_ref", "input_artifact_refs",
    "output_artifact_refs", "source_refs", "result_status", "error_class",
    "policy_decision_ref",
)

# Consequential side-effect classes require a fully attributable event.
CONSEQUENTIAL = {"CANONICAL_MUTATION", "EXTERNAL_ACTION", "LEGALLY_MATERIAL"}

VALID_RESULT_STATUSES = {"SUCCESS", "FAILED", "BLOCKED", "DENIED", "REQUIRE_APPROVAL"}

# Common raw-secret shapes (defense-in-depth; explicit fixtures are the test).
_SECRET_PATTERNS = (
    re.compile(r"sk-[A-Za-z0-9]{16,}"),      # OpenAI-style
    re.compile(r"AKIA[0-9A-Z]{16}"),         # AWS access key id
    re.compile(r"xox[baprs]-[A-Za-z0-9-]{10,}"),  # Slack tokens
    re.compile(r"eyJ[A-Za-z0-9_-]{20,}\.[A-Za-z0-9_-]{10,}\.[A-Za-z0-9_-]{10,}"),  # JWT
)


def _scan_strings(value, path: str, secrets: tuple[str, ...],
                  errors: list) -> None:
    """Recursively scan event values for raw secrets (fixtures + patterns)."""
    if isinstance(value, dict):
        for k, v in value.items():
            _scan_strings(v, f"{path}.{k}", secrets, errors)
    elif isinstance(value, (list, tuple)):
        for i, v in enumerate(value):
            _scan_strings(v, f"{path}[{i}]", secrets, errors)
    elif isinstance(value, str):
        for secret in secrets:
            if secret and secret in value:
                errors.append(f"{path}: contains raw secret fixture (LAW-B1-014)")
        for pat in _SECRET_PATTERNS:
            if pat.search(value):
                errors.append(f"{path}: value matches a raw secret shape "
                              "(LAW-B1-014) — redact before logging")


def validate(event: dict, context: dict | None = None) -> tuple[bool, dict]:
    """Validate one audit event against the B1.C9 contract.

    `context` may carry:
      - "secrets": tuple of raw secret fixture values that must never appear;
      - "capability_side_effect": map capability_id -> side_effect_class, so
        consequential-op attribution can be enforced from registry evidence.
    """
    context = context or {}
    secrets = tuple(context.get("secrets") or ())
    side_effects = context.get("capability_side_effect") or {}

    errors: list[str] = []

    if not isinstance(event, dict):
        return finish(VALIDATOR, False,
                      {"errors": ["event is not a mapping"], "checks": {}})

    missing = [f for f in AUDIT_EVENT_MINIMUM if f not in event]
    if missing:
        errors.append(f"missing audit event fields: {missing}")

    # event_id / timestamp sanity
    if event.get("event_id") in (None, ""):
        errors.append("event_id must be non-empty")
    ts = event.get("timestamp")
    if ts is not None and isinstance(ts, str) and ts.strip():
        try:
            datetime.fromisoformat(ts.replace("Z", "+00:00"))
        except ValueError:
            errors.append(f"timestamp not ISO-8601: {ts!r}")

    # result_status must resolve
    if event.get("result_status") not in VALID_RESULT_STATUSES:
        errors.append(f"unknown result_status '{event.get('result_status')}'")

    # consequential attribution: actor_id + request_id mandatory
    cap_id = event.get("capability_id")
    side_effect = side_effects.get(cap_id) if cap_id else None
    if side_effect in CONSEQUENTIAL:
        if not event.get("actor_id"):
            errors.append(f"consequential op '{cap_id}' lacks actor_id "
                          "(B1.C9 mandatory attribution)")
        if not event.get("request_id"):
            errors.append(f"consequential op '{cap_id}' lacks request_id "
                          "(B1.C9 mandatory attribution)")

    # tenant filtering: tenant-scoped events require a tenant
    if event.get("tenant_id") in (None, ""):
        errors.append("tenant_id must be non-empty for audit events (LAW-B1-015)")

    # approval linkability: approval_ref implies policy_decision_ref
    if event.get("approval_ref") and not event.get("policy_decision_ref"):
        errors.append("approval_ref present but policy_decision_ref missing "
                      "(approval decisions must be linkable)")

    # redaction scan (only after structural checks; never log the value itself)
    _scan_strings(event, "event", secrets, errors)

    checks = {
        "fields_present": len(AUDIT_EVENT_MINIMUM) - len(missing),
        "fields_total": len(AUDIT_EVENT_MINIMUM),
        "consequential_side_effect": side_effect if side_effect in CONSEQUENTIAL else None,
        "tenant_present": bool(event.get("tenant_id")),
    }
    return finish(VALIDATOR, not errors, {"errors": errors, "checks": checks})


def can_view_audit(actor_tenants, event_tenant_id: str, *,
                   platform_wide: bool = False) -> bool:
    """Tenant scope model for audit access (B1.C9: tenant filtering mandatory).

    A tenant-scoped actor may view audit events of their own tenants only;
    platform-wide actors (ACTOR-HUMAN-ADMIN, platform-wide services) may view
    across tenants. Everything else is blocked.
    """
    if platform_wide:
        return True
    return bool(event_tenant_id) and event_tenant_id in set(actor_tenants or ())


def main() -> int:
    payload = json.load(sys.stdin)
    ok, report = validate(payload.get("event", {}), payload.get("context", {}))
    print(json.dumps(report, indent=2))
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
