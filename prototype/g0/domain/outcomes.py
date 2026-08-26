"""G0 Book 2 — B2.C14 outcome & learning feedback semantics.

Outcomes are recorded as EVIDENCE for Book 7/self-improvement evaluation; an
outcome never rewrites prompts or policies by itself. Outcomes may be linked to
projects/awards after the fact; a historical award can exist without any
ApplicationProject.
"""
from __future__ import annotations

from dataclasses import replace

from prototype.g0.domain.models import OutcomeFeedback


def link_outcome(outcome: OutcomeFeedback, *, project_id: str | None = None,
                 award_id: str | None = None) -> OutcomeFeedback:
    """Link an outcome to a project/award AFTER the fact (B2.C14 linkage rule).
    The original outcome object is immutable and untouched."""
    return replace(outcome,
                   project_id=outcome.project_id if project_id is None else project_id,
                   award_id=outcome.award_id if award_id is None else award_id)


def learning_evidence(outcome: OutcomeFeedback) -> dict:
    """Outcome becomes an evidence record for Book 7 evaluation. This is the
    ONLY learning artifact: no prompt/policy rewrite happens here."""
    return {
        "evidence_kind": "outcome_feedback",
        "outcome_id": outcome.outcome_id,
        "outcome_type": outcome.outcome_type.value,
        "observed_at": outcome.observed_at,
        "reason_codes": list(outcome.reason_codes),
        "freeform_feedback": outcome.freeform_feedback,
        "source_evidence_refs": list(outcome.source_evidence_refs),
        "doctrine_effect": "none",       # B2.C14: evidence, not automatic doctrine
    }


def doctrine_unchanged(doctrine_before: dict, doctrine_after: dict) -> bool:
    """Guard: recording/learning from an outcome must leave doctrine intact."""
    return doctrine_before == doctrine_after
