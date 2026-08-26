"""B2.C13 tests — Artifact & Document Family Model.

Family coverage equals the client Phase 1 scope; version history is immutable;
a final package can never include a superseded version; mock artifacts are
visibly distinct and can never enter a real submission package.
"""
from __future__ import annotations

import copy

import pytest

from prototype.g0.domain.artifacts import (
    family_coverage,
    is_mock,
    package_versions,
    validate_package,
)
from prototype.g0.domain.models import (
    Artifact,
    ArtifactStatus,
    ArtifactType,
    ArtifactVersion,
)
from prototype.g0.domain.revisions import version_chain
from tools.g0.validate_domain import (
    load_artifact_families,
    validate_artifact_families,
)

POLICY = load_artifact_families()


def _art(art_id: str, atype: ArtifactType, status: ArtifactStatus = ArtifactStatus.DRAFT,
         **kw) -> Artifact:
    return Artifact(art_id, atype, art_id, status=status, **kw)


def test_live_artifact_families_passes():
    ok, report = validate_artifact_families(POLICY)
    assert ok, report["errors"]
    assert report["family_count"] == 10


def test_artifact_family_coverage_equals_client_phase1_scope():
    required = {f["artifact_type"] for f in POLICY["phase1_families"]}
    suite = [
        _art("a1", ArtifactType.GRANT_PROPOSAL),
        _art("a2", ArtifactType.BUSINESS_PLAN),
        _art("a3", ArtifactType.PITCH_DECK),
        _art("a4", ArtifactType.BUDGET_FINANCIAL),
        _art("a5", ArtifactType.PARTNERSHIP_MATERIAL),
        _art("a6", ArtifactType.TESTIMONIAL_MATERIAL),
        _art("a7", ArtifactType.GOAL_SHEET),
        _art("a8", ArtifactType.RESEARCH_REPORT),
        _art("a9", ArtifactType.QA_REPORT),
        _art("a10", ArtifactType.SUBMISSION_PACKAGE),
    ]
    covered, missing = family_coverage(suite, required)
    assert not missing, f"Phase 1 families missing: {missing}"
    assert covered == required
    # dropping one family leaves a visible gap
    _, missing = family_coverage(suite[:-1], required)
    assert "submission_package" in missing


def test_version_history_immutable():
    art = _art("art-1", ArtifactType.GRANT_PROPOSAL)
    v1 = ArtifactVersion("v-1", art.artifact_id, 1, "h1")
    with pytest.raises(Exception):
        v1.content_hash = "mutated"      # frozen dataclass -> AttributeError
    chain = version_chain([v1])
    assert chain == [v1]


def test_package_cannot_include_superseded_version():
    # supersession lives on the Artifact: once superseded, NONE of its versions
    # (old or newest) may enter a package
    art = _art("art-1", ArtifactType.GRANT_PROPOSAL, status=ArtifactStatus.SUPERSEDED)
    v1 = ArtifactVersion("v-1", art.artifact_id, 1, "h1")
    v2 = ArtifactVersion("v-2", art.artifact_id, 2, "h2")
    status = {"art-1": ArtifactStatus.SUPERSEDED}
    assert any("superseded" in e for e in validate_package([v1, v2], ["v-1"], status))
    assert any("superseded" in e for e in validate_package([v1, v2], ["v-2"], status))
    # an ACTIVE artifact's versions package cleanly
    active = _art("art-2", ArtifactType.GRANT_PROPOSAL, status=ArtifactStatus.DRAFT)
    va = ArtifactVersion("va-1", active.artifact_id, 1, "hA")
    status["art-2"] = ArtifactStatus.DRAFT
    assert validate_package([v1, v2, va], ["va-1"], status) == []


def test_package_unknown_version_fails_closed():
    art = _art("art-1", ArtifactType.GRANT_PROPOSAL)
    v1 = ArtifactVersion("v-1", art.artifact_id, 1, "h1")
    errors = validate_package([v1], ["ghost"], {"art-1": ArtifactStatus.DRAFT})
    assert any("unknown version" in e for e in errors)


def test_package_uses_latest_versions():
    art = _art("art-1", ArtifactType.GRANT_PROPOSAL)
    v1 = ArtifactVersion("v-1", art.artifact_id, 1, "h1")
    v2 = ArtifactVersion("v-2", art.artifact_id, 2, "h2")
    latest = package_versions([v1, v2])
    assert latest[art.artifact_id] is v2


def test_mock_artifact_visibly_distinguishable():
    real = _art("art-1", ArtifactType.GRANT_PROPOSAL, status=ArtifactStatus.SUBMISSION_READY)
    mock = _art("art-2", ArtifactType.GRANT_PROPOSAL, status=ArtifactStatus.MOCK)
    assert mock.status is ArtifactStatus.MOCK
    assert real.status is ArtifactStatus.SUBMISSION_READY
    assert is_mock(mock) is True and is_mock(real) is False
    assert mock.status is not real.status


def test_mock_version_cannot_enter_real_submission():
    mock_art = _art("art-2", ArtifactType.GRANT_PROPOSAL, status=ArtifactStatus.MOCK)
    v1 = ArtifactVersion("v-1", mock_art.artifact_id, 1, "h1")
    status = {"art-2": ArtifactStatus.MOCK}
    errors = validate_package([v1], ["v-1"], status, for_real_submission=True)
    assert any("MOCK" in e for e in errors)
    # a mock-only draft package (not for real submission) is allowed
    assert validate_package([v1], ["v-1"], status, for_real_submission=False) == []


# --- validator defect injection ------------------------------------------------

def test_missing_family_fails():
    data = copy.deepcopy(POLICY)
    data["phase1_families"] = [f for f in data["phase1_families"]
                               if f["artifact_type"] != "qa_report"]
    ok, report = validate_artifact_families(data)
    assert not ok
    assert any("phase1_families" in e for e in report["errors"])


def test_missing_version_rule_fails():
    data = copy.deepcopy(POLICY)
    data["version_rules"] = [r for r in data["version_rules"]
                             if r["rule"] != "no_superseded_in_package"]
    ok, report = validate_artifact_families(data)
    assert not ok
    assert any("no_superseded_in_package" in e for e in report["errors"])
