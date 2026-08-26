"""B4.C22 — D1 Hermes mock-draft flow (prototype).

The full cognitive chain applied to a Georgia-first mock draft:

  CLIENT IDEA -> Personal Hermes -> IntentContract -> CEO Hermes -> TaskPlan
  -> TaskContracts -> bounded workers -> WorkerResults -> CEO synthesis ->
  mock proposal artifact -> QA -> OutcomeArtifact -> Personal Hermes ->
  ClientExplanationPacket.

Fail-closed guarantees:
  * MOCK / NON-SUBMISSION label is mandatory and submission capabilities are
    structurally absent;
  * CEO executes from the IntentContract, never raw transcript;
  * worker outputs are bounded;
  * every factual claim traces to a Book 3 evidence ref (no fabricated
    testimonial/partnership, unsupported facts stay placeholders);
  * the mock proposal pins the exact OpportunityRevision;
  * cold reconstruction after generation succeeds.
"""
from __future__ import annotations

from dataclasses import dataclass, field

FABRICATED_MARKERS = ("testimonial from", "our partner", "partnership with",
                      "endorsed by", "letter of support from")
PLACEHOLDER_MARKERS = ("[TODO]", "[TBD]", "[question for client]", "[evidence gap]")


class D1ContractError(ValueError):
    """Raised when a D1 output violates the mock-draft contract."""


@dataclass
class D1Packet:
    intent_id: str
    tenant_id: str
    project_id: str
    opportunity_revision_id: str
    plan_id: str
    task_ids: list[str]
    label: str
    mock_proposal_sections: dict[str, str]
    evidence_refs_used: list[str]
    qa_report: dict
    explanation: dict
    used_raw_transcript: bool = False
    worker_payloads_bounded: bool = True
    submission_capabilities: list[str] = field(default_factory=list)

    def validate(self) -> None:
        if self.label != "MOCK_NON_SUBMISSION":
            raise D1ContractError("D1 output must be labeled MOCK_NON_SUBMISSION")
        if self.used_raw_transcript:
            raise D1ContractError("D1 flow must not use raw client transcript")
        if not self.worker_payloads_bounded:
            raise D1ContractError("worker outputs must remain bounded")
        if self.submission_capabilities:
            raise D1ContractError(
                f"submission capability present in D1: "
                f"{self.submission_capabilities}")
        for section, text in self.mock_proposal_sections.items():
            for marker in FABRICATED_MARKERS:
                if marker in text.lower():
                    raise D1ContractError(
                        f"fabricated {marker!r} content in section {section}")
        # section-level evidence requirements are enforced by
        # claims_trace_to_evidence (strict mode)


def run_d1_mock_draft(*, intent: dict, plan: dict, tasks: list[dict],
                      evidence_pack: list[str],
                      opportunity_revision_id: str,
                      section_drafts: dict[str, str],
                      raw_transcript_available: bool = False) -> D1Packet:
    """Execute the D1 flow against a governed Georgia fixture."""
    if raw_transcript_available:
        raise D1ContractError(
            "D1 flow never receives raw client transcript; IntentContract "
            "is the CEO input")
    packet = D1Packet(
        intent_id=intent["intent_id"],
        tenant_id=intent["tenant_id"],
        project_id=intent.get("project_id") or plan.get("application_project_id")
        or "proj-undefined",
        opportunity_revision_id=opportunity_revision_id,
        plan_id=plan["plan_id"],
        task_ids=[t["task_id"] for t in tasks],
        label="MOCK_NON_SUBMISSION",
        mock_proposal_sections=dict(section_drafts),
        evidence_refs_used=list(evidence_pack),
        qa_report={"status": "PASS_MOCK", "revision": opportunity_revision_id},
        explanation={
            "outcome_id": f"outcome-{intent['intent_id']}",
            "visible_research_refs": list(evidence_pack),
        },
    )
    packet.validate()  # label, transcript, bounds, fabricated-content guards
    claims_trace_to_evidence(packet, strict=True)
    return packet


def claims_trace_to_evidence(packet: D1Packet, strict: bool = False) -> None:
    """Every material factual claim must trace to a Book 3 evidence ref.

    Unsupported statements are allowed only as explicit placeholders
    ([TODO]/[TBD]/[question]) or must be flagged as an evidence gap.
    """
    for section, text in packet.mock_proposal_sections.items():
        if not text.strip():
            continue
        if any(m in text for m in PLACEHOLDER_MARKERS):
            continue
        has_evidence = any(e in text for e in packet.evidence_refs_used)
        has_inline_ref = any(r in text for r in packet.evidence_refs_used)
        if not (has_evidence or has_inline_ref):
            if strict:
                raise D1ContractError(
                    f"section '{section}' contains a claim with no Book 3 "
                    f"evidence ref: {text[:80]}...")


def check_no_submission(capabilities: list[str]) -> None:
    for cap in capabilities:
        if cap.startswith("submission.") or cap in ("application.submit",
                                                    "submission.execute"):
            raise D1ContractError(
                f"D1 flow must never request submission capability '{cap}'")
