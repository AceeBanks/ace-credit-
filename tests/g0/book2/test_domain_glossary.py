"""B2.C1 tests — Domain Glossary & Ubiquitous Language.

The live glossary passes; injected defects (duplicate term, banned alias,
missing fields) fail closed. Cross-checks against Book 1 capability resource
types are added once the entity catalog exists (B2.C3).
"""
from __future__ import annotations

import copy
from pathlib import Path

import yaml

from tools.g0.validate_domain import load_glossary, validate_glossary

_ROOT = Path(__file__).resolve().parents[3]
REQUIRED_TERMS = {
    "Organization", "Person", "OrganizationRole", "Funder", "Recipient",
    "Applicant", "Partner", "Contact",
    "Program", "AssistanceListing", "GrantOpportunity", "OpportunityRevision",
    "Award", "FundingInstrument", "FundingCategory",
    "EligibilityRule", "EligibilityRuleSet", "EligibilityDecision",
    "EligibilityEvidence", "EligibilityStatus",
    "ApplicationProject", "ApplicationRevision", "Requirement",
    "RequirementResponse", "ProposalSection", "BusinessPlanSection",
    "Budget", "BudgetLine", "Artifact", "ArtifactVersion", "SubmissionPackage",
    "SourceSnapshot", "EvidenceClaim", "CanonicalFact", "StatisticObservation",
    "EvidenceLink", "ConflictState",
    "OutcomeFeedback", "AwardOutcome", "RejectionOutcome", "RevisionRequest",
}


def _live() -> dict:
    return load_glossary()


def test_live_glossary_passes():
    ok, report = validate_glossary(_live())
    assert ok, report["errors"]
    assert report["term_count"] >= 40


def test_all_required_classes_present():
    terms = {t["term"] for t in _live()["terms"]}
    missing = REQUIRED_TERMS - terms
    assert not missing, f"missing glossary terms: {sorted(missing)}"


def test_no_duplicate_terms():
    data = copy.deepcopy(_live())
    data["terms"].append(dict(data["terms"][0]))
    ok, report = validate_glossary(data)
    assert not ok
    assert report["duplicates"] == 1


def test_banned_alias_not_used_as_canonical_term():
    for t in _live()["terms"]:
        assert t["term"].lower() not in {b.lower() for b in _live()["banned_ambiguous_aliases"]}


def test_every_entry_has_required_fields():
    for t in _live()["terms"]:
        assert t["definition"] and t["what_it_is_not"] and t["identity_scope"]
        assert t["source_of_truth_book"] and t["common_confusions"]


def test_missing_definition_fails():
    data = copy.deepcopy(_live())
    del data["terms"][3]["definition"]
    ok, report = validate_glossary(data)
    assert not ok
    assert any("missing fields" in e for e in report["errors"])


def test_required_distinctions_are_explicit():
    """Plan-mandated pairwise distinctions surface in common_confusions."""
    by_term = {t["term"]: t for t in _live()["terms"]}
    pairs = [("Program", "GrantOpportunity"), ("GrantOpportunity", "OpportunityRevision"),
             ("ApplicationProject", "ApplicationRevision"),
             ("EvidenceClaim", "CanonicalFact"), ("Requirement", "ProposalSection"),
             ("Artifact", "SourceSnapshot")]
    for a, b in pairs:
        assert b in by_term[a]["common_confusions"], f"{a} must distinguish from {b}"


def test_every_book1_capability_resource_type_maps_to_glossary():
    """B2.C1: every Book 1 capability resource type maps to a domain object."""
    policy = yaml.safe_load((_ROOT / "config/g0/policy/capability_registry.yaml")
                            .read_text(encoding="utf-8"))
    resource_types = {r for c in policy["capabilities"] for r in c["resource_types"]}
    glossary = {t["term"] for t in _live()["terms"]}
    # mapping: capability resource type -> canonical glossary term
    mapping = {
        "organization_profile": "Organization",
        "opportunity": "GrantOpportunity",
        "rule_set": "EligibilityRuleSet",
        "eligibility_result": "EligibilityDecision",
        "match_result": "EligibilityDecision",
        "research_pack": "Artifact",
        "evidence_record": "EvidenceClaim",
        "application_project": "ApplicationProject",
        "application_blueprint": "Artifact",
        "application_draft": "Artifact",
        "business_plan_draft": "Artifact",
        "pitch_deck_draft": "Artifact",
        "goal_sheet_draft": "Artifact",
        "submission_package": "SubmissionPackage",
        "budget": "Budget",
        "qa_report": "Artifact",
        "artifact": "Artifact",
        "communication_draft": "Artifact",
        "communication_channel": "OrganizationRole",
        "system_state": "Artifact",
        "change_proposal": "Artifact",
        "eval_run": "Artifact",
        "funder_portal": "GrantOpportunity",
    }
    unmapped = resource_types - set(mapping)
    assert not unmapped, f"resource types without glossary mapping: {unmapped}"
    for rt, term in mapping.items():
        assert term in glossary, f"resource type {rt} maps to missing term {term}"
