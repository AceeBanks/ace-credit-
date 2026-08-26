"""G0-B5-C20 — D0/D1 evidence readiness prototype.

D0 shadow drafts carry a mock proposal artifact version plus claim ledger,
research findings, provenance refs, QA factuality and an explanation packet,
with an evidence-completeness label derived from claim coverage (DRAFT-001)
and submission_ready always false (DRAFT-002). D1 CEO/worker evidence flows
through bounded ContextBundles (DRAFT-003/004); missing evidence surfaces as
gaps (DRAFT-005); Personal explanations reflect the CEO decision packet
(DRAFT-006).
"""
from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from prototype.g0.evidence.models import EvidenceGraph


class DraftReadinessError(ValueError):
    """Raised when a draft violates the evidence readiness policy."""


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _load_policy() -> dict:
    import yaml
    from pathlib import Path
    root = Path(__file__).resolve().parents[3]
    return yaml.safe_load((root / "config/g0/evidence/"
                           "draft_readiness_policy.yaml").read_text(encoding="utf-8"))


_POLICY = _load_policy()


def assess_d0_coverage(*, claim_ledger_entries: list[dict],
                       threshold: float | None = None,
                       policy: dict | None = None) -> dict:
    """DRAFT-001: coverage = SUPPORTED claims / total claims."""
    policy = policy or _POLICY
    threshold = threshold if threshold is not None \
        else policy["coverage_threshold"]
    total = len(claim_ledger_entries)
    if total == 0:
        return {"coverage": 0.0, "supported": 0, "total": 0,
                "evidence_label": "EVIDENCE_INCOMPLETE",
                "threshold": threshold, "meets_threshold": False}
    supported = sum(1 for e in claim_ledger_entries
                    if e.get("support_status") in ("SUPPORTED",
                                                   "SUPPORTED_WITH_QUALIFICATION",
                                                   "USER_ATTESTED"))
    coverage = supported / total
    return {
        "coverage": round(coverage, 3),
        "supported": supported,
        "total": total,
        "threshold": threshold,
        "meets_threshold": coverage >= threshold,
        "evidence_label": "EVIDENCE_COMPLETE" if coverage >= threshold
        else "EVIDENCE_INCOMPLETE",
    }


def build_d0_shadow_draft(*, artifact_version_id: str, tenant_id: str,
                          project_id: str, claim_ledger_entries: list[dict],
                          research_findings: list[dict],
                          evidence_refs: list[str],
                          qa_factuality: dict,
                          explanation_packet: dict,
                          policy: dict | None = None) -> dict:
    """Assemble a D0 shadow draft packet with derived evidence label."""
    policy = policy or _POLICY
    coverage = assess_d0_coverage(claim_ledger_entries=claim_ledger_entries,
                                  policy=policy)
    packet = {
        "label": "MOCK_NON_SUBMISSION",
        "submission_ready": False,  # DRAFT-002: structurally impossible
        "artifact_version_id": artifact_version_id,
        "tenant_id": tenant_id,
        "project_id": project_id,
        "claim_ledger_entries": claim_ledger_entries,
        "research_findings": research_findings,
        "evidence_refs": evidence_refs,
        "qa_factuality": qa_factuality,
        "explanation_packet": explanation_packet,
        "evidence_label": coverage["evidence_label"],
        "claim_coverage": coverage["coverage"],
        "created_at": _now(),
    }
    return packet


def build_d1_context_bundle(*, tenant_id: str, project_id: str,
                            requirements: list[str], graph: EvidenceGraph,
                            all_refs: list[str]) -> dict:
    """DRAFT-003/004: bounded ContextBundle — only tenant/project scoped
    evidence relevant to the assigned requirements reaches the worker."""
    bundle_refs = []
    for ref_id in all_refs:
        resolved = graph.resolve_or_tombstone(ref_id)
        if resolved.get("tombstoned"):
            continue
        if resolved.get("tenant_id") != tenant_id:
            continue  # DRAFT-003: unrelated tenant excluded
        # requirement relevance: ref entity/ref id mentions a requirement key
        if any(req.lower() in ref_id.lower() or req.lower() in str(
                resolved.get("entity_id", "")).lower()
                for req in requirements):
            bundle_refs.append(ref_id)
    return {"tenant_id": tenant_id, "project_id": project_id,
            "requirements": list(requirements),
            "evidence_refs": bundle_refs,
            "bounded": True}


def worker_result(*, draft_content_or_artifact_ref: str, claims_created: list[str],
                  evidence_used: list[str], assumptions: list[str],
                  sidechain_ref: str, policy: dict | None = None) -> dict:
    """DRAFT-005: missing evidence is surfaced as a gap, not hallucinated."""
    policy = policy or _POLICY
    gaps = []
    for claim in claims_created:
        if claim not in evidence_used and not any(
                m in claim for m in ("[TODO]", "[TBD]", "[question]",
                                     "[placeholder]")):
            gaps.append(f"claim '{claim[:40]}...' has no evidence ref")
    result = {
        "draft_content_or_artifact_ref": draft_content_or_artifact_ref,
        "claims_created": list(claims_created),
        "evidence_used": list(evidence_used),
        "assumptions": list(assumptions),
        "unresolved_evidence_gaps": gaps,
        "sidechain_ref": sidechain_ref,
    }
    return result


def explanation_reflects_decision(*, explanation_packet: dict,
                                  decision: Any) -> bool:
    """DRAFT-006: Personal Hermes explanation reflects the CEO decision
    packet — same outcome, decision ref, and evidence refs."""
    if explanation_packet.get("decision_record_ref") != decision.decision_id:
        return False
    if explanation_packet.get("summary") != (decision.result or {}).get("summary"):
        return False
    cited = set(explanation_packet.get("cited_evidence_refs", []))
    inputs = {i.ref for i in decision.input_refs}
    return cited <= inputs
