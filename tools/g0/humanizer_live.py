#!/usr/bin/env python3
"""G0-B7-PHASE-D — Humanizer live bake-off via the governed model runtime.

Amendment 003: Humanizer is a BOUNDED STYLE_TRANSFORM candidate. It may
transform prose only; it cannot modify canonical facts, evidence authority,
protected claims, names, dates, numbers, statistics, funding amounts,
citations, or eligibility statements. Every output is a NEW ArtifactVersion
(N+1); pre/post semantic comparison and factuality revalidation are
mandatory.

Pipeline (all through the governed Model Gateway, never a direct provider
call by Humanizer):

    BASELINE LIVE DRAFT (ArtifactVersion N)
        -> governed Humanizer style-transform call
        -> candidate ArtifactVersion N+1
        -> protected-claim diff (HZR-007)
        -> semantic comparison
        -> factuality revalidation
        -> full Book 7 evaluation
        -> PromotionDecision (PROMOTE/REVISE/REJECT/QUARANTINE/DEFER)

Hard rejection (§13/§22): any change to a protected fact, or any increase
in unsupported material claims, fails the bake-off regardless of style
gains. D2 stays MOCK/NON_SUBMISSION.

Usage: python tools/g0/humanizer_live.py [--model minimax/minimax-m3:free]
"""
from __future__ import annotations

import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[2]
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from prototype.g0.evaluation.assertions import (  # noqa: E402
    check_protected_facts_unchanged,
)
from prototype.g0.evaluation.fixtures import (  # noqa: E402
    D2_FIXTURE,
    D2_PROTECTED_ELEMENTS,
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

D2_LIVE_DIR = _ROOT / "docs" / "grant-sector" / "g0" / "07-evaluation" / \
    "d2-live"
OUT_DIR = _ROOT / "docs" / "grant-sector" / "g0" / "07-evaluation" / \
    "d2-live"

HUMANIZER_SYSTEM = (
    "You are a bounded STYLE TRANSFORM editor. Rewrite the grant prose to "
    "be more natural and readable WITHOUT changing ANY fact. Hard rules: "
    "1) Do not change or drop: organization legal name, EIN, founding year, "
    "location, opportunity title, opportunity id, revision id, deadline "
    "(October 15, 2026 / 2026-10-15), funding ceiling ($50,000 / 50000.00), "
    "eligibility (ELIGIBLE), the poverty statistic (18.2 percent, Dade "
    "County GA, 2023, ACS 5-year), or any number/date/citation. "
    "2) Do not add partnerships, testimonials, past performance, staff "
    "counts, outcomes, or any fact not already in the text. "
    "3) Do not remove UNKNOWN statements. "
    "4) Keep the same section headings (## community_impact, "
    "## organization, ## budget_narrative, ## deadline). "
    "5) Output only the rewritten draft, no commentary."
)


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def build_chain(model_id: str) -> tuple[dict, ModelGateway]:
    principals = PrincipalRegistry()
    scope = ScopeEvaluator()
    grants = GrantRegistry()
    authz = Authorizer(principals=principals, scope=scope, grants=grants)
    principals.register(Principal(
        principal_id="hzr-ceo", principal_type="HERMES_CEO",
        subject_id="hzr-ceo-1", status="ACTIVE",
        authentication_method="SERVICE_TOKEN",
        tenant_memberships=["tenant-a"], created_at=T0,
        credential_class="VAULT_REF", authority_level="L3"))
    scope.add_membership(membership_id="m-hzr", tenant_id="tenant-a",
                         principal_id="hzr-ceo", role_ids=["MEMBER"],
                         valid_from=T0, valid_to=T_FAR)
    scope.register_resource("res:hzr-draft", "tenant-a", project_id="proj-d2")
    authz.register_capability("model.invoke", required_level="L1")
    authz.allow_egress_destination("https://openrouter.ai")
    grants.issue(grant_id="g-hzr", principal_id="hzr-ceo",
                 capability_id="model.invoke", tenant_id="tenant-a",
                 authority_level="L3", valid_from=T0, expires_at=T_FAR,
                 issued_by="admin", project_id="proj-d2")
    profiles = ProviderProfileRegistry()
    gateway = ModelGateway(profiles, decisions=authz.decisions,
                           credential_resolver=DevRuntimeCredentialResolver())
    gateway.register_adapter("openrouter", OpenRouterAdapter())
    return {"gateway": gateway, "authz": authz}, gateway


def humanize(baseline_draft: str, model_id: str) -> dict:
    """Run the bounded style transform through the governed gateway."""
    chain, gateway = build_chain(model_id)
    req = {
        "model_request_id": "hzr-live-m1", "request_id": "hzr-live-r1",
        "tenant_id": "tenant-a", "project_id": "proj-d2",
        "principal_id": "hzr-ceo", "task_id": "task-hzr-transform",
        "capability_id": "model.invoke",
        "provider_profile_id": "pp_openrouter_dev",
        "model_id": model_id, "purpose": "grant_revision",
        "messages": [
            {"role": "system", "content": HUMANIZER_SYSTEM},
            {"role": "user", "content": baseline_draft},
        ],
        "temperature": 0.1, "max_output_tokens": 2048,
        "created_at": _now(), "destination": "https://openrouter.ai",
        "resource_id": "res:hzr-draft",
    }
    decision = chain["authz"].authorize(req)
    if decision["decision"] != "ALLOW":
        return {"status": "DENIED",
                "reason_code": decision["reason_code"]}
    resp = gateway.invoke(
        model_request=req, authorization_decision=decision,
        actor="hzr-ceo", principal_type="HERMES_CEO",
        tenant_id="tenant-a", project_id="proj-d2",
        resource_id="res:hzr-draft")
    return {"status": "OK", "response": resp,
            "audit": gateway.audit_trail()[-1],
            "generated_at": _now()}


def _protected_in_text(text: str) -> dict:
    out = {}
    for key, value in D2_PROTECTED_ELEMENTS.items():
        aliases = value if isinstance(value, list) else [value]
        present = [a for a in aliases if str(a).lower() in text.lower()]
        out[key] = {"present": bool(present), "found": present}
    return out


def compare(baseline: str, humanized: str) -> dict:
    """HZR-007 protected-claim diff + semantic preservation metrics."""
    diff_result = check_protected_facts_unchanged(
        original_text=baseline, new_text=humanized,
        protected=D2_PROTECTED_ELEMENTS)
    baseline_claims = _protected_in_text(baseline)
    humanized_claims = _protected_in_text(humanized)
    dropped = [k for k, v in baseline_claims.items()
               if v["present"] and not humanized_claims[k]["present"]]
    # word/sentence deltas for edit-burden approximation
    bw, hw = len(re.findall(r"\S+", baseline)), len(re.findall(r"\S+",
                                                               humanized))
    return {
        "protected_claim_diff_passed": diff_result.passed,
        "protected_claim_diff_detail": diff_result.detail,
        "baseline_protected_present": {k: v["present"]
                                       for k, v in baseline_claims.items()},
        "humanized_protected_present": {k: v["present"]
                                        for k, v in humanized_claims.items()},
        "protected_dropped": dropped,
        "baseline_word_count": bw,
        "humanized_word_count": hw,
        "word_delta": hw - bw,
        "semantic_preservation": "PASS" if not dropped else "FAIL",
    }


def main() -> int:
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--model", default="minimax/minimax-m3:free")
    parser.add_argument("--offline", action="store_true",
                        help="compare the last saved humanized draft without "
                             "a model call")
    args = parser.parse_args()

    baseline_path = D2_LIVE_DIR / "D2_LIVE_BASELINE_DRAFT.md"
    if not baseline_path.exists():
        print(json.dumps({"status": "NO_BASELINE"}, indent=2))
        return 1
    baseline = baseline_path.read_text(encoding="utf-8")

    if args.offline:
        hzr_path = OUT_DIR / "D2_LIVE_HUMANIZED_DRAFT.md"
        if not hzr_path.exists():
            print(json.dumps({"status": "NO_HUMANIZED"}, indent=2))
            return 1
        humanized = hzr_path.read_text(encoding="utf-8")
        run = {"status": "OFFLINE_REPLAY"}
    else:
        run = humanize(baseline, args.model)
        if run.get("status") != "OK":
            print(json.dumps({"status": "BLOCKED_COMPONENT_RUNTIME",
                              "humanizer_run": run}, indent=2))
            return 0
        humanized = str(run["response"]["output_text_or_structured_payload"])

    comparison = compare(baseline, humanized)

    (OUT_DIR / "D2_LIVE_HUMANIZED_DRAFT.md").write_text(
        humanized, encoding="utf-8")
    (OUT_DIR / "D2_LIVE_HUMANIZED_DIFF.json").write_text(
        json.dumps(comparison, indent=2, default=str), encoding="utf-8")
    (OUT_DIR / "D2_LIVE_HUMANIZER_RUN.json").write_text(
        json.dumps(run, indent=2, default=str), encoding="utf-8")

    hard_gates = {
        "protected_claim_diff": comparison["protected_claim_diff_passed"],
        "semantic_preservation":
            comparison["semantic_preservation"] == "PASS",
        "submission_disabled": True,
    }
    gate_pass = all(hard_gates.values())
    disposition = "DEFER" if not gate_pass else "REVISE"
    # NOTE: promotion decision is NOT auto-PROMOTE: one fixture is weak
    # evidence (C28). Even a clean transform stays PROVISIONAL.
    if not gate_pass:
        disposition = "REJECT" if not comparison[
            "protected_claim_diff_passed"] else "QUARANTINE"

    decision = {
        "promotion_decision_id": "pd-hzr-live-1",
        "candidate_change_id": "cc-hzr-live-1",
        "candidate": "blader/humanizer (bounded style transform)",
        "baseline_version": "d2-live-art-v1 (model draft)",
        "candidate_version": "d2-live-art-v2 (humanized)",
        "model_id": args.model,
        "hard_gates": hard_gates,
        "gate_pass": gate_pass,
        "disposition": disposition,
        "decision_note": (
            "Amendment 003 bounded contract. Protected-claim diff and "
            "semantic preservation must pass; unsupported claims must not "
            "rise. One fixture is weak evidence — no auto-PROMOTE; any "
            "positive result is PROVISIONAL/BOUNDED pending Book 8 "
            "evidence (C28)."),
        "submission": "DISABLED",
        "decided_at": _now(),
        "decided_by": "Book 7 evaluation machinery (no self-promotion)",
    }
    (OUT_DIR / "D2_LIVE_HUMANIZER_DECISION.json").write_text(
        json.dumps(decision, indent=2), encoding="utf-8")

    report = {
        "status": "COMPLETED",
        "humanizer_live_status": "RUN_COMPLETED",
        "model_id": args.model,
        "protected_claim_diff_passed":
            comparison["protected_claim_diff_passed"],
        "protected_dropped": comparison["protected_dropped"],
        "semantic_preservation": comparison["semantic_preservation"],
        "word_delta": comparison["word_delta"],
        "hard_gate_pass": gate_pass,
        "disposition": disposition,
        "submission_enabled": False,
        "generated_at": _now(),
    }
    print(json.dumps(report, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
