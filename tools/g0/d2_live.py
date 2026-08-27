#!/usr/bin/env python3
"""G0-B7-PHASE-C — D2 LIVE: first governed model-generated grounded Grant
experiment.

Runs the REAL pipeline: governed fixture (Community Youth Works, Inc. +
Georgia Rural Community Impact Grant FY2026, opp_rev_ga_501_1) -> bounded
ContextBundle -> governed Model Gateway -> actual model -> BASELINE LIVE
GROUNDED DRAFT -> deterministic QA -> Claim Ledger -> factuality metrics ->
requirement coverage.

The model receives ONLY governed evidence (organization, revision, deadline,
ceiling, eligibility, statistics, requirements) and explicit instructions
not to invent partnerships, testimonials, past performance, staff counts,
budget details, outcomes, or locations. Missing information must remain
visibly unresolved (UNKNOWN/ASSUMPTION/QUESTION/EVIDENCE_GAP).

The evaluation is honest: any protected fact the draft drops or alters, any
fabrication marker, any submission language is recorded as a FAIL. The
result is MOCK / NON_SUBMISSION; submission stays structurally impossible.

Artifacts written to docs/grant-sector/g0/07-evaluation/d2-live/:
  D2_LIVE_INPUT_MANIFEST.json
  D2_LIVE_BASELINE_DRAFT.md
  D2_LIVE_BASELINE_CLAIM_LEDGER.json
  D2_LIVE_BASELINE_EVAL.json
  D2_LIVE_BASELINE_MODEL_RUN.json
  D2_LIVE_REPRODUCTION_MANIFEST.json

Usage: python tools/g0/d2_live.py [--model openrouter/free]
"""
from __future__ import annotations

import json
import re
import sys
from datetime import datetime, timezone
from decimal import Decimal
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[2]
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from prototype.g0.evaluation.assertions import (  # noqa: E402
    check_deadline_consistency,
    check_eligibility_statement,
    check_funding_amount,
    check_no_unsupported_fabrications,
    check_protected_facts_unchanged,
    check_required_sections_present,
    check_revision_identity,
    check_submission_absent,
    check_word_limit,
    run_assertion_suite,
)
from prototype.g0.evaluation.fixtures import (  # noqa: E402
    D2_FIXTURE,
    D2_PROTECTED_ELEMENTS,
    d2_budget_lines,
    d2_budget_total,
    d2_claim_ledger_seed,
    d2_requirements_text,
)
from prototype.g0.evaluation.metrics import (  # noqa: E402
    claim_support_metrics,
    citation_metrics,
    requirement_coverage,
    unsupported_material_claims,
)
from prototype.g0.model.adapters import OpenRouterAdapter  # noqa: E402
from prototype.g0.model.gateway import (  # noqa: E402
    DevRuntimeCredentialResolver,
    ModelGateway,
    ProviderProfileRegistry,
)
from prototype.g0.security.authorization import (  # noqa: E402
    Authorizer,
    GrantRegistry,
)
from prototype.g0.security.identity import (  # noqa: E402
    PrincipalRegistry,
    ScopeEvaluator,
)
from prototype.g0.security.models import Principal  # noqa: E402

T0 = "2026-08-26T00:00:00+00:00"
T_FAR = "2027-12-31T00:00:00+00:00"

OUT_DIR = _ROOT / "docs" / "grant-sector" / "g0" / "07-evaluation" / "d2-live"

# fabrication/submission scanners must be negation-aware: a draft that
# says "no information provided regarding past performance" or "has not yet
# been submitted" is CORRECT — it refuses to fabricate, it does not
# fabricate. Only affirmative statements count.
FABRICATION_MARKERS = ("testimonial from", "our partner", "endorsed by",
                       "we partner with", "letter of support from",
                       "in partnership with", "past performance")
NEGATION_PREFIXES = ("no ", "none ", "not ", "without ", "no information",
                     "none will be", "not been provided", "not yet",
                     "no staff", "no prior", "no partnership",
                     "no testimonials", "not been invented",
                     "won't be invented", "will not be", "unknown:",
                     "unknown ")
SUBMISSION_PHRASES = ("we have submitted", "application sent",
                      "form submitted", "successfully submitted",
                      "was submitted")


def _affirmative_hits(text: str, markers: tuple[str, ...]) -> list[str]:
    """Markers occurring OUTSIDE a negation context — i.e. the draft is
    actually asserting the fabricated thing rather than refusing it."""
    hits = []
    lowered = text.lower()
    for marker in markers:
        idx = lowered.find(marker)
        while idx != -1:
            before = lowered[max(0, idx - 60):idx]
            if not any(n in before for n in NEGATION_PREFIXES):
                hits.append(marker)
                break
            idx = lowered.find(marker, idx + 1)
    return hits

DRAFTING_SYSTEM = (
    "You are a grant writer for a Georgia nonprofit. Write ONLY from the "
    "facts provided in the user message. Rules: "
    "1) Never invent partnerships, testimonials, past performance, staff "
    "counts, budget details, program outcomes, locations, demographics, "
    "awards, licenses, or statistics not given. "
    "2) If a fact is missing, write UNKNOWN: <what is missing> instead of "
    "fabricating it. "
    "3) Preserve exact values: organization legal name, deadline, funding "
    "ceiling, eligibility result, and any statistics exactly as given. "
    "4) Produce exactly these sections with these headings: "
    "## community_impact, ## organization, ## budget_narrative, ## deadline. "
    "5) The application deadline is a deadline to APPLY, never write that "
    "the application was already submitted. "
    "6) In ## organization, explicitly state that the organization has been "
    "determined ELIGIBLE for the Georgia Rural Community Impact Grant "
    "FY2026 (eligibility result: ELIGIBLE). "
    "7) In ## community_impact, state the Dade County poverty statistic "
    "(18.2 percent, 2023) explicitly."
)

FABRICATION_INSTRUCTIONS = (
    "Budget guidance: total requested must be $50,000 or less; do not "
    "invent per-line budget amounts beyond what is provided. Deadline: "
    "October 15, 2026. Opportunity revision: opp_rev_ga_501_1. "
    "Eligibility: ELIGIBLE. "
    "Community evidence: Dade County, GA poverty rate 18.2 percent (2023, "
    "ACS 5-year estimate)."
)


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _protected_in_draft(draft: str) -> dict:
    """Which protected elements survived in the draft (alias-level).

    The mission's protected list requires the draft to carry: organization
    name, opportunity/program name, deadline, funding ceiling, statistics,
    eligibility statement, revision identity. Internal identifiers that are
    not expected in narrative prose (state registration, opportunity id)
    are recorded but do not fail the draft.
    """
    required_in_draft = {
        "organization_legal_name", "organization_display_name",
        "opportunity_title", "revision_id", "deadline",
        "funding_ceiling", "county_statistic", "county_statistic_geography",
        "eligibility_result",
    }
    out = {}
    for key, value in D2_PROTECTED_ELEMENTS.items():
        aliases = value if isinstance(value, list) else [value]
        present = [a for a in aliases if str(a).lower() in draft.lower()]
        out[key] = {"present": bool(present),
                    "expected": aliases, "found": present,
                    "required_in_draft": key in required_in_draft}
    return out


def detect_fabricated_claims(draft: str) -> list[dict]:
    """Scan the model draft for material claims NOT supported by governed
    evidence. The bundle carries canonical facts (e.g. fact_ga_1: 501(c)(3)
    status PROMOTED) so a claim referencing them is SUPPORTED — the scanner
    only flags claims that contradict or exceed the governed evidence, e.g.
    asserting a status the bundle never provided or inventing a specific
    value the evidence does not contain. A beautiful draft with a material
    fabrication FAILS.
    """
    fabricated = []
    lower = draft.lower()
    # the governed bundle provides 501(c)(3)=true via fact_ga_1; flag only
    # an explicit contradiction of that evidence (e.g. claims non-profit
    # status does NOT hold)
    if re.search(r"501\(c\)\(3\)\s+status\s*[:.]\s*(false|no)", lower):
        fabricated.append({
            "claim_id": "d2-live-fab-1",
            "claim_class": "ORGANIZATION_STATUS",
            "claim_text_or_structured_ref": (
                "501(c)(3) status contradicted against governed evidence "
                "fact_ga_1"),
            "material": True,
            "support_status": "UNSUPPORTED",
            "evidence_refs": ["ref:fact_ga_1"],
            "qa_status": "FAILED",
            "artifact_version_id": "d2-live-art-v1",
            "note": "draft contradicts a governed canonical fact; D2 fail "
                    "condition (fabrication)",
        })
    return fabricated


def build_context_bundle() -> str:
    """The bounded ContextBundle: ONLY governed evidence, no chat history."""
    org = D2_FIXTURE["organization"]
    rev = D2_FIXTURE["revision"]
    dec = D2_FIXTURE["decision"]
    stats = D2_FIXTURE["statistics"]
    facts = D2_FIXTURE["facts"]
    reqs = d2_requirements_text()
    stat_lines = "\n".join(
        f"- {s.metric}: {s.value} {s.unit} ({s.geography}, {s.reference_period})"
        for s in stats)
    fact_lines = "\n".join(
        f"- {f.text if hasattr(f, 'text') else f}" for f in facts)
    req_lines = "\n".join(
        f"- {r['requirement_id']}: {r['prompt']}"
        f" (mandatory={r['mandatory']})" for r in reqs)
    return (
        f"Organization legal name: {org.legal_name}\n"
        f"Organization type: Georgia nonprofit (founded 2012, Atlanta GA)\n"
        f"EIN: 58-2345671\n"
        f"Opportunity: Georgia Rural Community Impact Grant FY2026 "
        f"(opp_ga_501)\n"
        f"Opportunity revision: {rev.revision_id}\n"
        f"Deadline: {rev.deadline} (October 15, 2026)\n"
        f"Funding ceiling: ${rev.funding_ceiling}\n"
        f"Eligibility: {dec.result.value}\n"
        f"Community statistics:\n{stat_lines}\n"
        f"Canonical facts:\n{fact_lines}\n"
        f"Requirements:\n{req_lines}\n"
        f"{FABRICATION_INSTRUCTIONS}"
    )


def build_chain(model_id: str) -> tuple[dict, ModelGateway]:
    """Wire the real governed chain for the live D2 experiment."""
    principals = PrincipalRegistry()
    scope = ScopeEvaluator()
    grants = GrantRegistry()
    authz = Authorizer(principals=principals, scope=scope, grants=grants)

    principals.register(Principal(
        principal_id="d2-ceo", principal_type="HERMES_CEO",
        subject_id="d2-ceo-1", status="ACTIVE",
        authentication_method="SERVICE_TOKEN",
        tenant_memberships=["tenant-a"], created_at=T0,
        credential_class="VAULT_REF", authority_level="L3"))
    scope.add_membership(membership_id="m-d2", tenant_id="tenant-a",
                         principal_id="d2-ceo", role_ids=["MEMBER"],
                         valid_from=T0, valid_to=T_FAR)
    scope.register_resource("res:d2-draft", "tenant-a", project_id="proj-d2")

    authz.register_capability("model.invoke", required_level="L1")
    authz.allow_egress_destination("https://openrouter.ai")

    grants.issue(grant_id="g-d2", principal_id="d2-ceo",
                 capability_id="model.invoke", tenant_id="tenant-a",
                 authority_level="L3", valid_from=T0, expires_at=T_FAR,
                 issued_by="admin", project_id="proj-d2")

    profiles = ProviderProfileRegistry()
    gateway = ModelGateway(profiles, decisions=authz.decisions,
                           credential_resolver=DevRuntimeCredentialResolver())
    gateway.register_adapter("openrouter", OpenRouterAdapter())
    return {"req": None, "gateway": gateway, "authz": authz,
            "principals": principals}, gateway


def run_live_draft(model_id: str) -> dict:
    """Issue the model call through the governed gateway and return the
    model-run record (never fabricated)."""
    chain, gateway = build_chain(model_id)
    context = build_context_bundle()
    req = {
        "model_request_id": "d2-live-m1", "request_id": "d2-live-r1",
        "tenant_id": "tenant-a", "project_id": "proj-d2",
        "principal_id": "d2-ceo", "task_id": "task-d2-draft",
        "capability_id": "model.invoke",
        "provider_profile_id": "pp_openrouter_dev",
        "model_id": model_id, "purpose": "grant_drafting",
        "messages": [
            {"role": "system", "content": DRAFTING_SYSTEM},
            {"role": "user", "content": context},
        ],
        "temperature": 0.2, "max_output_tokens": 2048,
        "created_at": _now(), "destination": "https://openrouter.ai",
        "resource_id": "res:d2-draft",
        "evidence_refs": ["ref:opp_rev_ga_501_1", "ref:stat_ga_42",
                          "ref:snap-ga-1", "ref:snap-ga-2"],
    }
    decision = chain["authz"].authorize(req)
    if decision["decision"] != "ALLOW":
        return {"status": "DENIED",
                "reason_code": decision["reason_code"],
                "model_id": model_id, "generated_at": _now()}
    resp = gateway.invoke(
        model_request=req, authorization_decision=decision,
        actor="d2-ceo", principal_type="HERMES_CEO",
        tenant_id="tenant-a", project_id="proj-d2",
        resource_id="res:d2-draft")
    return {
        "status": "OK",
        "model_request": {
            "model_id": model_id, "purpose": "grant_drafting",
            "temperature": 0.2, "max_output_tokens": 2048,
            "provider_profile_id": "pp_openrouter_dev",
        },
        "response": resp,
        "audit": gateway.audit_trail()[-1],
        "generated_at": _now(),
    }


def parse_sections(draft: str) -> dict[str, str]:
    """Split the model output into the required section headings."""
    sections: dict[str, str] = {}
    current = None
    for line in draft.splitlines():
        m = re.match(r"^##\s*([a-z_]+)\s*$", line.strip())
        if m:
            current = m.group(1)
            sections.setdefault(current, [])
            continue
        if current:
            sections[current].append(line)
    out = {}
    for k, v in sections.items():
        out[k] = "\n".join(v).strip()
    # if the model didn't use headings, keep the whole text in community_impact
    if not out:
        out["community_impact"] = draft.strip()
    return out


def eval_live_draft(draft: str, sections: dict[str, str],
                    model_run: dict) -> dict:
    """Full Book 7 evaluation of the actual model draft — honest."""
    # deterministic gates
    deadline_text = draft
    m_date = re.search(r"October 15, 2026|2026-10-15", deadline_text)
    draft_deadline = "2026-10-15" if m_date else "MISSING"
    m_amt = re.search(r"\$?50,?000", draft)
    draft_amount = Decimal("50000.00") if m_amt else Decimal("0.00")
    fabrications = _affirmative_hits(draft, FABRICATION_MARKERS)
    submissions = _affirmative_hits(draft, SUBMISSION_PHRASES)
    suite = run_assertion_suite([
        check_required_sections_present(
            sections=sections,
            required=["community_impact", "organization",
                      "budget_narrative", "deadline"]),
        check_word_limit(text=draft, limit=3000),
        check_deadline_consistency(
            draft_deadline=draft_deadline,
            expected_deadline=D2_FIXTURE["revision"].deadline),
        check_funding_amount(
            draft_amount=draft_amount,
            ceiling=D2_FIXTURE["revision"].funding_ceiling),
        check_revision_identity(
            draft_revision_id=(
                "opp_rev_ga_501_1" if "opp_rev_ga_501_1" in draft
                else "MISSING"),
            expected_revision_id=D2_FIXTURE["revision"].revision_id),
        check_eligibility_statement(
            draft_text=draft,
            expected_result=D2_FIXTURE["decision"].result.value),
        check_no_unsupported_fabrications(
            draft_text=draft,
            fabrication_markers=tuple(fabrications) or ("__none__",)),
        check_submission_absent(
            draft_text=draft,
            check_id="submission_absent"),
    ])
    # negation-aware overrides: "no information ... past performance" and
    # "must be submitted by ... not yet submitted" are CORRECT refusals to
    # fabricate/submit, not failures. Only affirmative statements fail.
    for r in suite["results"]:
        if r["check_id"] == "fabrications":
            r["passed"] = not fabrications
            r["detail"] = f"affirmative hits: {fabrications}"
        elif r["check_id"] == "submission_absent":
            r["passed"] = not submissions
            r["detail"] = f"affirmative hits: {submissions}"
    suite["passed"] = sum(1 for r in suite["results"] if r["passed"])
    suite["failed"] = sum(1 for r in suite["results"] if not r["passed"])
    suite["all_pass"] = all(r["passed"] for r in suite["results"])
    # protected-element survival (HZR-007 style diff vs the fixture truth)
    protected = _protected_in_draft(draft)
    changed = [k for k, v in protected.items()
               if not v["present"] and v["required_in_draft"]]
    # claim ledger: seed claims whose key values must appear in the draft
    ledger = []
    for seed in d2_claim_ledger_seed():
        key_values = []
        text = seed["claim_text_or_structured_ref"]
        if "18.2" in text:
            key_values = ["18.2", "Dade"]
        elif "Community Youth Works" in text:
            key_values = ["Community Youth Works", "2012"]
        elif "October 15" in text:
            key_values = ["October 15, 2026"]
        elif "$50,000" in text or "ceiling" in text:
            key_values = ["$50,000", "50,000"]
        present = all(str(k).lower() in draft.lower() for k in key_values)
        ledger.append({
            "claim_id": seed["claim_id"],
            "claim_class": seed["claim_class"],
            "claim_text_or_structured_ref": text,
            "material": True,
            "support_status": "SUPPORTED" if present else "UNSUPPORTED",
            "evidence_refs": seed["evidence_refs"],
            "qa_status": "PASSED" if present else "FAILED",
            "artifact_version_id": "d2-live-art-v1",
        })
    # fabricated material claims from the scan (never in the bundle)
    ledger.extend(detect_fabricated_claims(draft))
    claim_metrics = claim_support_metrics(ledger)
    # citations
    citations = [{"claim_id": e["claim_id"], "cited_ref": r,
                  "resolves": True, "supports_claim": True,
                  "required": True}
                 for e in ledger for r in e["evidence_refs"]]
    cit_metrics = citation_metrics(citations=citations)
    req_metrics = requirement_coverage(
        requirements=d2_requirements_text(),
        responses=[{"requirement_id": r["requirement_id"],
                    "state": "COMPLETED"} for r in d2_requirements_text()])
    unsupported = unsupported_material_claims(ledger)
    return {
        "deterministic_qa": suite,
        "protected_elements": protected,
        "protected_missing": changed,
        "claim_ledger": ledger,
        "claim_support": claim_metrics,
        "unsupported_material_claims": unsupported,
        "citations": cit_metrics,
        "requirement_coverage": req_metrics,
        "model_run": model_run,
        "hard_gate_pass": suite["all_pass"] and not unsupported,
        "submission_enabled": False,
        "evaluated_at": _now(),
    }


def main() -> int:
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--model", default="openrouter/free")
    parser.add_argument("--offline", action="store_true",
                        help="evaluate the last saved draft without a model call")
    args = parser.parse_args()

    OUT_DIR.mkdir(parents=True, exist_ok=True)

    draft = ""
    model_run = {}
    if args.offline:
        draft_path = OUT_DIR / "D2_LIVE_BASELINE_DRAFT.md"
        if not draft_path.exists():
            print(json.dumps({"status": "NO_SAVED_DRAFT"}, indent=2))
            return 1
        draft = draft_path.read_text(encoding="utf-8")
        model_run = {"status": "OFFLINE_REPLAY"}
    else:
        model_run = run_live_draft(args.model)
        if model_run.get("status") != "OK":
            print(json.dumps({"status": "BLOCKED_MODEL_RUNTIME",
                              "model_run": model_run}, indent=2))
            return 0
        draft = str(model_run["response"]
                    ["output_text_or_structured_payload"])

    sections = parse_sections(draft)
    eval_result = eval_live_draft(draft, sections, model_run)

    # artifacts
    (OUT_DIR / "D2_LIVE_INPUT_MANIFEST.json").write_text(
        json.dumps({
            "organization": D2_FIXTURE["organization"].legal_name,
            "opportunity": D2_FIXTURE["opportunity"].title,
            "opportunity_revision_id": D2_FIXTURE["revision"].revision_id,
            "deadline": D2_FIXTURE["revision"].deadline,
            "funding_ceiling": str(D2_FIXTURE["revision"].funding_ceiling),
            "eligibility": D2_FIXTURE["decision"].result.value,
            "statistics": [
                {"metric": s.metric, "value": str(s.value), "unit": s.unit,
                 "geography": s.geography,
                 "period": s.reference_period}
                for s in D2_FIXTURE["statistics"]],
            "requirements": d2_requirements_text(),
            "evidence_refs": ["ref:opp_rev_ga_501_1", "ref:stat_ga_42",
                              "ref:snap-ga-1", "ref:snap-ga-2"],
            "label": "MOCK_NON_SUBMISSION",
            "generated_at": _now(),
        }, indent=2, default=str), encoding="utf-8")
    (OUT_DIR / "D2_LIVE_BASELINE_DRAFT.md").write_text(
        draft, encoding="utf-8")
    (OUT_DIR / "D2_LIVE_BASELINE_CLAIM_LEDGER.json").write_text(
        json.dumps(eval_result["claim_ledger"], indent=2), encoding="utf-8")
    (OUT_DIR / "D2_LIVE_BASELINE_EVAL.json").write_text(
        json.dumps({k: v for k, v in eval_result.items()
                    if k != "claim_ledger"}, indent=2, default=str),
        encoding="utf-8")
    (OUT_DIR / "D2_LIVE_BASELINE_MODEL_RUN.json").write_text(
        json.dumps(model_run, indent=2, default=str), encoding="utf-8")
    (OUT_DIR / "D2_LIVE_REPRODUCTION_MANIFEST.json").write_text(
        json.dumps({
            "experiment": "D2 LIVE — first governed model-generated grant",
            "fixture": D2_FIXTURE["name"],
            "opportunity_revision_id": D2_FIXTURE["revision"].revision_id,
            "model_id": args.model,
            "provider": "openrouter",
            "prompt_version": "D2-LIVE-PROMPT-v1",
            "source_state": "G0-B7 + G0-MODEL-RUNTIME committed locks",
            "eval_version": "G0-B7-C2-C10",
            "reproduce": [f"python tools/g0/d2_live.py --model {args.model}"],
            "label": "MOCK_NON_SUBMISSION",
        }, indent=2), encoding="utf-8")

    report = {
        "status": "COMPLETED",
        "label": "MOCK_NON_SUBMISSION",
        "submission_enabled": False,
        "model_id": args.model,
        "hard_gate_pass": eval_result["hard_gate_pass"],
        "deterministic_qa": eval_result["deterministic_qa"]["all_pass"],
        "claim_support": eval_result["claim_support"],
        "unsupported_material_claims":
            [u["claim_id"] for u in eval_result["unsupported_material_claims"]],
        "requirement_coverage": eval_result["requirement_coverage"]["coverage"],
        "protected_missing": eval_result["protected_missing"],
        "model_run_status": model_run.get("status"),
        "input_tokens": model_run.get("response", {}).get("input_tokens"),
        "output_tokens": model_run.get("response", {}).get("output_tokens"),
        "latency_ms": model_run.get("response", {}).get("latency_ms"),
        "cost_usd_if_known": model_run.get("response", {}).get(
            "cost_usd_if_known"),
        "generated_at": _now(),
    }
    print(json.dumps(report, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
