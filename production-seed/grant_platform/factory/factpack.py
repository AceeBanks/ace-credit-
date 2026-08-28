"""G1-QUALITY-03 — Organization Fact Pack + Missing Fact Matrix.

Every applicant fact carries fact_id, value, source, confidence,
last_verified, and allowed_claim_type. Facts the solicitation demands but
the pack lacks are classified CRITICAL_BLOCKER / IMPORTANT_CLARIFICATION /
OPTIONAL_ENRICHMENT (mission §7-§9). Critical gaps become client questions
BEFORE drafting — the engine never invents facts to fill them.

The benchmark applicant is explicitly labeled MOCK_EVALUATION_ORGANIZATION:
its facts are evaluation fixtures, never presented as a real client's data.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


# Claim types (align with the claim ledger classifications)
ALLOWED_CLAIM_TYPES = (
    "CANONICAL_FACT",      # verbatim legal identity — always citable
    "CLIENT_ASSERTION",    # org-supplied fact, usable as client assertion
    "STATISTIC",           # externally sourced number w/ lineage
    "FUTURE_TARGET",       # approved planning target, labeled as such
)


@dataclass(frozen=True)
class OrgFact:
    fact_id: str
    category: str          # identity | mission | programs | staffing | capacity | financial | geography | outcomes
    key: str
    value: object
    source: str            # where the fact came from
    confidence: str        # VERIFIED | CLIENT_ASSERTED | ASSUMED
    last_verified: str
    allowed_claim_type: str = "CLIENT_ASSERTION"


@dataclass
class OrganizationFactPack:
    organization_label: str          # e.g. MOCK_EVALUATION_ORGANIZATION
    legal_name: str
    facts: dict[str, OrgFact] = field(default_factory=dict)

    def add(self, fact: OrgFact) -> None:
        self.facts[fact.fact_id] = fact

    def get(self, fact_id: str) -> OrgFact | None:
        return self.facts.get(fact_id)

    def value(self, fact_id: str, default=None):
        f = self.facts.get(fact_id)
        return f.value if f else default

    def by_category(self, category: str) -> list[OrgFact]:
        return [f for f in self.facts.values() if f.category == category]


@dataclass(frozen=True)
class MissingFact:
    fact_id: str
    what: str
    why_needed: str
    severity: str        # CRITICAL_BLOCKER | IMPORTANT_CLARIFICATION | OPTIONAL_ENRICHMENT
    client_question: str  # the exact question to ask the client


@dataclass
class MissingFactMatrix:
    organization_label: str
    missing: list[MissingFact] = field(default_factory=list)

    def critical(self) -> list[MissingFact]:
        return [m for m in self.missing if m.severity == "CRITICAL_BLOCKER"]

    def important(self) -> list[MissingFact]:
        return [m for m in self.missing if m.severity == "IMPORTANT_CLARIFICATION"]

    def client_questions(self) -> list[str]:
        return [m.client_question for m in self.missing
                if m.severity in ("CRITICAL_BLOCKER", "IMPORTANT_CLARIFICATION")]


def _f(fid: str, cat: str, key: str, value, src: str,
       conf: str = "CLIENT_ASSERTED",
       claim: str = "CLIENT_ASSERTION") -> OrgFact:
    return OrgFact(fact_id=fid, category=cat, key=key, value=value,
                   source=src, confidence=conf, last_verified=_now(),
                   allowed_claim_type=claim)


def build_mock_fact_pack() -> OrganizationFactPack:
    """Benchmark evaluation fact pack — MOCK_EVALUATION_ORGANIZATION.

    Enough known facts to draft substantively without fabrication; the
    gaps it intentionally retains exercise the missing-fact matrix.
    """
    pack = OrganizationFactPack(
        organization_label="MOCK_EVALUATION_ORGANIZATION",
        legal_name="Rural Georgia Youth Development Coalition, Inc.")
    A = _f
    # identity
    pack.add(A("legal_name", "identity", "legal_name",
               "Rural Georgia Youth Development Coalition, Inc.",
               "Mock org charter", "VERIFIED", "CANONICAL_FACT"))
    pack.add(A("ein", "identity", "ein", "58-2345671",
               "Mock IRS records", "VERIFIED", "CANONICAL_FACT"))
    pack.add(A("founded", "identity", "founded_year", 2012,
               "Mock org charter", "VERIFIED", "CANONICAL_FACT"))
    pack.add(A("sam_uei", "identity", "sam_uei", "JJ7KQM4XLYY3",
               "Mock SAM registration", "VERIFIED", "CANONICAL_FACT"))
    pack.add(A("address", "identity", "hq_address",
               "1420 Elm Street, LaFayette, GA 30728",
               "Mock org charter", "VERIFIED", "CANONICAL_FACT"))
    # mission / geography / population
    pack.add(A("mission", "mission", "mission_statement",
               "To expand educational and economic opportunity for rural "
               "Northwest Georgia youth through mentoring, tutoring, and "
               "workforce readiness.",
               "Mock org charter", "VERIFIED", "CANONICAL_FACT"))
    pack.add(A("service_area", "geography", "service_area",
               "Walker, Dade, and Catoosa counties in Northwest Georgia",
               "Mock program records", "VERIFIED", "CANONICAL_FACT"))
    pack.add(A("population", "population", "population_served",
               "Students in grades 6-12 in rural Northwest Georgia, with a "
               "focus on youth at risk of disengaging from school",
               "Mock program records", "VERIFIED", "CLIENT_ASSERTION"))
    pack.add(A("youth_served", "outcomes", "youth_served_annually", 420,
               "Mock 2025 program report", "VERIFIED", "CLIENT_ASSERTION"))
    # programs / capacity / staffing
    pack.add(A("programs", "programs", "current_programs",
               ("After-school tutoring in LaFayette and Trenton (4 sites)",
                "Summer bridge program", "Workforce readiness workshops"),
               "Mock program records", "VERIFIED", "CLIENT_ASSERTION"))
    pack.add(A("staff_ft", "staffing", "full_time_staff", 7,
               "Mock payroll", "VERIFIED", "CLIENT_ASSERTION"))
    pack.add(A("staff_pt", "staffing", "part_time_staff", 11,
               "Mock payroll", "VERIFIED", "CLIENT_ASSERTION"))
    pack.add(A("exec_director", "staffing", "executive_director",
               "Dana Whitfield, MPA — 14 years youth development leadership",
               "Mock org records", "VERIFIED", "CLIENT_ASSERTION"))
    pack.add(A("program_dir", "staffing", "program_director",
               "Marcus Ellison, LMSW — supervises site coordinators and "
               "member programming",
               "Mock org records", "VERIFIED", "CLIENT_ASSERTION"))
    pack.add(A("finance_controls", "capacity", "financial_controls",
               "Annual independent audit (last: FY2025, unqualified opinion); "
               "segregation of duties; board-approved procurement policy; "
               "QuickBooks-based grant cost tracking by award",
               "Mock audit letter", "VERIFIED", "CLIENT_ASSERTION"))
    pack.add(A("board", "capacity", "board_size", 13,
               "Mock board roster", "VERIFIED", "CLIENT_ASSERTION"))
    pack.add(A("facilities", "capacity", "facilities",
               "LaFayette community center HQ plus 3 partner school sites",
               "Mock facility agreements", "VERIFIED", "CLIENT_ASSERTION"))
    # financial
    pack.add(A("budget_annual", "financial", "annual_budget_usd", 1_150_000,
               "Mock FY2026 board-approved budget", "VERIFIED",
               "CLIENT_ASSERTION"))
    pack.add(A("match_ability", "financial", "match_capacity",
               "Board-committed cash match of $39,600/yr plus in-kind space "
               "valued at $18,000/yr — covers 24% match requirement",
               "Mock board resolution 2026-03", "VERIFIED",
               "CLIENT_ASSERTION"))
    pack.add(A("funding_history", "financial", "funding_history",
               ("21st CCLC (2019-2024)", "Schafer Family Foundation "
                "(2023-2026)", "United Way of Northwest Georgia (2022-2026)"),
               "Mock grant ledger", "VERIFIED", "CLIENT_ASSERTION"))
    # evidence base (supports Evidence Tier scoring)
    pack.add(A("evidence_study", "outcomes", "internal_eval_2025",
               "2025 internal evaluation: 3-year pre/post cohort (n=387) of "
               "program participants — +0.4 grade equivalents in math, +0.5 "
               "in reading; 91% of regularly attending seniors graduated on "
               "time vs 78% district comparison",
               "Mock 2025 evaluation report", "VERIFIED", "STATISTIC"))
    pack.add(A("prior_outcomes", "outcomes", "retention_metrics",
               "2024-25: 87% of youth attended 30+ sessions; 84% of "
               "regularly attending youth improved school engagement scores",
               "Mock 2025 program report", "VERIFIED", "CLIENT_ASSERTION"))
    # planning targets (FUTURE_TARGET type — must stay labeled as targets)
    pack.add(A("msy_target", "planning", "msy_request", 8,
               "Board-approved 2026 AmeriCorps plan", "CLIENT_ASSERTED",
               "FUTURE_TARGET"))
    pack.add(A("member_count", "planning", "americorps_members", 8,
               "Board-approved 2026 AmeriCorps plan", "CLIENT_ASSERTED",
               "FUTURE_TARGET"))
    pack.add(A("leveraged_volunteers", "planning", "leveraged_volunteers", 60,
               "Board-approved 2026 AmeriCorps plan", "CLIENT_ASSERTED",
               "FUTURE_TARGET"))
    pack.add(A("sites", "planning", "service_sites",
               "LaFayette HS, Ridgeville MS, Trenton Elementary, Rossville "
               "Community Center",
               "Board-approved 2026 AmeriCorps plan", "CLIENT_ASSERTED",
               "FUTURE_TARGET"))
    return pack


def build_missing_fact_matrix(
        pack: OrganizationFactPack) -> MissingFactMatrix:
    """Compare what drafting will assert vs what the pack actually holds
    (mission §8). Severity drives whether the engine asks the client first."""
    mx = MissingFactMatrix(pack.organization_label)
    V = pack.value
    # Member dosage details — required by NOFO logic-model criterion
    if not V("member_dosage"):
        mx.missing.append(MissingFact(
            "member_dosage",
            "Hours per week and total term-of-service hours for each member "
            "slot (half-time vs full-time MSY mix)",
            "NOFO Logic Model requires dosage for every activity",
            "CRITICAL_BLOCKER",
            "How many hours per week will each AmeriCorps member serve, and "
            "which term (full-time 1,700 hrs vs half-time 900 hrs) are you "
            "requesting?"))
    if not V("activity_schedule"):
        mx.missing.append(MissingFact(
            "activity_schedule",
            "Weekly tutoring session count and per-session length per site",
            "Logic model core activities need length + dosage",
            "IMPORTANT_CLARIFICATION",
            "How many tutoring sessions per week will run at each site, and "
            "how long is each session?"))
    if not V("grad_rate_baseline"):
        mx.missing.append(MissingFact(
            "grad_rate_baseline",
            "External confirmation of county graduation rates used as the "
            "comparison baseline",
            "Need section compares outcomes to district baseline",
            "OPTIONAL_ENRICHMENT",
            "Do you want us to cite GADOE 2025 graduation rates as the "
            "comparison baseline?"))
    if not V("prior_americorps"):
        mx.missing.append(MissingFact(
            "prior_americorps",
            "Whether the organization has ever held an AmeriCorps grant "
            "(new vs recompete applicant status)",
            "Determines grant types available and evaluation plan "
            "requirement",
            "CRITICAL_BLOCKER",
            "Has your organization previously received AmeriCorps or "
            "Georgia Serves funding?"))
    return mx
