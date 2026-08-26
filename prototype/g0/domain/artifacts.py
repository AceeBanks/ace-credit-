"""G0 Book 2 — B2.C13 artifact & document family model.

The client's complete Phase 1 document suite. Versions are immutable;
a final submission package can never include a superseded version; mock
artifacts are visibly distinguishable from approved/submission-ready ones
and can never enter a real package.
"""
from __future__ import annotations

from prototype.g0.domain.models import (
    Artifact,
    ArtifactStatus,
    ArtifactType,
    ArtifactVersion,
)


def family_coverage(artifacts: list[Artifact], phase1_types: set[str]) -> tuple[set[str], set[str]]:
    """(covered, missing) artifact types vs the required Phase 1 family set."""
    present = {a.artifact_type.value for a in artifacts}
    return present & phase1_types, phase1_types - present


def validate_package(versions: list[ArtifactVersion], package_refs: list[str],
                     artifact_status: dict[str, ArtifactStatus],
                     for_real_submission: bool = False) -> list[str]:
    """A package cannot reference a version whose artifact is SUPERSEDED.

    `versions` is the full known version history; `package_refs` the version
    ids selected for the package; `artifact_status` maps artifact_id -> status
    (supersession lives on the Artifact, not the version). Returns errors;
    caller treats non-empty as package rejection (fail closed).
    """
    by_id = {v.version_id: v for v in versions}
    errors: list[str] = []
    for ref in package_refs:
        if ref not in by_id:
            errors.append(f"package references unknown version '{ref}'")
            continue
        v = by_id[ref]
        if artifact_status.get(v.artifact_id) is ArtifactStatus.SUPERSEDED:
            errors.append(f"package includes superseded version '{ref}' "
                          f"(artifact {v.artifact_id})")
        if for_real_submission and artifact_status.get(v.artifact_id) is ArtifactStatus.MOCK:
            errors.append(f"package includes MOCK version '{ref}' in a real submission")
    return errors


def package_versions(artifact_versions: list[ArtifactVersion]) -> dict[str, ArtifactVersion]:
    """Latest (highest-numbered) version per artifact id."""
    latest: dict[str, ArtifactVersion] = {}
    for v in artifact_versions:
        cur = latest.get(v.artifact_id)
        if cur is None or v.version_number > cur.version_number:
            latest[v.artifact_id] = v
    return latest


def is_mock(artifact: Artifact) -> bool:
    return artifact.status is ArtifactStatus.MOCK
