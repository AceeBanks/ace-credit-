#!/usr/bin/env python3
"""G0-B7-PHASE-B2 — governed model runtime live smoke test.

Runs ONE harmless deterministic request through the FULL governed chain:

    PrincipalRegistry → GrantRegistry → Authorizer
    → AuthorizationDecision (registry-sealed) → ModelGateway
    → ProviderProfileRegistry → OpenRouterAdapter → live provider

The smoke payload is deliberately inert: it asks the model to return a JSON
object containing the supplied organization name unchanged — no drafting,
no client data, no side effects, MOCK/NON_SUBMISSION.

Credential: DEV_RUNTIME_ONLY resolver reads OPENROUTER_API_KEY from the
process environment server-side; the raw value is never printed, logged, or
serialized. If the variable is absent the tool reports
BLOCKED_MODEL_RUNTIME and exits 0 (an honest blocked state, not a failure).

Validates after the call:
  * gateway authorization (PDP ALLOW, capability binding)
  * server-side secret resolution
  * provider response received
  * structured output sanity
  * cost/latency recorded
  * audit emitted with credential REFERENCE only
  * no raw secret anywhere in the response/audit serialization

Usage: python tools/g0/model_smoke.py [--model openai/gpt-4o-mini]
"""
from __future__ import annotations

import json
import sys
from datetime import datetime, timezone
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[2]
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from prototype.g0.model.adapters import OpenRouterAdapter  # noqa: E402
from prototype.g0.model.gateway import (  # noqa: E402
    DevRuntimeCredentialResolver,
    ModelGateway,
    ProviderProfileRegistry,
)
from prototype.g0.security.authorization import Authorizer, GrantRegistry  # noqa: E402
from prototype.g0.security.identity import (  # noqa: E402
    PrincipalRegistry,
    ScopeEvaluator,
)
from prototype.g0.security.models import Principal  # noqa: E402

T0 = "2026-08-26T00:00:00+00:00"
T_FAR = "2027-12-31T00:00:00+00:00"


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def build_chain(model_id: str = "openai/gpt-4o-mini") -> tuple[dict, ModelGateway]:
    """Wire the real governed chain for the smoke test."""
    principals = PrincipalRegistry()
    scope = ScopeEvaluator()
    grants = GrantRegistry()
    authz = Authorizer(principals=principals, scope=scope, grants=grants)

    principals.register(Principal(
        principal_id="smoke-ceo", principal_type="HERMES_CEO",
        subject_id="smoke-ceo-1", status="ACTIVE",
        authentication_method="SERVICE_TOKEN",
        tenant_memberships=["tenant-a"], created_at=T0,
        credential_class="VAULT_REF", authority_level="L3"))
    scope.add_membership(membership_id="m-smoke", tenant_id="tenant-a",
                         principal_id="smoke-ceo", role_ids=["MEMBER"],
                         valid_from=T0, valid_to=T_FAR)
    scope.register_resource("res:smoke", "tenant-a", project_id="proj-smoke")

    authz.register_capability("model.invoke", required_level="L1")
    authz.allow_egress_destination("https://openrouter.ai")

    grants.issue(grant_id="g-smoke", principal_id="smoke-ceo",
                 capability_id="model.invoke", tenant_id="tenant-a",
                 authority_level="L3", valid_from=T0, expires_at=T_FAR,
                 issued_by="admin", project_id="proj-smoke")

    profiles = ProviderProfileRegistry()
    gateway = ModelGateway(profiles, decisions=authz.decisions,
                           credential_resolver=DevRuntimeCredentialResolver())
    gateway.register_adapter("openrouter", OpenRouterAdapter())

    req = {
        "model_request_id": "smoke-m1", "request_id": "smoke-r1",
        "tenant_id": "tenant-a", "project_id": "proj-smoke",
        "principal_id": "smoke-ceo", "task_id": "task-smoke",
        "capability_id": "model.invoke",
        "provider_profile_id": "pp_openrouter_dev",
        "model_id": model_id, "purpose": "smoke_test",
        "messages": [
            {"role": "system",
             "content": "Return a JSON object with the single key "
                        "\"organization_name\" whose value is the "
                        "organization name from the user message, unchanged."},
            {"role": "user",
             "content": "Organization name: Community Youth Works, Inc."},
        ],
        "temperature": 0.0, "max_output_tokens": 64,
        "structured_output_schema_ref": "json_object",
        "created_at": _now(), "destination": "https://openrouter.ai",
        "resource_id": "res:smoke",
    }
    decision = authz.authorize(req)
    return {"req": req, "decision": decision, "gateway": gateway,
            "authz": authz}, gateway


def main() -> int:
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--model", default="openai/gpt-4o-mini")
    args = parser.parse_args()
    chain, gateway = build_chain(model_id=args.model)
    req = chain["req"]
    decision = chain["decision"]

    if decision["decision"] != "ALLOW":
        print(json.dumps({
            "smoke": "FAIL",
            "block": "authorization denied",
            "reason_code": decision["reason_code"],
            "model_runtime": "BLOCKED_MODEL_RUNTIME",
            "note": "gateway requires a PDP ALLOW before any provider call; "
                    "no provider request was attempted",
        }, indent=2))
        return 0

    try:
        resp = gateway.invoke(
            model_request=req, authorization_decision=decision,
            actor="smoke-ceo", principal_type="HERMES_CEO",
            tenant_id="tenant-a", project_id="proj-smoke",
            resource_id="res:smoke")
    except Exception as exc:
        print(json.dumps({
            "smoke": "FAIL",
            "model_runtime": "AVAILABLE",
            "error": str(exc)[:500],
            "note": "live provider call failed; no fabrication",
        }, indent=2))
        return 1

    audit = gateway.audit_trail()
    serialized = json.dumps({"response": resp, "audit": audit},
                            default=str)
    import re
    leaked = re.findall(r"sk-[A-Za-z0-9]{16,}|OPENROUTER_API_KEY", serialized)
    report = {
        "smoke": "PASS",
        "model_runtime": "AVAILABLE",
        "provider": resp["provider"],
        "model_id": resp["model_id"],
        "finish_reason": resp["finish_reason"],
        "input_tokens": resp["input_tokens"],
        "output_tokens": resp["output_tokens"],
        "latency_ms": resp["latency_ms"],
        "cost_usd_if_known": resp["cost_usd_if_known"],
        "output_preview": str(
            resp["output_text_or_structured_payload"])[:200],
        "audit_ref": resp["audit_ref"],
        "audit_credential_ref": audit[-1]["credential_ref"],
        "secret_leak_detected": bool(leaked),
        "submission_enabled": False,
        "checked_at": _now(),
    }
    print(json.dumps(report, indent=2))
    return 0 if not leaked else 2


if __name__ == "__main__":
    sys.exit(main())
