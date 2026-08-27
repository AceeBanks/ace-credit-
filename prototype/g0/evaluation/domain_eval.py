"""G0-B7-C9/C10 — Eligibility, match & research evaluation.

Eligibility is rule/classification evaluation, not prose grading: hard-rule
evaluation accuracy, unknown handling, false-eligible/false-ineligible
rates, revision sensitivity. Matching is separate from hard eligibility and
can never override it. Research evaluation measures evidence grounding and
limitation disclosure (Book 5 FIND contracts).
"""
from __future__ import annotations

from dataclasses import dataclass


@dataclass
class EligibilityEvalResult:
    """Confusion-matrix-style eligibility accuracy."""
    total: int
    correct: int
    false_eligible: int = 0    # declared eligible when hard rule fails
    false_ineligible: int = 0  # declared ineligible when actually eligible
    unknown_handled: int = 0   # correctly surfaced as UNKNOWN/CONDITIONAL

    @property
    def accuracy(self) -> float:
        return round(self.correct / self.total, 4) if self.total else 1.0

    def to_dict(self) -> dict:
        return {
            "accuracy": self.accuracy,
            "correct": self.correct,
            "total": self.total,
            "false_eligible": self.false_eligible,
            "false_ineligible": self.false_ineligible,
            "unknown_handled": self.unknown_handled,
        }


def evaluate_eligibility_cases(cases: list[dict]) -> EligibilityEvalResult:
    """cases: {"expected": str, "predicted": str} where expected/predicted ∈
    ELIGIBLE/INELIGIBLE/CONDITIONAL/UNKNOWN."""
    result = EligibilityEvalResult(total=len(cases), correct=0)
    for case in cases:
        exp, pred = case["expected"], case["predicted"]
        if exp == pred:
            result.correct += 1
        if exp != "INELIGIBLE" and pred == "INELIGIBLE":
            result.false_ineligible += 1
        if exp == "INELIGIBLE" and pred == "ELIGIBLE":
            result.false_eligible += 1
        if exp in ("UNKNOWN", "CONDITIONAL") and pred == exp:
            result.unknown_handled += 1
    return result


def match_never_overrides_eligibility(*, match_score: float,
                                      eligibility: str) -> dict:
    """C9: hard eligibility dominates ranking. Ineligible can never be
    promoted by match score, however high."""
    if eligibility == "INELIGIBLE":
        return {"allowed": False, "reason": "ineligible cannot rank first "
                "(C9 hard gate)", "effective_status": "INELIGIBLE"}
    if eligibility in ("CONDITIONAL", "UNKNOWN"):
        return {"allowed": True, "reason": "conditional/unknown may rank but "
                "must surface unresolved facts",
                "effective_status": "CONDITIONAL"}
    return {"allowed": True, "reason": "eligible", "effective_status": "ELIGIBLE"}


def match_dimension_bundle(*, dimensions: dict[str, float]) -> dict:
    """C9: no one opaque match score. Separate dimensions + ranked
    recommendation derived deterministically (mean of aligned dimensions)."""
    if not dimensions:
        return {"dimensions": {}, "ranked_recommendation": None}
    aligned = {k: v for k, v in dimensions.items()
               if k not in ("competition_risk", "application_burden")}
    mean = sum(aligned.values()) / len(aligned) if aligned else 0.0
    return {
        "dimensions": dimensions,
        "ranked_recommendation": round(mean, 3),
        "derivation": "mean of alignment dimensions; hard eligibility "
                      "evaluated separately and never overridden",
    }


def evaluate_research_quality(*, findings: list[dict]) -> dict:
    """C10: research output evaluated for grounding, limitation disclosure,
    causal caution and provenance completeness (Book 5 FIND-001..005)."""
    total = len(findings)
    if total == 0:
        return {"research_quality": 0.0, "total": 0}
    with_evidence = sum(1 for f in findings if f.get("evidence_refs"))
    with_limitations = sum(1 for f in findings
                           if f.get("limitations"))
    weak_samples = [f for f in findings
                    if f.get("research_type") == "HISTORICAL_WINNER_PATTERN"
                    and (f.get("award_sample_size") or 0) < 10]
    causal_caution_fail = [f for f in weak_samples if not f.get("limitations")]
    provenance_complete = sum(1 for f in findings
                              if f.get("created_at") and f.get("created_by"))
    score = (with_evidence + with_limitations + provenance_complete) / (3 * total)
    return {
        "research_quality": round(score, 4),
        "with_evidence": with_evidence,
        "with_limitations": with_limitations,
        "weak_samples": len(weak_samples),
        "causal_caution_failures": len(causal_caution_fail),
        "provenance_complete": provenance_complete,
        "total": total,
    }


def future_target_not_historical(*, claims: list[dict]) -> dict:
    """C10/C29-27: a future target represented as a historical achievement is
    a hard failure (also enforced by Claim Ledger CLAIM-004)."""
    failures = [c["claim_id"] for c in claims
                if c.get("is_target") and not c.get("classified_as_target")]
    return {"pass": not failures, "failures": failures}
