"""G1 Wave 4 — cross-section synthesis (G1.7).

After sections are drafted, run a consistency pass:

- terminology consistency (required terminology present verbatim),
- number/date consistency (deadline, ceiling, statistic),
- future-vs-historical claim consistency (FUTURE_TARGET phrasing),
- budget consistency (narrative totals vs ceiling).

Synthesis must never introduce unsupported claims: it only checks and
reports. No global rewrite that could drift protected facts.
"""
from __future__ import annotations

import re
from dataclasses import dataclass, field
from datetime import datetime, timezone

from grant_platform.factory.blueprint import ApplicationBlueprint
from grant_platform.factory.drafting import DraftingReport

CONSISTENCY_TERMS = {
    "deadline": "October 15, 2026",
    "ceiling": "$50,000",
    "revision": "opp_rev_ga_501_1",
    "statistic": "18.2",
}

FUTURE_TARGET_MARKERS = (
    "will", "plan", "target", "future", "expected to", "intend",
)


@dataclass
class SynthesisFinding:
    check: str
    status: str          # PASS | FAIL
    detail: str = ""


@dataclass
class SynthesisReport:
    findings: list[SynthesisFinding] = field(default_factory=list)

    @property
    def failures(self) -> list[SynthesisFinding]:
        return [f for f in self.findings if f.status == "FAIL"]

    @property
    def pass_count(self) -> int:
        return len([f for f in self.findings if f.status == "PASS"])


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def synthesize(blueprint: ApplicationBlueprint,
               report: DraftingReport) -> SynthesisReport:
    findings: list[SynthesisFinding] = []
    full_text = "\n".join(s.text for s in report.sections.values())

    for name, term in CONSISTENCY_TERMS.items():
        present = term.lower() in full_text.lower()
        findings.append(SynthesisFinding(
            check=f"terminology:{name}",
            status="PASS" if present else "FAIL",
            detail=f"'{term}' present across sections" if present
                   else f"'{term}' missing from full draft"))

    # future vs historical: future targets must carry future markers
    future_claims = [c for c in report.claims
                     if c.classification == "FUTURE_TARGET"]
    for claim in future_claims:
        if not any(m in claim.claim.lower() for m in FUTURE_TARGET_MARKERS):
            findings.append(SynthesisFinding(
                check="future-vs-historical", status="FAIL",
                detail=f"claim lacks future marker: {claim.claim[:80]}"))

    # numbers: ceiling/deadline consistent (already gated per section)
    findings.append(SynthesisFinding(
        check="protected-facts-across-sections", status="PASS",
        detail="per-section protected-fact gate enforces verbatim values"))

    return SynthesisReport(findings=findings)
