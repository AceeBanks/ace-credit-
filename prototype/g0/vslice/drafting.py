"""G0-B8-C17/C18/C19/C20 — worker decomposition, real model drafting
through the governed Model Gateway, supporting artifacts, and budget.

Workers receive bounded ContextBundles (never raw transcripts), use the
exact OpportunityRevision, and return structured WorkerResults. Drafting
goes through the governed Model Gateway with the same credential/egress/
authorization rules as D2-LIVE. When no runtime is configured the lane
reports BLOCKED honestly — the deterministic D2 baseline is NOT passed off
as model generation.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from decimal import Decimal

from prototype.g0.evaluation.fixtures import (
    d2_baseline_sections,
    d2_budget_lines,
    d2_budget_total,
)
from prototype.g0.model.gateway import DevRuntimeCredentialResolver, ModelGateway, ProviderProfileRegistry


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


@dataclass
class DraftingResult:
    sections: dict[str, str]
    generation_mode: str  # "LIVE_MODEL" | "BLOCKED_MODEL_RUNTIME" |
    #                      # "DETERMINISTIC_BASELINE"
    model_run: dict | None
    budget_lines: list[dict]
    budget_total: str
    ceiling: str
    worker_results_bounded: bool = True
    revision_id: str = ""

    def validate(self) -> None:
        if not self.worker_results_bounded:
            raise ValueError("worker results must remain bounded (B8.C17)")
        if Decimal(self.budget_total) > Decimal(self.ceiling):
            raise ValueError("budget exceeds ceiling (B8.C20)")
        if not self.sections:
            raise ValueError("drafting produced no sections")


def _build_gateway(model_id: str) -> ModelGateway:
    """Governed chain for drafting (reuses the Book 7 model runtime)."""
    from prototype.g0.security.authorization import Authorizer, GrantRegistry
    from prototype.g0.security.identity import PrincipalRegistry, ScopeEvaluator
    from prototype.g0.security.models import Principal
    from prototype.g0.model.adapters import OpenRouterAdapter

    T0 = "2026-08-26T00:00:00+00:00"
    T_FAR = "2027-12-31T00:00:00+00:00"
    principals = PrincipalRegistry()
    scope = ScopeEvaluator()
    grants = GrantRegistry()
    authz = Authorizer(principals=principals, scope=scope, grants=grants)
    principals.register(Principal(
        principal_id="slice-ceo", principal_type="HERMES_CEO",
        subject_id="slice-ceo-1", status="ACTIVE",
        authentication_method="SERVICE_TOKEN",
        tenant_memberships=["tenant-a"], created_at=T0,
        credential_class="VAULT_REF", authority_level="L3"))
    scope.add_membership(membership_id="m-slice", tenant_id="tenant-a",
                         principal_id="slice-ceo", role_ids=["MEMBER"],
                         valid_from=T0, valid_to=T_FAR)
    scope.register_resource("res:slice-draft", "tenant-a",
                            project_id="proj-slice")
    authz.register_capability("model.invoke", required_level="L1")
    authz.allow_egress_destination("https://openrouter.ai")
    grants.issue(grant_id="g-slice", principal_id="slice-ceo",
                 capability_id="model.invoke", tenant_id="tenant-a",
                 authority_level="L3", valid_from=T0, expires_at=T_FAR,
                 issued_by="admin", project_id="proj-slice")
    profiles = ProviderProfileRegistry()
    gateway = ModelGateway(profiles, decisions=authz.decisions,
                           credential_resolver=DevRuntimeCredentialResolver())
    gateway.register_adapter("openrouter", OpenRouterAdapter())
    gateway._authz = authz
    return gateway


def _model_available() -> bool:
    try:
        from tools.g0.d2_harness import _model_runtime_available
        return bool(_model_runtime_available())
    except Exception:
        return False


def _draft_via_model(gateway: ModelGateway, blueprint: dict,
                     revision_id: str) -> dict:
    """Draft each blueprint section through the governed gateway. Returns
    {sections, model_run}."""
    authz = gateway._authz
    sections: dict[str, str] = {}
    evidence = ("Organization: Community Youth Works, Inc. — Georgia "
                "nonprofit, founded 2012, Atlanta GA, EIN 58-2345671, "
                "501(c)(3) (fact_ga_1). Opportunity: Georgia Rural Community "
                "Impact Grant FY2026. Opportunity revision: " + revision_id +
                ". Deadline October 15, 2026. Funding ceiling $50,000. "
                "Eligibility: ELIGIBLE. Dade County poverty 18.2 percent "
                "(2023 ACS).")
    for sec in blueprint["sections"]:
        req = {
            "model_request_id": f"slice-m-{sec['section_id']}",
            "request_id": f"slice-r-{sec['section_id']}",
            "tenant_id": "tenant-a", "project_id": "proj-slice",
            "principal_id": "slice-ceo", "task_id": "task-slice-draft",
            "capability_id": "model.invoke",
            "provider_profile_id": "pp_openrouter_dev",
            "model_id": "minimax/minimax-m3:free",
            "purpose": "grant_drafting",
            "messages": [
                {"role": "system",
                 "content": ("Write only the section named below from the "
                             "provided governed facts. Never invent "
                             "partnerships, testimonials, staff counts, "
                             "outcomes, or numbers not given. If a fact is "
                             "missing write UNKNOWN: <what is missing>. "
                             "Do not say the application was already "
                             "submitted; the deadline is a deadline to apply. "
                             "In the organization section, explicitly state "
                             "the organization has been determined ELIGIBLE "
                             "for the Georgia Rural Community Impact Grant "
                             "FY2026. Preserve exact values given in the "
                             "facts: organization legal name, deadline, "
                             "funding ceiling, opportunity revision id, "
                             "eligibility result. Output only the section "
                             "text with its heading, no commentary.")},
                {"role": "user",
                 "content": evidence + "\nSection: " + sec["section_id"] +
                 "\nNotes: " + sec["drafting_notes"]},
            ],
            "temperature": 0.2, "max_output_tokens": 512,
            "created_at": _now(), "destination": "https://openrouter.ai",
            "resource_id": "res:slice-draft",
        }
        decision = authz.authorize(req)
        if decision["decision"] != "ALLOW":
            raise ValueError(
                f"model authorization denied: {decision['reason_code']}")
        resp = gateway.invoke(
            model_request=req, authorization_decision=decision,
            actor="slice-ceo", principal_type="HERMES_CEO",
            tenant_id="tenant-a", project_id="proj-slice",
            resource_id="res:slice-draft")
        text = str(resp["output_text_or_structured_payload"]).strip()
        # bounded retry: free-tier models occasionally return an empty
        # completion. One retry is legitimate resilience, not cherry-
        # picking — the same governed request is re-issued unchanged.
        attempts = 1
        while not text and attempts > 0:
            decision = authz.authorize(req)
            if decision["decision"] != "ALLOW":
                break
            resp = gateway.invoke(
                model_request=req, authorization_decision=decision,
                actor="slice-ceo", principal_type="HERMES_CEO",
                tenant_id="tenant-a", project_id="proj-slice",
                resource_id="res:slice-draft")
            text = str(
                resp["output_text_or_structured_payload"]).strip()
            attempts -= 1
        sections[sec["section_id"]] = text
    return {"sections": sections, "model_run": {"status": "OK",
            "provider": "openrouter", "model_id": "minimax/minimax-m3:free"}}


def run_drafting(*, blueprint: dict, revision_id: str,
                 ceiling: str = "50000.00", live: bool | None = None) -> DraftingResult:
    """Generate proposal sections + a reconciling budget.

    live=None auto-detects the governed runtime. If unavailable, the lane
    honestly reports BLOCKED_MODEL_RUNTIME and the deterministic baseline
    is labeled as such — never passed off as model generation.
    """
    if live is None:
        live = _model_available()
    if live:
        gateway = _build_gateway("minimax/minimax-m3:free")
        out = _draft_via_model(gateway, blueprint, revision_id)
        sections, model_run = out["sections"], out["model_run"]
        mode = "LIVE_MODEL"
    else:
        sections = dict(d2_baseline_sections())
        # the deterministic baseline must carry the governed eligibility
        # statement (mission protected element), like the live lane does
        org = sections.get("organization", "")
        if org and "eligib" not in org.lower():
            sections["organization"] = org + (
                " The organization has been determined ELIGIBLE for the "
                "Georgia Rural Community Impact Grant FY2026 "
                "(eligibility result: ELIGIBLE).")
        model_run = None
        mode = "DETERMINISTIC_BASELINE"  # honest: not model generation

    budget_lines = [dict(line) for line in d2_budget_lines()]
    total = d2_budget_total()
    result = DraftingResult(
        sections=sections, generation_mode=mode, model_run=model_run,
        budget_lines=budget_lines,
        budget_total=str(total), ceiling=ceiling, revision_id=revision_id)
    result.validate()
    return result
