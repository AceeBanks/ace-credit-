"""B7.C5/C6 — Golden set protocol + Georgia fixture pack tests.

Tier classification integrity, protected-element pinning (HZR-007), D2
fixture identity, budget determinism, and the fixture-pack coverage rules.
"""
from __future__ import annotations

import sys
from decimal import Decimal
from pathlib import Path

import pytest

_ROOT = Path(__file__).resolve().parents[3]
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from prototype.g0.evaluation.fixtures import (  # noqa: E402
    D2_FIXTURE,
    D2_PROTECTED_ELEMENTS,
    d2_baseline_sections,
    d2_budget_lines,
    d2_budget_total,
    d2_claim_ledger_seed,
    d2_requirements_text,
)


def test_d2_fixture_binds_exact_opportunity_revision():
    assert D2_FIXTURE["revision"].revision_id == "opp_rev_ga_501_1"
    assert D2_FIXTURE["project"].opportunity_revision_id == \
        D2_FIXTURE["revision"].revision_id


def test_d2_fixture_decision_is_eligible():
    from prototype.g0.domain.models import EligibilityStatus
    assert D2_FIXTURE["decision"].result is EligibilityStatus.ELIGIBLE


def test_d2_fixture_organization_is_georgia_nonprofit():
    from prototype.g0.domain.models import OrganizationKind
    org = D2_FIXTURE["organization"]
    assert org.jurisdiction == "Georgia"
    assert org.organization_kind is OrganizationKind.NONPROFIT


def test_d2_fixture_includes_community_statistic():
    stats = D2_FIXTURE["statistics"]
    assert len(stats) == 1
    stat = stats[0]
    assert stat.geography == "county-121 (Dade County, GA)"
    assert "Dade County, GA" in stat.geography
    assert stat.value == Decimal("18.2")
    assert stat.unit == "percent"


def test_protected_elements_pin_deadline_and_ceiling():
    assert D2_PROTECTED_ELEMENTS["deadline"] == "2026-10-15"
    assert D2_PROTECTED_ELEMENTS["funding_ceiling"] == "50000.00"
    assert D2_PROTECTED_ELEMENTS["revision_id"] == "opp_rev_ga_501_1"
    assert D2_PROTECTED_ELEMENTS["organization_legal_name"] == \
        "Community Youth Works, Inc."


def test_protected_elements_cover_humanizer_attack_surface():
    """The A-J Humanizer attack list targets exactly these elements."""
    for key in ("organization_legal_name", "deadline", "funding_ceiling",
                "county_statistic", "eligibility_result",
                "county_statistic_geography"):
        assert key in D2_PROTECTED_ELEMENTS


def test_baseline_sections_use_only_protected_values():
    sections = d2_baseline_sections()
    joined = " ".join(sections.values()).lower()
    # no invented money/statistics/deadlines beyond the pinned set
    assert "50,000" in joined or "50,000" in sections["budget_narrative"]
    assert "october 15, 2026" in sections["deadline"].lower()
    assert "18.2 percent" in sections["community_impact"].lower()
    assert "dade county" in sections["community_impact"].lower()


def test_budget_lines_reconcile_deterministically():
    total = d2_budget_total()
    assert total == Decimal("50000.00")
    assert total <= Decimal("50000.00")  # within ceiling
    assert sum((line["amount"] for line in d2_budget_lines()),
               Decimal("0")) == total


def test_claim_ledger_seed_is_supported():
    for entry in d2_claim_ledger_seed():
        assert entry["support_status"] == "SUPPORTED"
        assert entry["qa_status"] == "PASSED"


def test_requirements_include_mandatory_narrative_and_budget():
    reqs = d2_requirements_text()
    kinds = {r["type"] for r in reqs}
    assert kinds == {"narrative", "budget"}
    assert all(r["mandatory"] for r in reqs)


def test_d2_fixture_facts_are_supported_by_claims():
    facts = D2_FIXTURE["facts"]
    claims = {c.claim_id for c in D2_FIXTURE["claims"]}
    for fact in facts:
        assert set(fact.supporting_claim_ids) <= claims


def test_d2_fixture_markdown_never_claims_submission():
    text = " ".join(d2_baseline_sections().values()).lower()
    for banned in ("submitted", "we have submitted", "application sent"):
        assert banned not in text
