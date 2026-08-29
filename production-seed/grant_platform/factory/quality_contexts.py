"""G1-QUALITY-PROD — resolve the quality context for a project.

Maps a project's opportunity revision to a decomposed SolicitationProfile
plus the organization fact pack, client answers, applicant status, and
research block needed to run the canonical quality pipeline. Without a real
decomposed solicitation there is NO profile -> the API reports
NEEDS_OPPORTUNITY rather than generating a generic fake package.

The FY2026 AmeriCorps Georgia benchmark (the repo's decomposed
solicitation) is registered here so both the API and the benchmark API test
drive the SAME canonical path with the SAME governed inputs.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date

from grant_platform.factory.factpack import (
    build_mock_fact_pack, build_missing_fact_matrix)
from grant_platform.factory.integrity import (
    ApplicantStatus, ClientAnswer, RESEARCH_SOURCES)
from grant_platform.factory.solicitation import AMERICORPS_GA_2026

# Benchmark research pack — normalized official provenance (mission §18-§20).
RESEARCH_BLOCK = """- Child poverty, Walker County GA: 19.5% of under-18 residents
  (Census ACS 5-year 2020-2024, table S1701; retrieved 2026-08-28).
- Child poverty, Dade County GA: 16.4% of children
  (Census ACS via QuickFacts PEPTADR; retrieved 2026-08-28).
- Median household income, Dade County GA: $41,629
  (Census QuickFacts INC910224, 2020-2024; retrieved 2026-08-28).
- HS graduate or higher (25+), Dade County: 88.6%
  (Census QuickFacts, 2020-2024; retrieved 2026-08-28).
"""

AS_OF_BENCHMARK = date(2026, 2, 27)  # AmeriCorps NOFO deadline = as-of

BENCHMARK_BUDGET_LINES = [
    ("Member living allowances (8 full-time MSY)", "personnel", "112000.00"),
    ("Member FICA (7.65% of allowances)", "personnel", "8568.00"),
    ("Member healthcare assistance", "personnel", "4800.00"),
    ("Program director (0.25 FTE) — supervision & compliance",
     "personnel", "15600.00"),
    ("Member recruitment — advertising, campus visits, screening",
     "recruitment", "4800.00"),
    ("Member retention — certifications, coaching, recognition",
     "retention", "6000.00"),
    ("Data collection & evaluation systems", "evaluation", "7200.00"),
    ("Member training plan & tutoring curriculum", "training", "4800.00"),
    ("Indirect costs (10% de minimis)", "indirect", "16377.00"),
]


def _benchmark_client_answers() -> tuple[ClientAnswer, ...]:
    t = "2026-02-20T12:00:00+00:00"
    return (
        ClientAnswer(
            "member_dosage",
            ("Each member serves a full-time 1,700-hour term: 32 hours per "
             "week delivering 3 tutoring sessions per week of 90 minutes "
             "each across a 32-week program year"),
            answered_at=t, label="MOCK_CLIENT_ASSERTION"),
        ClientAnswer(
            "activity_schedule",
            ("Tutoring runs 3 afternoons per week per site in 90-minute "
             "sessions; summer bridge runs 4 weeks at 20 hours per week; "
             "workforce workshops run monthly (12 per year)"),
            answered_at=t, label="MOCK_CLIENT_ASSERTION"),
        ClientAnswer(
            "prior_americorps",
            ("NEW — the organization has never received AmeriCorps or "
             "Georgia Serves funding"),
            answered_at=t, label="MOCK_CLIENT_ASSERTION"),
    )


@dataclass
class QualityContext:
    """Everything required to run the canonical quality pipeline for one
    project, resolved from governed inputs (never invented)."""
    profile: object
    fact_pack: object
    matrix: object
    client_answers: tuple = ()
    applicant_status: object = None
    as_of: date | None = None
    research_block: str = ""
    ceiling: str | None = None
    client_budget_lines: list | None = None
    project_id: str = ""
    revision_id: str = ""
    source_id: str = ""

    @property
    def ready(self) -> bool:
        return self.profile is not None and self.fact_pack is not None


def _americorps_context(project_id: str, revision_id: str) -> QualityContext:
    fact_pack = build_mock_fact_pack()
    return QualityContext(
        profile=AMERICORPS_GA_2026,
        fact_pack=fact_pack,
        matrix=build_missing_fact_matrix(fact_pack),
        client_answers=_benchmark_client_answers(),
        applicant_status=ApplicantStatus(
            status="FORMULA_NEW",
            basis="MOCK_CLIENT_ASSERTION: never received AmeriCorps/Georgia "
                  "Serves funding; new applicants apply via formula funding "
                  "(NOFO C.1/B.1)"),
        as_of=AS_OF_BENCHMARK,
        research_block=RESEARCH_BLOCK,
        ceiling="182400.00",
        client_budget_lines=list(BENCHMARK_BUDGET_LINES),
        project_id=project_id,
        revision_id=revision_id,
        source_id="ga_dca_nofp_2026")


# Revision id -> profile builder. AmeriCorps is the repo's decomposed
# solicitation benchmark; the Georgia dev seed has no decomposed NOFO and
# therefore resolves to None -> NEEDS_OPPORTUNITY.
_CONTEXT_BUILDERS = {
    "ga_dca_nofp_2026": _americorps_context,
}


def build_context_for_revision(*, project_id: str,
                               revision_id: str) -> QualityContext | None:
    """QualityContext for a revision, or None when that revision has no
    decomposed solicitation (a real client gets NEEDS_OPPORTUNITY, never a
    generic fixture package)."""
    builder = _CONTEXT_BUILDERS.get(revision_id)
    if builder is None:
        return None
    return builder(project_id=project_id, revision_id=revision_id)


def unit_test_context(*, project_id: str = "proj-americorps",
                      revision_id: str = "ga_dca_nofp_2026",
                      with_answers: bool = True,
                      ) -> QualityContext:
    """Pure Python context builder (no store dependency) for API/factory
    integration tests and diagnostic runs."""
    ctx = build_context_for_revision(project_id=project_id,
                                     revision_id=revision_id)
    if ctx is not None and not with_answers:
        ctx.client_answers = ()
    return ctx


# Re-exported for provenance/reporting parity with run_quality_benchmark.
RESEARCH_SOURCES = RESEARCH_SOURCES