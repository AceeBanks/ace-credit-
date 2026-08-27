"""G0-B8-C10/C11/C12/C13 — funder/winner/community research + synthesis.

Every research statement carries Book 5 lineage (source snapshot,
statistic, or canonical fact). Research is limitation-aware: historical
awards prove what they prove and nothing more (no prohibited inference to
this client). Community evidence is typed and geographically correct.
"""
from __future__ import annotations

from dataclasses import dataclass, field

from prototype.g0.domain.fixtures.community import COMMUNITY_1
from prototype.g0.domain.fixtures.georgia import GA_1
from prototype.g0.evidence.research import validate_finding


class _Graph:
    """Minimal evidence graph stub: refs resolve to their base type."""

    _TYPE = {
        "ref:snap-ga-1": "SOURCE_SNAPSHOT",
        "ref:snap-ga-2": "SOURCE_SNAPSHOT",
        "ref:snap-community-1": "SOURCE_SNAPSHOT",
        "ref:stat_ga_42": "STATISTIC_OBSERVATION",
        "ref:fact_ga_1": "CANONICAL_FACT",
    }

    def resolve_or_tombstone(self, ref: str) -> dict:
        return {"ref_type": self._TYPE.get(ref, "SOURCE_SNAPSHOT"),
                "tombstoned": False}


@dataclass
class ResearchResult:
    findings: list[dict]
    synthesis: dict
    evidence_refs: list[str] = field(default_factory=list)

    def validate(self) -> None:
        for f in self.findings:
            if not f.get("evidence_refs"):
                raise ValueError("research finding without lineage (B8.C10)")
            if not f.get("limitations"):
                raise ValueError("research finding must carry limitations "
                                 "(FIND-002)")


def run_research(*, tenant_id: str, project_id: str, principal_id: str,
                 intent_id: str, revision_id: str) -> ResearchResult:
    """Gather funder priorities, organization verification, and community
    statistics — all governed and lineaged."""
    stats = COMMUNITY_1["statistic"]
    graph = _Graph()
    findings = [
        {
            "finding_id": f"rs-{intent_id}-community",
            "research_type": "COMMUNITY_NEED",
            "subject_refs": ["ref:stat_ga_42"],
            "statement": (f"county poverty rate {stats.value} {stats.unit} "
                          f"({stats.geography}, {stats.reference_period})"),
            "evidence_refs": ["ref:stat_ga_42", "ref:snap-community-1"],
            "applicability": "Dade County, GA population",
            "limitations": [("statistic describes the county population; it "
                             "does not prove this organization's outcomes")],
            "created_by": "CommunityEvidenceWorker",
        },
        {
            "finding_id": f"rs-{intent_id}-org",
            "research_type": "OTHER",
            "subject_refs": [f"ref:org_{GA_1['organization'].organization_id}"],
            "statement": (f"{GA_1['organization'].legal_name} is a Georgia "
                          f"nonprofit; 501(c)(3) verified via fact_ga_1"),
            "evidence_refs": ["ref:snap-ga-1", "ref:snap-ga-2",
                              "ref:fact_ga_1"],
            "applicability": f"organization {GA_1['organization'].organization_id}",
            "limitations": [("entity status verified; staff size and "
                             "financial capacity are UNKNOWN")],
            "created_by": "WinnerResearchWorker",
        },
        {
            "finding_id": f"rs-{intent_id}-funder",
            "research_type": "FUNDER_PRIORITY",
            "subject_refs": [f"ref:opp_rev_{revision_id}"],
            "statement": (f"Georgia Rural Community Impact Grant FY2026 "
                          f"targets rural community impact "
                          f"(program {GA_1['opportunity'].program_id})"),
            "evidence_refs": [f"ref:opp_rev_{revision_id}", "ref:snap-ga-1"],
            "applicability": "Georgia Rural Community Impact Grant FY2026",
            "limitations": [("funder priorities as stated in the solicitation "
                             "revision; no insider preference inferred")],
            "created_by": "FunderResearchWorker",
        },
    ]
    validated = [validate_finding(finding=f, graph=graph) for f in findings]

    synthesis = {
        "strategy": [
            "lead with the county poverty statistic (governed, typed)",
            "state eligibility plainly (ELIGIBLE, deterministic)",
            "declare capacity unknowns explicitly rather than inventing",
            "align program activities to the funder's rural-impact theme",
        ],
        "evidence_refs_used": [f["evidence_refs"][0]
                               for f in validated],
        "prohibited_inferences_checked": [
            "winner similarity implies this client wins",
            "past award amount implies this request",
            "funder preference implies eligibility",
        ],
    }
    result = ResearchResult(
        findings=validated, synthesis=synthesis,
        evidence_refs=[r for f in validated for r in f["evidence_refs"]])
    result.validate()
    return result
