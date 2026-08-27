"""G0-B7-C6 — Georgia-first fixture pack.

Reuses the governed Book 2/3 fixtures (GA-1 nonprofit + state opportunity,
COMMUNITY-1 statistic, federal profile) and layers evaluation metadata on
top: eligibility cases, requirement coverage, adversarial/protected-claim
cases, and the D2 experiment's canonical input. Fixtures are for evaluation
and shadow/mock work only — never external submission.
"""
from __future__ import annotations

from decimal import Decimal

from prototype.g0.domain.fixtures.georgia import GA_1
from prototype.g0.domain.fixtures.community import COMMUNITY_1

# D2 canonical input: the best governed Georgia-first fixture available
D2_FIXTURE = {
    "name": "D2 — first grounded grant-writing quality experiment",
    "organization": GA_1["organization"],
    "identifiers": GA_1["identifiers"],
    "opportunity": GA_1["opportunity"],
    "revision": GA_1["revision"],
    "rule_set": GA_1["rule_set"],
    "decision": GA_1["decision"],
    "requirements": GA_1["requirements"],
    "project": GA_1["project"],
    "statistics": [COMMUNITY_1["statistic"]],
    "facts": [GA_1["fact"]],
    "claims": [GA_1["claim"]],
}

# Protected elements for Humanizer evaluation (HZR-007): these values must
# never change across a style transform.
D2_PROTECTED_ELEMENTS = {
    "organization_legal_name": "Community Youth Works, Inc.",
    "organization_display_name": "Community Youth Works",
    "ein": "58-2345671",
    "state_registration": "1234567",
    "opportunity_title": "Georgia Rural Community Impact Grant FY2026",
    "opportunity_id": "opp_ga_501",
    "revision_id": "opp_rev_ga_501_1",
    "deadline": ["2026-10-15", "October 15, 2026"],
    "funding_ceiling": ["50000.00", "$50,000"],
    "geography": "Georgia",
    "county_statistic": "18.2",
    "county_statistic_unit": "percent",
    "county_statistic_geography": "Dade County, GA",
    "county_statistic_period": "2023",
    "eligibility_result": "ELIGIBLE",
}


def d2_requirements_text() -> list[dict]:
    """Normalized requirement texts used by deterministic drafting eval."""
    return [
        {
            "requirement_id": "req_ga_1",
            "mandatory": True,
            "type": "narrative",
            "prompt": "Describe the community impact of your program.",
            "word_limit": 2000,
            "source_location": "ga-solicitation-sec-5a",
        },
        {
            "requirement_id": "req_ga_2",
            "mandatory": True,
            "type": "budget",
            "prompt": "Provide a budget consistent with the award ceiling.",
            "ceiling": Decimal("50000.00"),
            "source_location": "ga-solicitation-sec-6",
        },
    ]


def d2_baseline_sections() -> dict[str, str]:
    """BASELINE GROUNDED DRAFT (deterministic, evidence-anchored).

    Every material value derives from D2_FIXTURE / D2_PROTECTED_ELEMENTS;
    nothing is invented. This is the seed for the D2 experiment and is also
    the reference against which Humanizer candidates are compared.
    """
    return {
        "community_impact": (
            "Community Youth Works operates in Georgia and serves Dade "
            "County, where the county poverty rate was 18.2 percent in 2023 "
            "(ACS 5-year estimate, Dade County, GA). The program addresses "
            "this need through youth workforce development activities."
        ),
        "organization": (
            "Community Youth Works, Inc. is a Georgia nonprofit founded in "
            "2012 and headquartered in Atlanta, GA."
        ),
        "budget_narrative": (
            "This request is for $50,000 within the Georgia Rural Community "
            "Impact Grant FY2026 award ceiling of $50,000. Funding supports "
            "program expansion into additional Georgia counties."
        ),
        "deadline": (
            "The application deadline is October 15, 2026 (revision "
            "opp_rev_ga_501_1)."
        ),
    }


def d2_claim_ledger_seed() -> list[dict]:
    """Seed Claim Ledger entries for the D2 baseline draft."""
    return [
        {
            "claim_id": "d2-c1",
            "claim_class": "POPULATION_COMMUNITY_STATISTICS",
            "claim_text_or_structured_ref": (
                "county poverty rate 18.2 percent, Dade County GA, 2023"),
            "is_target": False,
            "evidence_refs": ["ref:stat_ga_42"],
            "geography": "Dade County, GA",
            "unit": "percent",
            "support_status": "SUPPORTED",
            "qa_status": "PASSED",
            "artifact_version_id": "d2-art-v1",
        },
        {
            "claim_id": "d2-c2",
            "claim_class": "ORGANIZATION_IDENTITY",
            "claim_text_or_structured_ref": (
                "Community Youth Works, Inc. is a Georgia nonprofit, "
                "founded 2012"),
            "is_target": False,
            "evidence_refs": ["ref:snap-ga-1", "ref:snap-ga-2"],
            "support_status": "SUPPORTED",
            "qa_status": "PASSED",
            "artifact_version_id": "d2-art-v1",
        },
        {
            "claim_id": "d2-c3",
            "claim_class": "DEADLINE",
            "claim_text_or_structured_ref": "deadline October 15, 2026",
            "is_target": False,
            "evidence_refs": ["ref:opp_rev_ga_501_1"],
            "support_status": "SUPPORTED",
            "qa_status": "PASSED",
            "artifact_version_id": "d2-art-v1",
        },
        {
            "claim_id": "d2-c4",
            "claim_class": "FUNDING_AMOUNT",
            "claim_text_or_structured_ref": "award ceiling $50,000",
            "is_target": False,
            "evidence_refs": ["ref:opp_rev_ga_501_1"],
            "support_status": "SUPPORTED",
            "qa_status": "PASSED",
            "artifact_version_id": "d2-art-v1",
        },
    ]


def d2_budget_lines() -> list[dict]:
    """Deterministic budget: totals must reconcile exactly."""
    return [
        {"line_id": "d2-b1", "category": "program_staffing",
         "amount": Decimal("30000.00")},
        {"line_id": "d2-b2", "category": "participant_support",
         "amount": Decimal("12000.00")},
        {"line_id": "d2-b3", "category": "materials_and_equipment",
         "amount": Decimal("8000.00")},
    ]


def d2_budget_total() -> Decimal:
    return sum((line["amount"] for line in d2_budget_lines()), Decimal("0"))
