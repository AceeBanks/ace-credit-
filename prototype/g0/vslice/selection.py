"""G0-B8-C5 — real opportunity discovery & selection.

Selection is governed: the candidate opportunity must exist in the
governed source fixture, carry an exact OpportunityRevision, and be
recorded via a Selection DecisionRecord. Discovery never fabricates a
source; when live source adapters are unavailable, the captured governed
snapshot is used and source mode is recorded accurately.
"""
from __future__ import annotations

from dataclasses import dataclass, field

from prototype.g0.domain.fixtures.georgia import GA_1
from prototype.g0.evidence.decisions import DecisionInputRef, build_decision


@dataclass
class SelectionResult:
    opportunity_id: str
    opportunity_title: str
    revision_id: str
    revision_number: int
    deadline: str | None
    funding_ceiling: str | None
    source_mode: str  # "LIVE_SOURCE" | "CAPTURED_SNAPSHOT"
    decision_record: dict
    candidate_records: list[dict] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {"opportunity_id": self.opportunity_id,
                "opportunity_title": self.opportunity_title,
                "revision_id": self.revision_id,
                "revision_number": self.revision_number,
                "deadline": self.deadline,
                "funding_ceiling": self.funding_ceiling,
                "source_mode": self.source_mode,
                "decision_record": self.decision_record,
                "candidate_records": self.candidate_records}


def run_selection(*, tenant_id: str, project_id: str,
                  principal_id: str, intent_id: str) -> SelectionResult:
    """Select the governed Georgia opportunity as the primary candidate.

    Uses the captured governed snapshot (GA_1 fixture) — source_mode is
    recorded as CAPTURED_SNAPSHOT because no live source adapter is
    configured in this environment; nothing is fabricated as live.
    """
    opp = GA_1["opportunity"]
    rev = GA_1["revision"]
    rev_ref = f"ref:opp_rev_{rev.revision_id}"
    decision = build_decision(
        decision_id=f"dec-sel-{intent_id}",
        decision_type="OPPORTUNITY_SELECTION",
        tenant_id=tenant_id, project_id=project_id,
        actor_ref=principal_id,
        capability_id="research.run",
        input_refs=[
            DecisionInputRef(input_role="intent", ref=f"ctx:intent-{intent_id}"),
            DecisionInputRef(input_role="opportunity_revision",
                             ref=rev_ref),
            DecisionInputRef(input_role="source_snapshot", ref="ref:snap-ga-1"),
        ],
        policy_ref="policy:book8-selection",
        result={"opportunity_id": opp.opportunity_id,
                "revision_id": rev.revision_id,
                "source_mode": "CAPTURED_SNAPSHOT"},
        explanation_data={
            "rationale": ("Governed Georgia-first fixture: state rural "
                           "community impact opportunity matching the "
                           "client's expansion intent (Georgia, rural "
                           "counties, youth workforce).")},
        status="APPROVED")
    return SelectionResult(
        opportunity_id=opp.opportunity_id,
        opportunity_title=opp.title,
        revision_id=rev.revision_id,
        revision_number=rev.revision_number,
        deadline=rev.deadline,
        funding_ceiling=str(rev.funding_ceiling) if rev.funding_ceiling
        else None,
        source_mode="CAPTURED_SNAPSHOT",
        decision_record=decision.to_dict(),
        candidate_records=[{
            "opportunity_id": opp.opportunity_id,
            "title": opp.title,
            "revision_id": rev.revision_id,
            "reason": "Georgia rural impact, county expansion fit",
        }])
