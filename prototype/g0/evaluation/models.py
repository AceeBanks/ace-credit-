"""G0-B7-C3/C4 — Evaluation core models (provisional executable form).

EvalCase, EvalCorpusVersion, EvalSuite, EvalRun and MetricBundle implement
the project-owned evaluation contracts (EVAL-LAW-014). Cases inherit Book 5
lineage semantics; corpus versions are immutable; every quality claim binds
baseline + corpus + suite + run (EVAL-LAW-001/002).
"""
from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any

from prototype.g0.evidence.eval_lineage import (
    EvalLineageError,
    assert_unchanged,
    validate_eval_case as validate_lineage_case,
)

CASE_TYPES = (
    "deterministic_rule", "structured_extraction", "grant_opportunity",
    "organization_profile", "eligibility", "matching", "research",
    "drafting", "budget", "qa", "personal_hermes_interaction",
    "ceo_orchestration", "worker_execution", "security_adversarial",
    "memory_reconstruction", "tool_execution",
)

CORPUS_CLASSES = (
    "GOLDEN_PUBLIC", "GOLDEN_SYNTHETIC", "GOLDEN_HUMAN_REVIEWED",
    "TENANT_PRIVATE_APPROVED", "ADVERSARIAL", "REGRESSION",
    "SHADOW_PRODUCTION", "HOLDOUT",
)

PRIVACY_CLASSES = (
    "PUBLIC_SOURCE", "GOLDEN_SYNTHETIC", "GOLDEN_HUMAN_REVIEWED",
    "TENANT_PRIVATE_APPROVED", "ADVERSARIAL", "REGRESSION",
    "SHADOW_PRODUCTION", "HOLDOUT",
)

LABEL_ORIGINS = (
    "HUMAN_REVIEWER", "HUMAN_ATTESTED", "MODEL_GENERATED", "SYNTHETIC",
    "DERIVED_FROM_EVIDENCE",
)


class EvalError(ValueError):
    """Raised when an evaluation contract is violated (fail closed)."""


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _canonical(obj: Any) -> str:
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), default=str)


def content_hash(obj: Any) -> str:
    return hashlib.sha256(_canonical(obj).encode("utf-8")).hexdigest()[:32]


# ---------------------------------------------------------------------
# EvalCase
# ---------------------------------------------------------------------

@dataclass(frozen=True)
class EvalCase:
    eval_case_id: str
    case_type: str
    corpus_version_id: str
    input_fixture_refs: tuple[str, ...]
    expected_assertions: tuple[dict, ...]
    privacy_class: str
    tenant_scope: str | None
    label_origin: str
    created_at: str
    source_lineage_refs: tuple[str, ...] = ()
    domain_fixture_refs: tuple[str, ...] = ()
    decision_artifact_refs: tuple[str, ...] = ()
    rubric_refs: tuple[str, ...] = ()
    label_reviewer: str | None = None
    valid_for_versions: tuple[str, ...] = ()
    content_hash: str = ""

    def __post_init__(self) -> None:
        if self.case_type not in CASE_TYPES:
            raise EvalError(f"unknown case_type {self.case_type!r}")
        if self.privacy_class not in PRIVACY_CLASSES:
            raise EvalError(f"unknown privacy_class {self.privacy_class!r}")
        if self.label_origin not in LABEL_ORIGINS:
            raise EvalError(f"unknown label_origin {self.label_origin!r}")
        # EVAL-LAW-007 / EVAL-001: lineage required
        if not self.source_lineage_refs and not self.domain_fixture_refs \
                and not self.input_fixture_refs:
            raise EvalError("eval case without lineage (EVAL-LAW-007)")
        if not self.decision_artifact_refs and not self.input_fixture_refs:
            raise EvalError("eval case without decision/artifact refs (EVAL-001)")
        if not self.content_hash:
            object.__setattr__(self, "content_hash",
                               content_hash(self._payload()))

    def _payload(self) -> dict:
        return {
            "eval_case_id": self.eval_case_id,
            "case_type": self.case_type,
            "corpus_version_id": self.corpus_version_id,
            "source_lineage_refs": list(self.source_lineage_refs),
            "domain_fixture_refs": list(self.domain_fixture_refs),
            "input_fixture_refs": list(self.input_fixture_refs),
            "decision_artifact_refs": list(self.decision_artifact_refs),
            "expected_assertions": list(self.expected_assertions),
            "privacy_class": self.privacy_class,
            "tenant_scope": self.tenant_scope,
            "label_origin": self.label_origin,
        }

    def to_dict(self) -> dict:
        return {
            **self._payload(),
            "created_at": self.created_at,
            "rubric_refs": list(self.rubric_refs),
            "label_reviewer": self.label_reviewer,
            "valid_for_versions": list(self.valid_for_versions),
            "content_hash": self.content_hash,
        }

    @staticmethod
    def from_governed_dict(data: dict) -> "EvalCase":
        """Build from a validated lineage case (Book 5 EVAL-001..005).

        Book 5's validate_eval_case expects source_snapshot_refs /
        domain_fixture_refs / decision_artifact_refs (EVAL-001) plus
        privacy_classification / split_membership / governance_approval
        (EVAL-002/005). The raw dict is translated so the model field names
        (source_lineage_refs, input_fixture_refs) stay the EvalCase contract
        while lineage validation uses the Book 5 vocabulary.
        """
        raw = dict(data)
        raw.setdefault("source_snapshot_refs",
                       list(raw.get("source_lineage_refs", [])))
        raw.setdefault("domain_fixture_refs",
                       list(raw.get("domain_fixture_refs", [])))
        raw.setdefault("decision_artifact_refs",
                       list(raw.get("decision_artifact_refs", [])))
        raw.setdefault("label_reviewer", data.get("label_reviewer"))
        raw.setdefault("split_membership", "UNASSIGNED")
        raw.setdefault("label_origin", data.get("label_origin"))
        # translate Book 7 corpus privacy classes into the Book 5 lineage
        # vocabulary; TENANT_PRIVATE_APPROVED maps to the governed class
        privacy = raw.get("privacy_class")
        if privacy == "TENANT_PRIVATE_APPROVED":
            privacy = "TENANT_PRIVATE"
        raw.setdefault("privacy_classification", privacy)
        if data.get("label_origin") == "MODEL_GENERATED" and \
                data.get("presented_as_human_gold"):
            raise EvalError(
                "model-generated label presented as human gold (EVAL-002)")
        try:
            governed = validate_lineage_case(case=raw)
        except EvalLineageError as exc:
            raise EvalError(f"lineage validation failed: {exc}") from exc
        return EvalCase(
            eval_case_id=governed["eval_case_id"],
            case_type=governed["case_type"],
            corpus_version_id=governed["corpus_version_id"],
            input_fixture_refs=tuple(data.get("input_fixture_refs", [])),
            expected_assertions=tuple(data.get("expected_assertions", [])),
            privacy_class=data.get("privacy_class",
                                   governed["privacy_classification"]),
            tenant_scope=data.get("tenant_scope"),
            label_origin=governed["label_origin"],
            created_at=governed["created_at"],
            source_lineage_refs=tuple(data.get("source_lineage_refs", [])),
            domain_fixture_refs=tuple(
                data.get("domain_fixture_refs", [])),
            decision_artifact_refs=tuple(
                governed.get("decision_artifact_refs", [])),
            rubric_refs=tuple(data.get("rubric_refs", [])),
            label_reviewer=governed.get("label_reviewer"),
            valid_for_versions=tuple(data.get("valid_for_versions", [])),
        )


# ---------------------------------------------------------------------
# EvalCorpusVersion — immutable
# ---------------------------------------------------------------------

@dataclass(frozen=True)
class EvalCorpusVersion:
    corpus_version_id: str
    corpus_class: str
    version: int
    case_ids: tuple[str, ...]
    created_at: str
    split_membership: str = "UNASSIGNED"
    parent_version_id: str | None = None
    composition_report_ref: str | None = None
    content_hash: str = ""

    def __post_init__(self) -> None:
        if self.corpus_class not in CORPUS_CLASSES:
            raise EvalError(f"unknown corpus_class {self.corpus_class!r}")
        if self.version < 1:
            raise EvalError("corpus version must be >= 1")
        if not self.content_hash:
            object.__setattr__(self, "content_hash",
                               content_hash(self._payload()))

    def _payload(self) -> dict:
        return {
            "corpus_version_id": self.corpus_version_id,
            "corpus_class": self.corpus_class,
            "version": self.version,
            "case_ids": list(self.case_ids),
            "parent_version_id": self.parent_version_id,
            "split_membership": self.split_membership,
        }

    def to_dict(self) -> dict:
        return {
            **self._payload(),
            "created_at": self.created_at,
            "composition_report_ref": self.composition_report_ref,
            "content_hash": self.content_hash,
        }

    def assert_unchanged(self) -> None:
        """EVAL-LAW-002 / corpus immutability: recompute and compare."""
        if content_hash(self._payload()) != self.content_hash:
            raise EvalError(
                f"corpus {self.corpus_version_id} mutated; versions are "
                "immutable (additions create a new version)")


# ---------------------------------------------------------------------
# EvalSuite
# ---------------------------------------------------------------------

@dataclass(frozen=True)
class EvalSuite:
    suite_id: str
    suite_version: int
    name: str
    target_capability_or_class: str
    corpus_version_id: str
    case_ids: tuple[str, ...]
    evaluator_ids: tuple[str, ...]
    hard_gate_dimensions: tuple[str, ...]
    created_at: str = ""
    content_hash: str = ""

    def __post_init__(self) -> None:
        if not self.created_at:
            object.__setattr__(self, "created_at", _now())
        if not self.content_hash:
            object.__setattr__(self, "content_hash",
                               content_hash(self._payload()))

    def _payload(self) -> dict:
        return {
            "suite_id": self.suite_id,
            "suite_version": self.suite_version,
            "name": self.name,
            "target_capability_or_class": self.target_capability_or_class,
            "corpus_version_id": self.corpus_version_id,
            "case_ids": list(self.case_ids),
            "evaluator_ids": list(self.evaluator_ids),
            "hard_gate_dimensions": list(self.hard_gate_dimensions),
        }

    def to_dict(self) -> dict:
        return {**self._payload(), "created_at": self.created_at,
                "content_hash": self.content_hash}


# ---------------------------------------------------------------------
# MetricBundle — visible dimensions, no opaque score
# ---------------------------------------------------------------------

@dataclass(frozen=True)
class MetricBundle:
    metric_bundle_id: str
    dimensions: tuple[dict, ...]
    created_at: str = ""

    def __post_init__(self) -> None:
        if not self.created_at:
            object.__setattr__(self, "created_at", _now())
        for dim in self.dimensions:
            if not dim.get("dimension_id"):
                raise EvalError("metric dimension without dimension_id")
            if dim.get("direction") not in ("higher_is_better", "lower_is_better"):
                raise EvalError(f"dimension {dim.get('dimension_id')} "
                                "missing/invalid direction")

    def to_dict(self) -> dict:
        return {"metric_bundle_id": self.metric_bundle_id,
                "dimensions": list(self.dimensions),
                "created_at": self.created_at}

    def dimension(self, dimension_id: str) -> dict | None:
        for dim in self.dimensions:
            if dim.get("dimension_id") == dimension_id:
                return dim
        return None


# ---------------------------------------------------------------------
# EvalRun
# ---------------------------------------------------------------------

@dataclass(frozen=True)
class EvalRun:
    eval_run_id: str
    suite_id: str
    suite_version: int
    corpus_version_id: str
    subject_ref: str
    subject_version: str
    subject_role: str
    metric_bundle_id: str
    status: str = "RUNNING"
    started_at: str = ""
    completed_at: str | None = None
    per_case_results: tuple[dict, ...] = ()

    def __post_init__(self) -> None:
        if not self.started_at:
            object.__setattr__(self, "started_at", _now())
        if self.subject_role not in ("BASELINE", "CANDIDATE",
                                     "REGRESSION_SUBJECT", "CONTROL"):
            raise EvalError(f"invalid subject_role {self.subject_role!r}")
        if self.status not in ("RUNNING", "COMPLETED", "FAILED", "ABORTED"):
            raise EvalError(f"invalid status {self.status!r}")

    def to_dict(self) -> dict:
        return {
            "eval_run_id": self.eval_run_id,
            "suite_id": self.suite_id,
            "suite_version": self.suite_version,
            "corpus_version_id": self.corpus_version_id,
            "subject_ref": self.subject_ref,
            "subject_version": self.subject_version,
            "subject_role": self.subject_role,
            "metric_bundle_id": self.metric_bundle_id,
            "status": self.status,
            "started_at": self.started_at,
            "completed_at": self.completed_at,
            "per_case_results": list(self.per_case_results),
        }
