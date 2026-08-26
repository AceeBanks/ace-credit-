"""B2.C15 tests — CommonGrants Interoperability Contract.

Standards compatibility without reducing internal richness. Mapping classes are
exactly one of EXACT/EXTENSION/INTERNAL_ONLY/EXTERNAL_ONLY/LOSSY; EXACT fields
round-trip with semantic equality; LOSSY is explicit and test-visible; the
schema pin fails closed until the real CommonGrants schemas are vendored.
"""
from __future__ import annotations

import copy
from decimal import Decimal

import pytest

from prototype.g0.domain.common_grants import (
    check_schema_version,
    classify_rows,
    from_common_grants,
    lossy_fields,
    round_trip,
    to_common_grants,
)
from prototype.g0.domain.models import CommonGrantsExtension
from tools.g0.validate_domain import (
    load_common_grants_mapping,
    validate_common_grants_mapping,
)

MAPPING = load_common_grants_mapping()


def test_live_mapping_passes():
    ok, report = validate_common_grants_mapping(MAPPING)
    assert ok, report["errors"]
    assert report["row_count"] >= 12


def test_mapping_classes_exactly_one():
    classes = classify_rows(MAPPING)
    assert set(classes) == {"EXACT", "EXTENSION", "INTERNAL_ONLY", "EXTERNAL_ONLY", "LOSSY"}
    for cls in ("EXACT", "EXTENSION", "LOSSY"):
        assert classes[cls]


def test_opportunity_round_trip():
    internal = {"opportunity_id": "opp-1", "title": "Community Grant FY2026",
                "status": "ACTIVE", "deadline (revision)": "2026-10-15"}
    ok, mismatches = round_trip(internal, MAPPING, "GrantOpportunity")
    assert ok, mismatches
    # LOSSY fields survive the config's declared reverse transform
    assert to_common_grants(internal, MAPPING, "GrantOpportunity")["opportunity_id"] == "opp-1"


def test_application_round_trip():
    internal = {"project_id": "app-1", "organization_id": "org-42",
                "opportunity_id": "opp-1", "state": "DRAFTING",
                "opportunity_revision_id": "opp_rev-2"}
    ok, mismatches = round_trip(internal, MAPPING, "ApplicationProject")
    assert ok, mismatches


def test_award_round_trip_with_decimal():
    internal = {"award_id": "award-1", "amount": Decimal("75000.00"),
                "currency": "USD", "recipient_id": "org-42",
                "award_date": "2026-06-01"}
    ext = to_common_grants(internal, MAPPING, "Award")
    assert ext["funding_amount"] == "75000.00"        # decimal -> string
    ok, mismatches = round_trip(internal, MAPPING, "Award")
    assert ok, mismatches
    back = from_common_grants(ext, MAPPING, "Award")
    assert back["amount"] == Decimal("75000.00")      # string -> decimal


def test_extension_preservation():
    internal = {"project_id": "app-1", "organization_id": "org-42",
                "opportunity_id": "opp-1", "state": "DRAFTING",
                "opportunity_revision_id": "opp_rev-2"}
    ext = to_common_grants(internal, MAPPING, "ApplicationProject")
    assert ext["cgx_opportunity_revision_id"] == "opp_rev-2"   # extension carried
    # an unknown cgx_ field coming back in is preserved, not dropped
    ext["cgx_qa_status"] = "QA_PENDING"
    back = from_common_grants(ext, MAPPING, "ApplicationProject")
    assert back["cgx_qa_status"] == "QA_PENDING"


def test_unknown_non_extension_field_rejected():
    ext = {"application_id": "app-1", "mystery_field": "nope"}
    with pytest.raises(ValueError):
        from_common_grants(ext, MAPPING, "ApplicationProject")


def test_lossy_fields_explicit_and_visible():
    losses = lossy_fields(MAPPING, "GrantOpportunity")
    assert losses and all(r["mapping_class"] == "LOSSY" for r in losses)
    for r in losses:
        assert r["loss_notes"]                    # loss is documented, not silent
    assert any("deadline" in r["internal_field"] for r in losses)


def test_schema_version_unpinned_fails_closed():
    ok, msg = check_schema_version(MAPPING, "0.1.0")
    assert ok is False
    assert "unpinned" in msg
    # a mismatched vendored pin also fails
    pinned = {**MAPPING, "common_grants_schema_version": "0.2.0"}
    ok, msg = check_schema_version(pinned, "0.1.0")
    assert ok is False and "mismatch" in msg
    ok, msg = check_schema_version(pinned, "0.2.0")
    assert ok is True


def test_external_id_mapping_does_not_replace_internal_identity():
    ext = {"application_id": "app-1", "opportunity_id": "opp-1"}
    back = from_common_grants(ext, MAPPING, "ApplicationProject")
    assert back["project_id"] == "app-1"          # internal id stays authoritative
    extid = CommonGrantsExtension("cgx_1", "ApplicationProject",
                                  "opportunity_id", mapping_class="EXTENSION",
                                  value="opp-1")
    assert extid.extension_id.startswith("cgx_")  # project-owned namespace
    assert extid.internal_field == "opportunity_id"


# --- validator defect injection ------------------------------------------------

def test_missing_column_fails():
    data = copy.deepcopy(MAPPING)
    del data["entities"][0]["rows"][0]["loss_notes"]
    ok, report = validate_common_grants_mapping(data)
    assert not ok
    assert any("missing columns" in e for e in report["errors"])


def test_duplicate_cg_target_fails():
    data = copy.deepcopy(MAPPING)
    dup = dict(data["entities"][0]["rows"][0])
    dup["internal_field"] = "another_field"
    data["entities"][0]["rows"].append(dup)       # same common_grants_field twice
    ok, report = validate_common_grants_mapping(data)
    assert not ok
    assert any("common_grants_field duplicated" in e for e in report["errors"])
