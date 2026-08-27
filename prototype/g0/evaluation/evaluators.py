"""G0-B7-C18 — Evaluator governance.

Every evaluator declares what it measures, what it cannot measure, its
version, known bias/failure modes, required independence and calibration
evidence. LLM judges are advisory (EVAL-LAW-005); deterministic truth wins
when they conflict (EVAL-LAW-004); candidates cannot be sole evaluators of
themselves (EVAL-LAW-006); one opaque "quality judge" can never decide
production promotion.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


class EvaluatorError(ValueError):
    """Raised when an evaluator violates governance rules."""


EVALUATOR_TYPES = (
    "deterministic_assertion", "schema_validator", "domain_rule",
    "statistical_metric", "llm_judge", "pairwise_preference",
    "human_reviewer", "production_outcome",
)


@dataclass
class EvaluatorDeclaration:
    evaluator_id: str
    evaluator_type: str
    measures: str
    cannot_measure: str
    version: str
    required_independence: str = "independent_of_candidate"
    known_bias_failure_modes: tuple[str, ...] = ()
    calibration_evidence_ref: str | None = None

    def __post_init__(self) -> None:
        if self.evaluator_type not in EVALUATOR_TYPES:
            raise EvaluatorError(f"unknown evaluator_type {self.evaluator_type!r}")
        if self.evaluator_type == "llm_judge" and not self.version:
            raise EvaluatorError("llm_judge must declare model/version (C18)")
        if not self.measures or not self.cannot_measure:
            raise EvaluatorError("evaluator must declare measures AND "
                                 "cannot_measure (C18)")

    def to_dict(self) -> dict:
        return {
            "evaluator_id": self.evaluator_id,
            "evaluator_type": self.evaluator_type,
            "measures": self.measures,
            "cannot_measure": self.cannot_measure,
            "version": self.version,
            "required_independence": self.required_independence,
            "known_bias_failure_modes": list(self.known_bias_failure_modes),
            "calibration_evidence_ref": self.calibration_evidence_ref,
        }


class EvaluatorRegistry:
    """Registry of governed evaluators."""

    def __init__(self) -> None:
        self._evaluators: dict[str, EvaluatorDeclaration] = {}

    def register(self, decl: EvaluatorDeclaration) -> EvaluatorDeclaration:
        self._evaluators[decl.evaluator_id] = decl
        return decl

    def get(self, evaluator_id: str) -> EvaluatorDeclaration:
        try:
            return self._evaluators[evaluator_id]
        except KeyError:
            raise EvaluatorError(f"unknown evaluator {evaluator_id!r}") from None

    def all(self) -> list[EvaluatorDeclaration]:
        return list(self._evaluators.values())


class LLMJudge:
    """Advisory LLM judge wrapper.

    - EVAL-LAW-005: advisory only; can never alone authorize promotion.
    - C18: declares model/version + known biases; cannot measure factuality
      authority (deterministic truth wins on conflict).
    """

    def __init__(self, judge_id: str, model_version: str,
                 known_biases: tuple[str, ...] = ()) -> None:
        self.judge_id = judge_id
        self.model_version = model_version
        self.known_biases = known_biases

    def score(self, *, dimension: str, candidate_id: str,
              sample: dict, score: float, confidence: float = 0.0) -> dict:
        return {
            "judge_id": self.judge_id,
            "model_version": self.model_version,
            "dimension": dimension,
            "candidate_id": candidate_id,
            "score": score,
            "confidence": confidence,
            "role": "ADVISORY",
            "known_biases": list(self.known_biases),
            "cannot_override": ["factuality", "security", "correctness"],
        }

    @staticmethod
    def conflict_with_deterministic(deterministic_result: dict,
                                    judge_score: float) -> dict:
        """EVAL-LAW-004: deterministic truth wins on conflict."""
        if not deterministic_result.get("all_pass", False):
            return {"resolved_by": "deterministic", "judge_overridden": True,
                    "reason": "deterministic assertion failed; judge score "
                              "cannot override it"}
        return {"resolved_by": "both", "judge_overridden": False}


def independence_ok(*, candidate_id: str, evaluator: EvaluatorDeclaration,
                    judge_owner: str | None = None) -> bool:
    """EVAL-LAW-006: a candidate must not be the sole evaluator of itself."""
    if evaluator.required_independence == "independent_of_candidate" and \
            judge_owner and judge_owner == candidate_id:
        return False
    return True


def calibration_report(agreements: list[dict]) -> dict:
    """C18: measured agreement / positional bias / verbosity bias between
    LLM judge and reviewed ground truth."""
    total = len(agreements)
    if total == 0:
        return {"sample_size": 0, "agreement_rate": None,
                "positional_bias": None, "verbosity_bias": None}
    agree = sum(1 for a in agreements if a.get("agrees"))
    return {
        "sample_size": total,
        "agreement_rate": round(agree / total, 3),
        "positional_bias": sum(1 for a in agreements
                               if a.get("position_bias")) / total,
        "verbosity_bias": sum(1 for a in agreements
                              if a.get("verbosity_bias")) / total,
    }
