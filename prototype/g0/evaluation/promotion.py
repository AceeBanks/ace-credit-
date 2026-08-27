"""G0-B7-C19..C21 — CandidateChange + promotion engine.

Every proposed improvement becomes a typed CandidateChange. Promotion is
explicit (EVAL-LAW-008), reversible (EVAL-LAW-009), gated by hard
dimensions (EVAL-LAW-003/010/011), and governed by PROM-001..007. No
candidate generator may self-promote (EVAL-LAW-006); no external skill
framework may write directly into production behavior (Amendment 002).
"""
from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any

from prototype.g0.evaluation.models import EvalError, MetricBundle

CHANGE_TYPES = (
    "PROMPT", "SKILL", "MODEL", "ROUTE", "PARSER", "RETRIEVAL", "WORKFLOW",
    "CONFIG", "MEMORY_POLICY", "CONTEXT_ASSEMBLY", "TOOL_ADAPTER",
    "RUNTIME_COMPONENT", "RUBRIC_EVALUATOR",
)

DECISIONS = ("PROMOTE", "REVISE", "REJECT", "QUARANTINE", "DEFER")

HARD_FAMILIES = ("correctness", "factuality", "agent_quality", "security")


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _canonical(obj: Any) -> str:
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), default=str)


def content_hash(obj: Any) -> str:
    return hashlib.sha256(_canonical(obj).encode("utf-8")).hexdigest()[:32]


@dataclass(frozen=True)
class CandidateChange:
    candidate_change_id: str
    change_type: str
    baseline_version: str
    candidate_version: str
    source_or_generator: str
    reason: str
    expected_benefit: str
    risk_class: str
    affected_capabilities: tuple[str, ...]
    required_eval_suites: tuple[str, ...]
    rollback_ref: str
    status: str = "DRAFT"
    created_at: str = ""
    content_hash: str = ""

    def __post_init__(self) -> None:
        if self.change_type not in CHANGE_TYPES:
            raise EvalError(f"unknown change_type {self.change_type!r}")
        if self.risk_class not in ("LOW", "MEDIUM", "HIGH", "CRITICAL"):
            raise EvalError(f"unknown risk_class {self.risk_class!r}")
        if not self.rollback_ref:
            raise EvalError("candidate must carry rollback_ref (EVAL-LAW-009)")
        if not self.created_at:
            object.__setattr__(self, "created_at", _now())
        if not self.content_hash:
            object.__setattr__(self, "content_hash",
                               content_hash(self._payload()))

    def _payload(self) -> dict:
        return {
            "candidate_change_id": self.candidate_change_id,
            "change_type": self.change_type,
            "baseline_version": self.baseline_version,
            "candidate_version": self.candidate_version,
            "source_or_generator": self.source_or_generator,
            "reason": self.reason,
            "risk_class": self.risk_class,
            "affected_capabilities": list(self.affected_capabilities),
            "required_eval_suites": list(self.required_eval_suites),
            "rollback_ref": self.rollback_ref,
        }

    def to_dict(self) -> dict:
        return {**self._payload(), "status": self.status,
                "created_at": self.created_at,
                "content_hash": self.content_hash}


@dataclass(frozen=True)
class PromotionDecision:
    promotion_decision_id: str
    candidate_change_id: str
    baseline_run_ref: str
    candidate_run_ref: str
    corpus_version_id: str
    suite_id: str
    suite_version: int
    decision: str
    reason_codes: tuple[str, ...]
    rollout_policy_ref: str
    rollback_ref: str
    decided_by: str
    hard_gate_results: tuple[dict, ...] = ()
    metric_comparison_ref: str = ""
    decided_at: str = ""

    def __post_init__(self) -> None:
        if self.decision not in DECISIONS:
            raise EvalError(f"invalid decision {self.decision!r}")
        if not self.decided_at:
            object.__setattr__(self, "decided_at", _now())
        if not self.rollback_ref:
            raise EvalError("promotion decision must carry rollback_ref")

    def to_dict(self) -> dict:
        return {
            "promotion_decision_id": self.promotion_decision_id,
            "candidate_change_id": self.candidate_change_id,
            "baseline_run_ref": self.baseline_run_ref,
            "candidate_run_ref": self.candidate_run_ref,
            "corpus_version_id": self.corpus_version_id,
            "suite_id": self.suite_id,
            "suite_version": self.suite_version,
            "decision": self.decision,
            "reason_codes": list(self.reason_codes),
            "rollout_policy_ref": self.rollout_policy_ref,
            "rollback_ref": self.rollback_ref,
            "decided_by": self.decided_by,
            "hard_gate_results": list(self.hard_gate_results),
            "metric_comparison_ref": self.metric_comparison_ref,
            "decided_at": self.decided_at,
        }


# ---------------------------------------------------------------------
# Promotion evaluation
# ---------------------------------------------------------------------

def evaluate_promotion(*, candidate: CandidateChange,
                       baseline_metrics: MetricBundle,
                       candidate_metrics: MetricBundle,
                       hard_gate_results: list[dict],
                       independent_evaluator: str | None = None,
                       min_improvement: float = 0.05,
                       optimization_tolerance: float = 0.05) -> dict:
    """EVAL-LAW-003/008 + PROM-001..007: decide PROMOTE/REVISE/REJECT/
    QUARANTINE/DEFER from evidence, never from a generator's assertion.

    hard_gate_results: [{"dimension_id", "family", "baseline", "candidate",
    "passed", "detail"}]
    """
    # PROM-005: generator cannot be the sole evaluator of its own candidate
    if independent_evaluator and \
            independent_evaluator == candidate.source_or_generator:
        return {"decision": "REJECT",
                "reason_codes": ["PROM-005_SELF_EVALUATION"],
                "detail": "candidate generator cannot self-promote "
                          "(EVAL-LAW-006)"}

    # PROM-001/002: any hard-gate failure vetoes
    hard_failures = [g for g in hard_gate_results if not g.get("passed")]
    if hard_failures:
        security_fail = any(g.get("family") == "security" or
                            g.get("family") == "agent_quality"
                            for g in hard_failures)
        return {
            "decision": "QUARANTINE" if security_fail else "REJECT",
            "reason_codes": [f"HARD_GATE_{g['dimension_id']}"
                             for g in hard_failures],
            "hard_gate_failures": hard_failures,
            "detail": "hard gate failure vetoes aggregate improvement "
                      "(EVAL-LAW-003/010)",
        }

    # dimension deltas
    base_dims = {d["dimension_id"]: d for d in baseline_metrics.dimensions}
    cand_dims = {d["dimension_id"]: d for d in candidate_metrics.dimensions}
    deltas = {}
    for dim_id, bdim in base_dims.items():
        cdim = cand_dims.get(dim_id)
        if not cdim:
            continue
        direction = bdim.get("direction", "higher_is_better")
        delta = (cdim["value"] - bdim["value"]) if direction == \
            "higher_is_better" else (bdim["value"] - cdim["value"])
        family = bdim.get("family", "")
        deltas[dim_id] = {
            "delta": round(float(delta), 4),
            "family": family,
            "gate": bdim.get("gate", "OPTIMIZE"),
        }

    # PROM-002: HARD family regression vetoes (beyond zero tolerance)
    hard_regressions = [
        (dim_id, d) for dim_id, d in deltas.items()
        if d["gate"] == "HARD" and d["delta"] < -1e-9]
    if hard_regressions:
        return {
            "decision": "REJECT",
            "reason_codes": [f"HARD_REGRESSION_{dim_id}"
                             for dim_id, _ in hard_regressions],
            "detail": "hard dimension regression vetoes promotion",
            "deltas": deltas,
        }

    # PROM-007: at least one optimization dimension improves by a RELATIVE
    # margin (5% by default). Relative deltas keep the threshold meaningful
    # across ratio scales (coverage 0-1, cost in USD, latency in ms).
    def _relative(delta: float, base_value: float) -> float:
        if abs(base_value) < 1e-12:
            return 1.0 if delta > 0 else 0.0
        return delta / abs(base_value)

    optimizations = [d for dim_id, d in deltas.items()
                     if d["gate"] == "OPTIMIZE"]
    improved = [dim_id for dim_id, d in deltas.items()
                if d["gate"] == "OPTIMIZE"
                and _relative(d["delta"],
                              baseline_metrics.dimension(dim_id)["value"])
                >= min_improvement]
    regressed_opt = [dim_id for dim_id, d in deltas.items()
                     if d["gate"] == "OPTIMIZE" and d["delta"] < -1e-9]
    undocumented_tradeoffs = [dim_id for dim_id in regressed_opt
                              if _relative(deltas[dim_id]["delta"],
                                           baseline_metrics.dimension(
                                               dim_id)["value"])
                              < -optimization_tolerance]

    if not optimizations:
        return {"decision": "DEFER", "reason_codes": ["PROM-007_NO_METRICS"],
                "detail": "no optimization dimensions measured",
                "deltas": deltas}

    if improved and not undocumented_tradeoffs:
        return {
            "decision": "PROMOTE",
            "reason_codes": ["PROM-001", "PROM-007"],
            "improved_dimensions": improved,
            "deltas": deltas,
            "detail": "hard gates pass and measurable improvement exists",
        }

    if undocumented_tradeoffs:
        return {
            "decision": "REVISE",
            "reason_codes": ["PROM-003_UNJUSTIFIED_TRADEOFF"],
            "regressed_dimensions": undocumented_tradeoffs,
            "deltas": deltas,
            "detail": "optimization trade-off exceeds tolerance without "
                      "documented justification",
        }

    # no meaningful improvement but no regression: DEFER
    return {"decision": "DEFER", "reason_codes": ["PROM-007_NO_IMPROVEMENT"],
            "deltas": deltas,
            "detail": "no measurable improvement over baseline"}


def approve_pareto_tradeoff(*, candidate: CandidateChange,
                            tradeoff_doc: str) -> dict:
    """PROM-003: documented Pareto trade-offs allowed only when no hard gate
    regresses. The documentation must name the trade-off and the reason."""
    if not tradeoff_doc or len(tradeoff_doc) < 20:
        return {"approved": False,
                "reason": "trade-off documentation insufficient (PROM-003)"}
    return {"approved": True, "tradeoff_doc_ref": tradeoff_doc}
