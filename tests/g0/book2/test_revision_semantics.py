"""B2.C8 tests — Versioning, Revision & Temporal Semantics.

Stable root + immutable revisions; material changes invalidate dependent
decisions; non-material changes do not; artifact version lineage stays intact.
"""
from __future__ import annotations

import copy

from prototype.g0.domain.models import (
    ApplicationProject,
    Artifact,
    ArtifactType,
    ArtifactVersion,
)
from prototype.g0.domain.revisions import (
    DecisionAnchor,
    Revision,
    RevisionSet,
    classify_revision,
    is_stale,
    version_chain,
)
from tools.g0.validate_domain import (
    load_revision_policy,
    validate_revision_policy,
)

POLICY = load_revision_policy()


def _rev(rid: str, num: int, terms: list[str], created: str = "2026-08-10T00:00:00Z"):
    return classify_revision(rid, num, terms, created, POLICY)


def _set(*revs: Revision) -> RevisionSet:
    rs = RevisionSet("opp-1", "GrantOpportunity")
    for r in revs:
        rs = rs.add(r)
    return rs


def test_live_revision_policy_passes():
    ok, report = validate_revision_policy(POLICY)
    assert ok, report["errors"]
    assert report["material_category_count"] >= 10


def test_reconstruct_application_against_revision_n():
    # rev1 (deadline) -> rev2 (formatting, non-material) -> rev3 (deadline moved)
    rev1 = _rev("rev-1", 1, ["deadline"])
    rev2 = _rev("rev-2", 2, ["formatting"])
    rev3 = _rev("rev-3", 3, ["deadline"])
    rs = _set(rev1, rev2, rev3)
    # application was built against rev1 and stays anchored there
    app = ApplicationProject("app-1", "org-42", "opp-1", rev1.revision_id)
    anchored = rs.get(app.opportunity_revision_id)
    assert anchored is not None and anchored.revision_id == "rev-1"
    assert anchored.revision_number == 1
    assert anchored.material is True          # deadline change was material
    # reconstructing against rev-1 reads the OLD terms, not the later ones
    assert "deadline" in anchored.changed_terms


def test_new_revision_does_not_mutate_old_decision():
    rev1 = _rev("rev-1", 1, ["deadline"])
    anchor = DecisionAnchor("eldec-1", rev1.revision_id, decision_kind="eligibility")
    rs1 = _set(rev1)
    rs2 = rs1.add(_rev("rev-2", 2, ["eligibility"]))
    # the old decision object and the old revision chain are unchanged
    assert anchor.revision_id == "rev-1"
    assert rs1.revisions == (rev1,)
    assert len(rs2.revisions) == 2
    assert rs2.revisions[0] is rev1             # same frozen revision object


def test_material_amendment_marks_dependent_state_stale():
    rev1 = _rev("rev-1", 1, ["deadline"])
    rev2 = _rev("rev-2", 2, ["eligibility"])    # material
    rs = _set(rev1, rev2)
    anchor = DecisionAnchor("eldec-1", "rev-1")
    assert is_stale(anchor, rs) is True


def test_non_material_formatting_change_need_not_invalidate_eligibility():
    rev1 = _rev("rev-1", 1, ["deadline"])
    rev2 = _rev("rev-2", 2, ["formatting"])     # non-material
    rs = _set(rev1, rev2)
    anchor = DecisionAnchor("eldec-1", "rev-1")
    assert rev2.material is False
    assert is_stale(anchor, rs) is False


def test_cancellation_is_material():
    rev = _rev("rev-9", 9, ["cancelled"])
    assert rev.material is True


def test_artifact_version_lineage_remains_intact():
    art = Artifact("art-1", ArtifactType.GRANT_PROPOSAL, "Proposal")
    v1 = ArtifactVersion("v-1", art.artifact_id, 1, "h1")
    v2 = ArtifactVersion("v-2", art.artifact_id, 2, "h2")
    v3 = ArtifactVersion("v-3", art.artifact_id, 3, "h3")
    chain = version_chain([v3, v1, v2])          # unordered input
    assert [v.version_number for v in chain] == [1, 2, 3]
    assert all(v.artifact_id == art.artifact_id for v in chain)


def test_version_gap_fails_closed():
    art = Artifact("art-1", ArtifactType.GRANT_PROPOSAL, "Proposal")
    v1 = ArtifactVersion("v-1", art.artifact_id, 1, "h1")
    v3 = ArtifactVersion("v-3", art.artifact_id, 3, "h3")
    try:
        version_chain([v1, v3])
        raise AssertionError("gap must raise")
    except ValueError as exc:
        assert "gap" in str(exc)


def test_version_chain_cannot_cross_roots():
    art_a = Artifact("art-a", ArtifactType.GRANT_PROPOSAL, "A")
    art_b = Artifact("art-b", ArtifactType.BUSINESS_PLAN, "B")
    va = ArtifactVersion("va-1", art_a.artifact_id, 1, "h1")
    vb = ArtifactVersion("vb-1", art_b.artifact_id, 1, "h1")
    try:
        version_chain([va, vb])
        raise AssertionError("cross-root chain must raise")
    except ValueError as exc:
        assert "roots" in str(exc)


# --- validator defect injection ------------------------------------------------

def test_unknown_root_rule_fails():
    data = copy.deepcopy(POLICY)
    data["root_rule"] = "mutate_in_place"
    ok, report = validate_revision_policy(data)
    assert not ok
    assert any("root_rule" in e for e in report["errors"])


def test_unknown_temporal_field_fails():
    data = copy.deepcopy(POLICY)
    data["temporal_fields"].append({"field": "watched_at", "semantic_role": "nope"})
    ok, report = validate_revision_policy(data)
    assert not ok
    assert any("not in B2.C8 semantic set" in e for e in report["errors"])


def test_duplicate_material_category_fails():
    data = copy.deepcopy(POLICY)
    data["material_change_categories"].append(
        dict(data["material_change_categories"][0]))
    ok, report = validate_revision_policy(data)
    assert not ok
    assert any("duplicated" in e for e in report["errors"])


def test_empty_material_category_terms_fail():
    data = copy.deepcopy(POLICY)
    data["material_change_categories"].append(
        {"category": "vibes", "affected_terms": []})
    ok, report = validate_revision_policy(data)
    assert not ok
    assert any("empty affected_terms" in e for e in report["errors"])
