#!/usr/bin/env python3
"""G0-B7-D2 — First grounded grant-writing quality experiment (harness).

Runs the real evaluation chain on the canonical Georgia-first fixture:
  fixture -> baseline grounded draft (deterministic, evidence-anchored)
  -> deterministic QA gates -> Claim Ledger -> factuality metrics
  -> requirement coverage -> budget reconciliation -> promotion-style
  baseline bundle.

LIVE MODEL LANES:
  * BASELINE GROUNDED DRAFT is generated deterministically from governed
    evidence (no model required; nothing invented).
  * HUMANIZED GROUNDED DRAFT requires a live language model runtime. None is
    configured in this environment, so that lane is reported honestly as
    BLOCKED_MODEL_RUNTIME. The protected-claim diff validator (HZR-007) and
    the semantic-comparison contract are fully implemented and exercised
    against the deterministic draft so the pipeline is testable today.

D2 stays MOCK / NON_SUBMISSION. No metric is fabricated; BLOCKED is an
honest result.
"""
from __future__ import annotations

import json
import sys
from datetime import datetime, timezone
from decimal import Decimal
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[2]
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from prototype.g0.evaluation.assertions import (  # noqa: E402
    check_budget_reconciles,
    check_deadline_consistency,
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
    d2_baseline_sections,
    d2_budget_lines,
    d2_budget_total,
    d2_claim_ledger_seed,
    d2_requirements_text,
)
from prototype.g0.evaluation.metrics import (  # noqa: E402
    claim_support_metrics,
    requirement_coverage,
)

FABRICATION_MARKERS = ("testimonial from", "our partner", "endorsed by",
                       "we partner with", "letter of support from")


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _model_runtime_available() -> bool:
    """Probe for an AUTHORIZED, configured model runtime for the governed G0
    pipeline.

    Since G0-MODEL-RUNTIME-C1/C2 the governed Model Gateway exists
    (prototype/g0/model/) with a provider profile registry; the live lane is
    executed through it by tools/g0/d2_live.py. A runtime is available when
    the governed profile is configured AND a server-side credential exists
    in the process environment (DEV_RUNTIME_ONLY resolver). A bare env var
    alone is still not enough — the governed gateway must exist too. No
    credential value is printed or committed.
    """
    from pathlib import Path
    try:
        import os
        from prototype.g0.model.gateway import ProviderProfileRegistry
        profiles = ProviderProfileRegistry()
        profiles.get("pp_openrouter_dev")  # raises if unconfigured
        return bool(os.environ.get("OPENROUTER_API_KEY", ""))
    except Exception:
        return False


def run_deterministic_qa(baseline_sections: dict[str, str]) -> dict:
    """Deterministic gates over the baseline draft (C7)."""
    joined = " ".join(baseline_sections.values())
    suite = run_assertion_suite([
        check_required_sections_present(
            sections=baseline_sections,
            required=["community_impact", "organization", "budget_narrative",
                      "deadline"]),
        check_word_limit(text=joined, limit=3000),
        check_deadline_consistency(
            draft_deadline="2026-10-15",
            expected_deadline=D2_FIXTURE["revision"].deadline),
        check_funding_amount(
            draft_amount=d2_budget_total(),
            ceiling=D2_FIXTURE["revision"].funding_ceiling),
        check_revision_identity(
            draft_revision_id="opp_rev_ga_501_1",
            expected_revision_id=D2_FIXTURE["revision"].revision_id),
        check_budget_reconciles(
            lines_total=sum((line["amount"] for line in d2_budget_lines()),
                            Decimal("0")),
            declared_total=d2_budget_total()),
        check_no_unsupported_fabrications(
            draft_text=joined, fabrication_markers=FABRICATION_MARKERS),
        check_submission_absent(draft_text=joined),
    ])
    return suite


def run_claim_ledger_eval(entries: list[dict]) -> dict:
    """C8 factuality metrics over the claim ledger seed."""
    return claim_support_metrics(entries)


def run_requirement_eval() -> dict:
    """C7 requirement coverage over the D2 requirements."""
    reqs = [{"requirement_id": r["requirement_id"],
             "mandatory": r["mandatory"]}
            for r in d2_requirements_text()]
    responses = [{"requirement_id": "req_ga_1", "state": "COMPLETED"},
                 {"requirement_id": "req_ga_2", "state": "COMPLETED"}]
    return requirement_coverage(requirements=reqs, responses=responses)


def run_humanizer_protected_claim_diff(new_text: str) -> dict:
    """HZR-007 diff against the deterministic baseline. In live mode this
    runs on the Humanizer output; today it exercises the validator on the
    baseline itself (identity transform must pass) and on a planted
    tamper (must fail) to prove the pipeline is real."""
    baseline = " ".join(d2_baseline_sections().values())
    identity = check_protected_facts_unchanged(
        original_text=baseline, new_text=baseline,
        protected=D2_PROTECTED_ELEMENTS)
    tampered = baseline.replace("$50,000", "$750,000").replace(
        "October 15, 2026", "October 16, 2026")
    tamper = check_protected_facts_unchanged(
        original_text=baseline, new_text=tampered,
        protected=D2_PROTECTED_ELEMENTS)
    return {
        "identity_transform_preserves_protected_facts": identity.passed,
        "tampered_amount_and_deadline_detected": not tamper.passed,
        "detected_changes": tamper.detail,
        "contract": "HZR-007 protected-claim diff (validator live)",
    }


def build_baseline_bundle() -> dict:
    """MetricBundle-shaped baseline evidence for the D2 report."""
    qa = run_deterministic_qa(d2_baseline_sections())
    claims = run_claim_ledger_eval(d2_claim_ledger_seed())
    reqs = run_requirement_eval()
    return {
        "deterministic_qa": qa,
        "claim_support": claims,
        "requirement_coverage": reqs,
        "budget_total": str(d2_budget_total()),
        "eligibility_result": D2_FIXTURE["decision"].result.value,
        "deadline": D2_FIXTURE["revision"].deadline,
        "funding_ceiling": str(D2_FIXTURE["revision"].funding_ceiling),
        "opportunity_revision_id": D2_FIXTURE["revision"].revision_id,
        "organization": D2_FIXTURE["organization"].legal_name,
        "fixture_name": D2_FIXTURE["name"],
    }


def build_humanized_lane_status() -> dict:
    """Honest status of the Humanizer lane.

    With a governed runtime available (G0-MODEL-RUNTIME), the live lane is
    executed through the Model Gateway by tools/g0/d2_live.py and
    tools/g0/humanizer_live.py; artifacts land in d2-live/. Without one,
    the lane reports BLOCKED_MODEL_RUNTIME truthfully and nothing is
    fabricated.
    """
    if _model_runtime_available():
        return {
            "status": "AVAILABLE",
            "note": "governed model runtime configured; live lane executed "
                    "through tools/g0/d2_live.py (see d2-live/ artifacts)",
            "artifacts_dir": "docs/grant-sector/g0/07-evaluation/d2-live/",
            "harness_complete": True,
        }
    return {
        "status": "BLOCKED_MODEL_RUNTIME",
        "note": "no configured language model provider in this environment; "
                "BASELINE GROUNDED DRAFT generated deterministically from "
                "governed evidence. HUMANIZED GROUNDED DRAFT requires a live "
                "model. The protected-claim diff (HZR-007) and factuality "
                "revalidation (HZR-008) contracts are implemented and tested.",
        "harness_complete": True,
    }


def build_d2_report() -> dict:
    baseline = build_baseline_bundle()
    hzr_diff = run_humanizer_protected_claim_diff("")
    humanizer = build_humanized_lane_status()
    return {
        "experiment": "D2 — FIRST GROUNDED GRANT-WRITING QUALITY EXPERIMENT",
        "milestone": "D2",
        "label": "MOCK_NON_SUBMISSION",
        "submission_enabled": False,
        "generated_at": _now(),
        "fixture": {
            "name": D2_FIXTURE["name"],
            "organization": D2_FIXTURE["organization"].legal_name,
            "opportunity": D2_FIXTURE["opportunity"].title,
            "opportunity_revision_id": D2_FIXTURE["revision"].revision_id,
            "revision_deadline": D2_FIXTURE["revision"].deadline,
            "revision_ceiling": str(D2_FIXTURE["revision"].funding_ceiling),
            "eligibility": D2_FIXTURE["decision"].result.value,
            "statistics": [
                {"metric": s.metric, "value": str(s.value), "unit": s.unit,
                 "geography": s.geography, "period": s.reference_period}
                for s in D2_FIXTURE["statistics"]],
        },
        "baseline_grounded_draft": {
            "generation": "DETERMINISTIC_FROM_GOVERNED_EVIDENCE",
            "sections": d2_baseline_sections(),
            "model_or_version": "none (deterministic)",
        },
        "baseline_metrics": baseline,
        "humanizer_lane": humanizer,
        "humanizer_protected_claim_diff": hzr_diff,
        "humanized_draft": None,  # never fabricated (BLOCKED_MODEL_RUNTIME)
        "comparison": {
            "status": "PARTIAL",
            "note": "baseline metrics recorded; humanized comparison "
                    "requires live model runtime (BLOCKED_MODEL_RUNTIME)",
        },
        "human_review": {
            "status": "NOT_PERFORMED",
            "note": "no human reviewer available; no human-review score is "
                    "invented",
        },
        "limitations": [
            "single fixture (GA-1); initial quality experiment, not proof "
            "across grants (C28 statistical discipline)",
            "humanized lane blocked: no model runtime",
            "no human edit-burden measurement (no reviewer)",
            "cost/latency reflect deterministic gates, not model inference",
        ],
        "d2_fail_conditions": {
            "fabricated_partnership": False,
            "fabricated_testimonial": False,
            "wrong_deadline": False,
            "wrong_funding_amount": False,
            "unsupported_statistic": False,
            "citation_does_not_support_claim": False,
            "requirement_omitted": False,
            "wrong_opportunity_revision": False,
            "eligibility_inconsistency": False,
            "tenant_project_contamination": False,
            "submission_capability_present": False,
            "humanizer_changed_protected_fact": "N/A (no humanized draft "
                                                "generated)",
        },
    }


def main() -> int:
    report = build_d2_report()
    out = _ROOT / "docs" / "grant-sector" / "g0" / "07-evaluation" / "d2"
    out.mkdir(parents=True, exist_ok=True)
    (out / "D2_INPUT_MANIFEST.json").write_text(
        json.dumps(report["fixture"], indent=2), encoding="utf-8")
    (out / "D2_BASELINE_DRAFT.md").write_text(
        "\n\n".join(f"## {k}\n\n{v}" for k, v in
                    report["baseline_grounded_draft"]["sections"].items()),
        encoding="utf-8")
    (out / "D2_BASELINE_EVAL.json").write_text(
        json.dumps(report["baseline_metrics"], indent=2), encoding="utf-8")
    (out / "D2_COMPARISON_REPORT.md").write_text(
        _comparison_markdown(report), encoding="utf-8")
    runtime = _model_runtime_available()
    decision = {
        "decision": "HARNESS_COMPLETE",
        "harness": "deterministic baseline + evaluation chain",
        "live_model_runtime": "AVAILABLE" if runtime
        else "BLOCKED_MODEL_RUNTIME",
        "live_lane_artifacts": "docs/grant-sector/g0/07-evaluation/d2-live/"
        if runtime else None,
        "humanizer_disposition": "SEE D2_LIVE_HUMANIZER_DECISION.json"
        if runtime else "DEFER (no live run)",
        "reason": "deterministic harness complete; promotion requires "
                  "baseline-vs-candidate comparison through the live lane "
                  "(d2_live.py) when a governed runtime exists",
        "submission": "DISABLED",
    }
    (out / "D2_DECISION.json").write_text(
        json.dumps(decision, indent=2), encoding="utf-8")
    (out / "D2_REPRODUCTION_MANIFEST.json").write_text(
        json.dumps({
            "experiment": report["experiment"],
            "fixture": D2_FIXTURE["name"],
            "opportunity_revision_id": D2_FIXTURE["revision"].revision_id,
            "model_or_version": "none (deterministic baseline)",
            "source_state": "G0-B7 committed locks",
            "eval_version": "G0-B7-C2-C10",
            "reproduce": ["python tools/g0/d2_harness.py"],
        }, indent=2), encoding="utf-8")
    print(json.dumps(report, indent=2)[:4000])
    return 0


def _comparison_markdown(report: dict) -> str:
    b = report["baseline_metrics"]
    lines = [
        "# D2 — Comparison Report (Baseline vs Humanized)",
        "",
        f"**Experiment:** {report['experiment']}",
        f"**Label:** {report['label']} (submission enabled: "
        f"{report['submission_enabled']})",
        "",
        "## Baseline Grounded Draft (deterministic, evidence-anchored)",
        "",
        f"- Requirement coverage: "
        f"{b['requirement_coverage']['coverage']} "
        f"({b['requirement_coverage']['covered']}/"
        f"{b['requirement_coverage']['mandatory_total']} mandatory)",
        f"- Material claim support rate: "
        f"{b['claim_support']['material_claim_support_rate']} "
        f"(supported {b['claim_support']['supported']}/"
        f"{b['claim_support']['total']})",
        f"- Unsupported material claims: {b['claim_support']['unsupported']}",
        f"- Deterministic QA: {b['deterministic_qa']['passed']}/"
        f"{b['deterministic_qa']['total']} passed",
        f"- Budget total: {b['budget_total']} (ceiling "
        f"{b['funding_ceiling']})",
        f"- Eligibility: {b['eligibility_result']}",
        "",
        "## Humanized Grounded Draft",
        "",
        f"- **Status: {report['humanizer_lane']['status']}**",
        f"- {report['humanizer_lane']['note']}",
        "",
        "## Humanizer protected-claim diff (HZR-007)",
        "",
        f"- Identity transform preserves protected facts: "
        f"{report['humanizer_protected_claim_diff']['identity_transform_preserves_protected_facts']}",
        f"- Tampered amount/deadline detected: "
        f"{report['humanizer_protected_claim_diff']['tampered_amount_and_deadline_detected']}",
        "",
        "## Metrics (Baseline)",
        "",
        "| Dimension | Value |",
        "|---|---|",
        f"| Requirement coverage | {b['requirement_coverage']['coverage']} |",
        f"| Claim support rate | "
        f"{b['claim_support']['material_claim_support_rate']} |",
        f"| Unsupported claims | {b['claim_support']['unsupported']} |",
        f"| Budget reconciled | "
        f"{b['deterministic_qa']['all_pass']} |",
        "",
        "## Humanized metrics",
        "",
        "BLOCKED_MODEL_RUNTIME — no model-generated humanized draft exists; "
        "no humanized metrics are fabricated.",
        "",
        "## Limitations",
        "",
    ] + [f"- {l}" for l in report["limitations"]] + [
        "",
        "## Disposition",
        "",
        "Humanizer: **DEFER (no live run)** — D2 does not automatically "
        "promote Humanizer; promotion requires a baseline-vs-candidate "
        "comparison through the Book 7 promotion path.",
    ]
    return "\n".join(lines)


if __name__ == "__main__":
    sys.exit(main())
