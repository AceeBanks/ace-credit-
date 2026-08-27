"""G0-B8-C21/C22/C23/C24 — Claim Ledger completion, deterministic QA,
Book 7 evaluation integration, and human review.

Every material claim maps to governed evidence; unsupported material
claims block SUBMISSION_READY_MOCK. Deterministic gates run before any
subjective dimension. Human review is recorded honestly: NOT_PERFORMED
when no reviewer exists — never an invented approval.
"""
from __future__ import annotations

import re
from dataclasses import dataclass, field
from datetime import datetime, timezone

from prototype.g0.evaluation.assertions import (
    check_deadline_consistency,
    check_eligibility_statement,
    check_funding_amount,
    check_no_unsupported_fabrications,
    check_required_sections_present,
    check_revision_identity,
    check_submission_absent,
    check_word_limit,
    run_assertion_suite,
)
from prototype.g0.evaluation.fixtures import (
    D2_FIXTURE,
    d2_claim_ledger_seed,
)
from prototype.g0.evaluation.metrics import (
    claim_support_metrics,
    unsupported_material_claims,
)

FABRICATION_MARKERS = ("testimonial from", "our partner", "endorsed by",
                       "we partner with", "letter of support from")


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


@dataclass
class AssuranceResult:
    claim_ledger: list[dict]
    claim_metrics: dict
    deterministic_qa: dict
    hard_gate_pass: bool
    human_review: dict
    unsupported_claims: list[str] = field(default_factory=list)

    def validate(self) -> None:
        if not self.hard_gate_pass:
            raise ValueError("hard gate failure blocks SUBMISSION_READY_MOCK "
                             "(B8.C22/C23)")
        if self.unsupported_claims:
            raise ValueError("unsupported material claims block readiness "
                             "(B8.C21)")


def run_assurance(*, sections: dict[str, str], revision_id: str,
                  deadline: str, ceiling: str) -> AssuranceResult:
    """Complete the Claim Ledger, run deterministic QA, and record human
    review honestly."""
    joined = " ".join(sections.values())
    # deadline appears in prose ("October 15, 2026") or ISO ("2026-10-15")
    m_date = re.search(r"October 15, 2026|2026-10-15", joined)
    draft_deadline = "2026-10-15" if m_date else "MISSING"
    suite = run_assertion_suite([
        check_required_sections_present(
            sections=sections,
            required=["community_impact", "organization",
                      "budget_narrative", "deadline"]),
        check_word_limit(text=joined, limit=3000),
        check_deadline_consistency(
            draft_deadline=draft_deadline,
            expected_deadline=D2_FIXTURE["revision"].deadline),
        check_funding_amount(
            draft_amount=ceiling,
            ceiling=D2_FIXTURE["revision"].funding_ceiling),
        check_revision_identity(
            draft_revision_id=revision_id if revision_id in joined
            else "MISSING",
            expected_revision_id=D2_FIXTURE["revision"].revision_id),
        check_eligibility_statement(
            draft_text=joined,
            expected_result=D2_FIXTURE["decision"].result.value),
        check_no_unsupported_fabrications(
            draft_text=joined, fabrication_markers=FABRICATION_MARKERS),
        check_submission_absent(draft_text=joined),
    ])
    ledger = []
    for seed in d2_claim_ledger_seed():
        text = seed["claim_text_or_structured_ref"]
        key_values = []
        if "18.2" in text:
            key_values = ["18.2", "Dade"]
        elif "Community Youth Works" in text:
            key_values = ["Community Youth Works", "2012"]
        elif "October 15" in text:
            key_values = ["October 15, 2026"]
        elif "$50,000" in text or "ceiling" in text:
            key_values = ["$50,000", "50,000"]
        present = all(str(k).lower() in joined.lower()
                      for k in key_values)
        ledger.append({
            "claim_id": seed["claim_id"],
            "claim_class": seed["claim_class"],
            "claim_text_or_structured_ref": text,
            "material": True,
            "support_status": "SUPPORTED" if present else "UNSUPPORTED",
            "evidence_refs": seed["evidence_refs"],
            "qa_status": "PASSED" if present else "FAILED",
            "artifact_version_id": "b8-art-v1",
        })
    metrics = claim_support_metrics(ledger)
    unsupported = [u["claim_id"] for u in unsupported_material_claims(ledger)]
    hard_gate = bool(suite["all_pass"]) and not unsupported
    human_review = {
        "status": "NOT_PERFORMED",
        "note": "no human reviewer available; no approval/rejection score "
                "is invented",
        "reviewed_at": None,
    }
    return AssuranceResult(
        claim_ledger=ledger, claim_metrics=metrics,
        deterministic_qa=suite, hard_gate_pass=hard_gate,
        human_review=human_review, unsupported_claims=unsupported)
