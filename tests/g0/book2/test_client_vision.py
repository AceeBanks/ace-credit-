"""B2.C18 tests — Client Vision Coverage Matrix.

Proves the ontology can represent the product the client asked for: intake,
research & matching, document generation, quality, and submission-ready
output — plus the eight grant categories via metadata, never eight entity
types. Any uncovered Phase 1 requirement blocks ratification.
"""
from __future__ import annotations

import copy

from tools.g0.validate_domain import (
    load_client_vision_matrix,
    validate_client_vision_matrix,
)

MATRIX = load_client_vision_matrix()


def test_live_matrix_passes():
    ok, report = validate_client_vision_matrix(MATRIX)
    assert ok, report["errors"]
    assert report["coverage_count"] >= 30


def test_every_phase1_requirement_covered():
    for row in MATRIX["coverage"]:
        assert row["covered"] is True, f"{row['client_requirement_id']} uncovered"
        assert row["gap"] == "" or "submission" in row["gap"].lower(), (
            f"{row['client_requirement_id']} has unrecorded gap: {row['gap']}")


def test_all_five_areas_represented():
    areas = {"CV-I": "intake", "CV-R": "research", "CV-D": "document",
             "CV-Q": "quality", "CV-S": "submission"}
    ids = {r["client_requirement_id"][:4] for r in MATRIX["coverage"]}
    assert set(areas) == ids, f"missing areas: {set(areas) - ids}"


def test_intake_coverage_complete():
    intakes = [r for r in MATRIX["coverage"] if r["client_requirement_id"].startswith("CV-I")]
    concepts = {r["requirement"] for r in intakes}
    for c in ("organization identity", "founder/contact", "business concept",
              "mission/vision", "goals", "target population", "geography",
              "program/project concept", "financial assumptions",
              "existing partnerships/evidence"):
        assert c in concepts, c


def test_research_and_matching_coverage_complete():
    rows = [r for r in MATRIX["coverage"] if r["client_requirement_id"].startswith("CV-R")]
    concepts = {r["requirement"] for r in rows}
    for c in ("opportunity", "funder", "program", "historical awards/winners",
              "eligibility rules/decision", "match explanation",
              "research evidence", "community statistics"):
        assert c in concepts, c


def test_document_generation_coverage_complete():
    rows = [r for r in MATRIX["coverage"] if r["client_requirement_id"].startswith("CV-D")]
    concepts = {r["requirement"] for r in rows}
    for c in ("proposal", "business plan", "pitch deck", "financials",
              "partnership/testimonial material", "goal sheets",
              "research reports"):
        assert c in concepts, c


def test_quality_coverage_complete():
    rows = [r for r in MATRIX["coverage"] if r["client_requirement_id"].startswith("CV-Q")]
    concepts = {r["requirement"] for r in rows}
    for c in ("requirement coverage", "factuality evidence",
              "cross-document consistency", "alignment", "QA reports",
              "review state"):
        assert c in concepts, c


def test_submission_ready_output_without_submission_claim():
    row = next(r for r in MATRIX["coverage"] if r["client_requirement_id"] == "CV-S01")
    assert row["covered"] is True
    assert "never represents actual submission" in row["gap"]


def test_eight_grant_categories_single_opportunity_entity():
    assert len(MATRIX["grant_categories"]) == 8
    assert MATRIX["opportunity_entity_rule"] == \
        "single_grant_opportunity_entity_with_category_metadata"
    # no eight opportunity entity types anywhere in the matrix
    entities = {e for row in MATRIX["coverage"] for e in row["domain_entities"]}
    opp_entities = {e for e in entities if "Opportunity" in e}
    assert opp_entities == {"GrantOpportunity", "OpportunityRevision"}


def test_domain_entities_are_known_domain_types():
    """Every domain_entities entry is a real domain object: either a catalog
    entity type or a prototype model class. Invented types are rejected."""
    import inspect

    from prototype.g0.domain import models
    from tools.g0.validate_domain import load_entity_types
    known = {e["entity_type"] for e in load_entity_types()["entity_types"]}
    known |= {name for name, obj in inspect.getmembers(models, inspect.isclass)
              if obj.__module__ == models.__name__}
    for row in MATRIX["coverage"]:
        for ent in row["domain_entities"]:
            assert ent in known, f"{row['client_requirement_id']}: unknown entity {ent}"


# --- validator defect injection ------------------------------------------------

def test_uncovered_requirement_fails():
    data = copy.deepcopy(MATRIX)
    data["coverage"][0]["covered"] = False
    ok, report = validate_client_vision_matrix(data)
    assert not ok
    assert any("uncovered" in e for e in report["errors"])


def test_wrong_category_set_fails():
    data = copy.deepcopy(MATRIX)
    data["grant_categories"] = data["grant_categories"][:7]
    ok, report = validate_client_vision_matrix(data)
    assert not ok
    assert any("grant_categories" in e for e in report["errors"])
