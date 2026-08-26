"""G0-B3-C20-C21 — validate retention + provenance chain policy.

Fail-closed checks:
  * all eight data classes D0..D7 are declared with retention policies and
    allowed deletion semantics from the known enum;
  * the provenance chain declares all nine stages and all eleven required
    relationships, plus the trace rule;
  * the provenance deletion rule is declared.
"""

from __future__ import annotations

import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[2]
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from tools.g0._common import (  # noqa: E402
    SOURCE_CONFIG_DIR,
    ValidationFailure,
    emit,
    load_yaml,
)

KNOWN_DELETION_SEMANTICS = {
    "DELETE_CONTENT", "TOMBSTONE_METADATA", "REVOKE_ACCESS", "ARCHIVE",
    "LEGAL_OPERATIONAL_HOLD",
}
REQUIRED_DATA_CLASSES = {f"D{i}" for i in range(8)}  # D0..D7

REQUIRED_CHAIN_STAGES = [
    "SourceRegistry", "CaptureEvent_SourceSnapshot", "ExtractionEvent",
    "NormalizationEvent", "EvidenceClaim_ExternalIdentifier_StatisticObservation",
    "PromotionEvent_CanonicalFact",
    "EligibilityDecision_MatchExplanation_ResearchFinding",
    "RequirementResponse_ProposalSection_BudgetLine",
    "ArtifactVersion_SubmissionPackage",
]
REQUIRED_RELATIONSHIPS = {
    "CAPTURED_FROM", "EXTRACTED_FROM", "NORMALIZED_FROM", "SUPPORTED_BY",
    "CONTRADICTED_BY", "DERIVED_FROM", "USED_IN", "SATISFIES",
    "GENERATED_FROM", "SUPERSEDES", "INVALIDATED_BY",
}


def validate_retention(cfg: dict, errors: list) -> None:
    classes = {c["class_id"] for c in cfg.get("data_classes", [])}
    missing = REQUIRED_DATA_CLASSES - classes
    if missing:
        errors.append(f"retention policy missing data classes: {sorted(missing)}")
    extra = classes - REQUIRED_DATA_CLASSES
    if extra:
        errors.append(f"unknown data classes: {sorted(extra)}")
    semantics = set(cfg.get("deletion_semantics", []))
    unknown = semantics - KNOWN_DELETION_SEMANTICS
    if unknown:
        errors.append(f"unknown deletion semantics: {sorted(unknown)}")
    for row in cfg.get("data_classes", []):
        allowed = set(row.get("deletion_semantics", []))
        bad = allowed - KNOWN_DELETION_SEMANTICS
        if bad:
            errors.append(f"{row['class_id']}: unknown allowed deletion "
                          f"semantics {sorted(bad)}")
    if not cfg.get("provenance_deletion_rule"):
        errors.append("provenance deletion rule must be declared")


def validate_provenance(cfg: dict, errors: list) -> None:
    stages = cfg.get("chain_stages", [])
    if stages != REQUIRED_CHAIN_STAGES:
        errors.append("chain_stages must be exactly the nine minimum stages in order")
    rels = set(cfg.get("relationships", []))
    missing = REQUIRED_RELATIONSHIPS - rels
    if missing:
        errors.append(f"provenance relationships missing: {sorted(missing)}")
    if not cfg.get("trace_rule"):
        errors.append("trace rule must be declared (missing hop = FAIL)")


def main() -> int:
    errors: list[str] = []
    try:
        retention = load_yaml(SOURCE_CONFIG_DIR / "retention_policy.yaml")
        provenance = load_yaml(SOURCE_CONFIG_DIR / "provenance_chain.yaml")
        validate_retention(retention, errors)
        validate_provenance(provenance, errors)
    except ValidationFailure as exc:
        errors.append(str(exc))
    ok = not errors
    return emit({
        "validator": "validate_retention_provenance",
        "status": "PASS" if ok else "FAIL",
        "errors": errors,
        "data_class_count": len(retention.get("data_classes", [])),
        "chain_stage_count": len(provenance.get("chain_stages", [])),
        "relationship_count": len(provenance.get("relationships", [])),
    })


if __name__ == "__main__":
    sys.exit(main())
