#!/usr/bin/env python3
"""G1-W4-LIVE — first complete full-proposal experiment through the
governed Model Gateway.

Runs the full Grant factory (blueprint -> 7 sections -> synthesis -> budget
-> full QA -> DOCX/PDF) with the LIVE_MODEL lane wired to the governed G0
Model Gateway (same credential/egress/authorization rules as D2-LIVE).
When the governed runtime is unavailable the lane honestly reports
BLOCKED_MODEL_RUNTIME — the deterministic baseline is never passed off as
model generation.

Artifacts land in docs/grant-sector/g1/w4-live/.
"""
from __future__ import annotations

import json
import sys
from datetime import datetime, timezone
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[2]
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))
_SEED = _ROOT / "production-seed"
if str(_SEED) not in sys.path:
    sys.path.insert(0, str(_SEED))

from grant_platform.factory.orchestrator import run_factory  # noqa: E402

OUT_DIR = _ROOT / "docs" / "grant-sector" / "g1" / "w4-live"


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _model_runtime_available() -> bool:
    try:
        from prototype.g0.model.gateway import ProviderProfileRegistry
        profiles = ProviderProfileRegistry()
        profiles.get("pp_openrouter_dev")
        return bool(__import__("os").environ.get("OPENROUTER_API_KEY", ""))
    except Exception:
        return False


def build_governed_model_invoke(model_id: str =
                                "nvidia/nemotron-3.5-lightning:free"):
    """Return model_invoke(bundle) -> str wired through the governed Model
    Gateway. Never exposes credentials; the gateway resolves them
    server-side (DEV_RUNTIME_ONLY)."""
    from prototype.g0.model.adapters import OpenRouterAdapter
    from prototype.g0.model.gateway import (
        DevRuntimeCredentialResolver,
        ModelGateway,
        ProviderProfileRegistry,
    )
    from prototype.g0.security.authorization import Authorizer, GrantRegistry
    from prototype.g0.security.identity import (
        PrincipalRegistry,
        ScopeEvaluator,
    )
    from prototype.g0.security.models import Principal

    T0 = "2026-08-26T00:00:00+00:00"
    T_FAR = "2027-12-31T00:00:00+00:00"
    principals = PrincipalRegistry()
    scope = ScopeEvaluator()
    grants = GrantRegistry()
    authz = Authorizer(principals=principals, scope=scope, grants=grants)
    principals.register(Principal(
        principal_id="g1-w4-ceo", principal_type="HERMES_CEO",
        subject_id="g1-w4-ceo-1", status="ACTIVE",
        authentication_method="SERVICE_TOKEN",
        tenant_memberships=["tenant-a"], created_at=T0,
        credential_class="VAULT_REF", authority_level="L3"))
    scope.add_membership(membership_id="m-w4", tenant_id="tenant-a",
                         principal_id="g1-w4-ceo", role_ids=["MEMBER"],
                         valid_from=T0, valid_to=T_FAR)
    scope.register_resource("res:w4-draft", "tenant-a",
                            project_id="proj-w4")
    authz.register_capability("model.invoke", required_level="L1")
    authz.allow_egress_destination("https://openrouter.ai")
    grants.issue(grant_id="g-w4", principal_id="g1-w4-ceo",
                 capability_id="model.invoke", tenant_id="tenant-a",
                 authority_level="L3", valid_from=T0, expires_at=T_FAR,
                 issued_by="admin", project_id="proj-w4")
    profiles = ProviderProfileRegistry()
    gateway = ModelGateway(profiles, decisions=authz.decisions,
                           credential_resolver=DevRuntimeCredentialResolver())
    gateway.register_adapter("openrouter", OpenRouterAdapter())
    gateway._authz = authz

    counter = {"n": 0}

    def model_invoke(bundle: dict) -> str:
        counter["n"] += 1
        i = counter["n"]
        req = {
            "model_request_id": f"w4-m-{i}",
            "request_id": f"w4-r-{i}",
            "tenant_id": "tenant-a", "project_id": "proj-w4",
            "principal_id": "g1-w4-ceo", "task_id": f"task-w4-{i}",
            "capability_id": "model.invoke",
            "provider_profile_id": "pp_openrouter_dev",
            "model_id": model_id,
            "purpose": "grant_drafting",
            "messages": [
                {"role": "system", "content": bundle["instructions"]},
                {"role": "user", "content": (
                    bundle["evidence"] + "\nSection: " +
                    bundle["section_id"] + "\nNotes: " +
                    bundle["notes"])},
            ],
            "temperature": 0.2, "max_output_tokens": 512,
            "created_at": _now(), "destination": "https://openrouter.ai",
            "resource_id": "res:w4-draft",
        }
        decision = authz.authorize(req)
        if decision["decision"] != "ALLOW":
            raise ValueError(
                f"model authorization denied: {decision['reason_code']}")
        resp = gateway.invoke(
            model_request=req, authorization_decision=decision,
            actor="g1-w4-ceo", principal_type="HERMES_CEO",
            tenant_id="tenant-a", project_id="proj-w4",
            resource_id="res:w4-draft")
        text = str(resp["output_text_or_structured_payload"]).strip()
        # bounded retry (same governed request, unchanged) for free-tier
        # empty completions
        attempts = 1
        while not text and attempts > 0:
            decision = authz.authorize(req)
            if decision["decision"] != "ALLOW":
                break
            resp = gateway.invoke(
                model_request=req, authorization_decision=decision,
                actor="g1-w4-ceo", principal_type="HERMES_CEO",
                tenant_id="tenant-a", project_id="proj-w4",
                resource_id="res:w4-draft")
            text = str(resp["output_text_or_structured_payload"]).strip()
            attempts -= 1
        return text

    return model_invoke, gateway, counter


def main() -> int:
    live = _model_runtime_available()
    model_id = "minimax/minimax-m3:free"
    model_invoke = None
    gateway = None
    if live:
        model_invoke, gateway, counter = build_governed_model_invoke(model_id)

    factory = run_factory(project_id="proj-w4",
                          model_invoke=model_invoke, model_id=model_id)
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    # write artifacts (real DOCX/PDF payloads)
    docx_path = OUT_DIR / "W4_LIVE_PROPOSAL.docx"
    pdf_path = OUT_DIR / "W4_LIVE_PROPOSAL.pdf"
    factory.docx.write(str(docx_path))
    factory.pdf.write(str(pdf_path))

    # markdown draft
    md = "\n\n".join(
        f"## {sid.replace('_', ' ').title()}\n\n{s.text}"
        for sid, s in factory.draft.sections.items())
    (OUT_DIR / "W4_LIVE_PROPOSAL.md").write_text(md, encoding="utf-8")

    model_run = {
        "provider": "openrouter" if live else None,
        "model_id": model_id if live else None,
        "generation_mode": factory.draft.generation_mode,
        "model_runs": factory.model_runs,
        "model_available": live,
        "honest_note": ("governed model lane executed through the Model "
                        "Gateway" if live
                        else "BLOCKED_MODEL_RUNTIME: no governed runtime; "
                             "deterministic baseline labeled as such"),
    }
    (OUT_DIR / "W4_LIVE_MODEL_RUN.json").write_text(
        json.dumps(model_run, indent=2), encoding="utf-8")

    report = {
        "experiment": "G1-W4-LIVE — first complete full-proposal experiment",
        "label": "MOCK_NON_SUBMISSION",
        "submission_enabled": False,
        "generated_at": _now(),
        "summary": factory.summary(),
        "model_run": model_run,
        "docx_artifact": str(docx_path.relative_to(_ROOT)),
        "pdf_artifact": str(pdf_path.relative_to(_ROOT)),
        "reproduce": ["python tools/g1/run_w4_live.py"],
    }
    (OUT_DIR / "W4_LIVE_REPORT.json").write_text(
        json.dumps(report, indent=2), encoding="utf-8")
    print(json.dumps(report, indent=2)[:3000])
    return 0


if __name__ == "__main__":
    sys.exit(main())
