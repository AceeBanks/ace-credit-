"""G0-B8-C2 — canonical client fixture.

Community Youth Works, Inc. — the governed Georgia fixture carried from
Books 2-7 — enriched for the vertical slice. Every material value declares
its evidence status; intentionally incomplete in places to exercise
UNKNOWN / clarification behavior (no magical perfect client).
"""
from __future__ import annotations

from prototype.g0.domain.fixtures.georgia import GA_1
from prototype.g0.vslice.models import ClientProfile

CLIENT_INTENT = (
    "We want to expand our youth workforce program into two more Georgia "
    "counties next year. Find funding that makes sense and build the "
    "strongest package we can for the best opportunity."
)

# Evidence-status taxonomy from the Book 8 plan (C2)
EVIDENCE_VERIFIED_OFFICIAL = "VERIFIED_OFFICIAL"
EVIDENCE_CLIENT_PROVIDED = "CLIENT_PROVIDED"
EVIDENCE_DERIVED = "DERIVED"
EVIDENCE_INFERRED = "INFERRED"
EVIDENCE_UNKNOWN = "UNKNOWN"
EVIDENCE_CONFLICTED = "CONFLICTED"


def build_client_profile() -> ClientProfile:
    org = GA_1["organization"]
    return ClientProfile(
        organization_id=org.organization_id,
        legal_name=org.legal_name,
        display_name=org.preferred_display_name,
        entity_type=org.organization_kind.value,
        jurisdiction=org.jurisdiction or "Georgia",
        ein="58-2345671",
        formation_year="2012",
        status_claim="501(c)(3)",
        mission=("Youth workforce development for Georgia communities "
                 "experiencing economic need."),
        problem_addressed=(
            "Youth unemployment and underemployment in high-poverty rural "
            "Georgia counties."),
        target_population="Youth ages 14-24 in rural Georgia counties",
        service_geography="Atlanta, GA (HQ); serving Dade County, GA",
        program_activities=["job-skill training", "mentorship",
                            "after-school enrichment", "work placement"],
        current_capacity=None,  # UNKNOWN: staff size / annual budget
        expansion_goal="Expand into two more Georgia counties next year",
        requested_funding_use="Program expansion into additional counties",
        measurable_future_outcomes=[
            "increased youth employment placement",
            "improved educational outcomes",
        ],
        known_historical_outcomes=[],  # none governed; must stay UNKNOWN
        unknown_items=[
            "staff size", "annual operating budget", "board composition",
            "prior grants received", "program outcomes history",
            "Dade County service-site address",
        ],
        evidence_status={
            "legal_name": EVIDENCE_VERIFIED_OFFICIAL,
            "ein": EVIDENCE_VERIFIED_OFFICIAL,
            "formation_year": EVIDENCE_VERIFIED_OFFICIAL,
            "status_claim": EVIDENCE_VERIFIED_OFFICIAL,
            "mission": EVIDENCE_CLIENT_PROVIDED,
            "target_population": EVIDENCE_CLIENT_PROVIDED,
            "expansion_goal": EVIDENCE_CLIENT_PROVIDED,
            "current_capacity": EVIDENCE_UNKNOWN,
            "known_historical_outcomes": EVIDENCE_UNKNOWN,
        },
    )
