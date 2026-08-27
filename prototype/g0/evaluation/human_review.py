"""G0-B7-C23 — Human review protocol.

Human review is targeted, not ceremonial. Reviewer records are attributable;
inter-reviewer disagreement is data, not something to hide; the reviewer
receives a structured review packet, not unbounded raw logs.
"""
from __future__ import annotations

from datetime import datetime, timezone

REVIEW_DECISIONS = ("APPROVE", "REQUEST_EDITS", "REJECT", "CONFIRM_FACT",
                    "RESOLVE_AMBIGUITY")

REQUIRED_WHEN = (
    "rubric_dimension_materially_subjective_and_high_impact",
    "candidate_changes_client_facing_grant_strategy",
    "evaluation_disagreement_unresolved",
    "security_or_policy_boundary_changes",
    "production_skill_promotion_risk_exceeds_threshold",
    "gold_label_creation_requires_expertise",
)


class HumanReviewError(ValueError):
    """Raised when a review record violates the protocol."""


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def human_review_required(*, reason: str) -> bool:
    if reason in REQUIRED_WHEN:
        return True
    # security/policy or high-impact client-facing reasons are mandatory
    if "security" in reason or "client" in reason:
        return True
    return False


def record_review(*, reviewer_identity: str, reviewer_role: str,
                  subject_ref: str, decision: str, reason_codes: list[str],
                  rubric_ref: str | None = None, scores: dict | None = None,
                  comments: str = "", conflict_of_interest: str = "") -> dict:
    """Attributable review record. No anonymous consequential review."""
    if not reviewer_identity or not reviewer_role:
        raise HumanReviewError("reviewer identity and role required")
    if decision not in REVIEW_DECISIONS:
        raise HumanReviewError(f"invalid decision {decision!r}")
    return {
        "review_id": f"hr-{abs(hash((reviewer_identity, subject_ref))) % 10**6}",
        "reviewer_identity": reviewer_identity,
        "reviewer_role": reviewer_role,
        "subject_ref": subject_ref,
        "rubric_ref": rubric_ref,
        "scores": scores or {},
        "decision": decision,
        "reason_codes": list(reason_codes),
        "comments": comments,
        "conflict_of_interest": conflict_of_interest,
        "reviewed_at": _now(),
    }


def review_packet(*, subject_ref: str, opportunity_revision_id: str,
                  eligibility_summary: dict, draft_artifact_ref: str,
                  requirement_coverage: dict, claim_ledger_issues: list[str],
                  budget_validation: dict, uncertainties: list[str],
                  qa_eval_results: dict,
                  confirmation_items: list[str]) -> dict:
    """Structured review packet — bounded, attributable, no raw logs."""
    return {
        "subject_ref": subject_ref,
        "opportunity_revision_id": opportunity_revision_id,
        "eligibility_summary": eligibility_summary,
        "draft_artifact_ref": draft_artifact_ref,
        "requirement_coverage": requirement_coverage,
        "claim_ledger_issues": list(claim_ledger_issues),
        "budget_validation": budget_validation,
        "uncertainties": list(uncertainties),
        "qa_eval_results": qa_eval_results,
        "confirmation_items": list(confirmation_items),
    }


def disagreement_is_data(*, reviews: list[dict]) -> dict:
    """C23: inter-reviewer disagreement is recorded, not hidden."""
    if len(reviews) < 2:
        return {"disagreement": False, "note": "fewer than 2 reviews"}
    decisions = [r["decision"] for r in reviews]
    agree = len(set(decisions)) == 1
    return {"disagreement": not agree, "decisions": decisions,
            "note": "inter-reviewer disagreement is data, not something "
                    "to hide" if not agree else ""}
