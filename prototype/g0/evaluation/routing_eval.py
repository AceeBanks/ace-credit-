"""G0-B7-C16/C17 — Model routing & parser/retrieval evaluation.

C16: models are interchangeable implementation resources, not personalities.
A routing candidate must prove value against a simpler baseline; do not
route merely because a plugin claims intelligent routing.
C17: parser and retrieval candidates get empirical comparison on
task-appropriate truth; do not reward semantic retrieval where exact lookup
is the correct mechanism.
"""
from __future__ import annotations

from dataclasses import dataclass


@dataclass
class ModelRun:
    model_id: str
    model_version: str
    correctness: float
    factuality: float
    instruction_adherence: float
    structured_output_valid: float
    latency_ms: float
    cost_usd: float
    context_tokens: int
    tool_use_reliable: float
    retry_rate: float = 0.0
    safety_regression: bool = False
    provider_available: bool = True

    def to_dict(self) -> dict:
        return {k: getattr(self, k) for k in (
            "model_id", "model_version", "correctness", "factuality",
            "instruction_adherence", "structured_output_valid", "latency_ms",
            "cost_usd", "context_tokens", "tool_use_reliable", "retry_rate",
            "safety_regression", "provider_available")}


def compare_models(baseline: ModelRun, candidate: ModelRun) -> dict:
    """C16: per-dimension comparison; safety regression is a hard veto."""
    dims = {
        "correctness": (candidate.correctness, baseline.correctness,
                        "higher_is_better"),
        "factuality": (candidate.factuality, baseline.factuality,
                       "higher_is_better"),
        "instruction_adherence": (candidate.instruction_adherence,
                                  baseline.instruction_adherence,
                                  "higher_is_better"),
        "structured_output_valid": (candidate.structured_output_valid,
                                    baseline.structured_output_valid,
                                    "higher_is_better"),
        "latency_ms": (candidate.latency_ms, baseline.latency_ms,
                       "lower_is_better"),
        "cost_usd": (candidate.cost_usd, baseline.cost_usd,
                     "lower_is_better"),
        "tool_use_reliable": (candidate.tool_use_reliable,
                              baseline.tool_use_reliable,
                              "higher_is_better"),
        "retry_rate": (candidate.retry_rate, baseline.retry_rate,
                       "lower_is_better"),
    }
    deltas = {}
    for name, (cand, base, direction) in dims.items():
        delta = cand - base if direction == "higher_is_better" \
            else base - cand
        deltas[name] = round(delta, 4)
    vetoed = candidate.safety_regression or not candidate.provider_available
    return {
        "baseline": baseline.to_dict(),
        "candidate": candidate.to_dict(),
        "deltas": deltas,
        "hard_veto": vetoed,
        "veto_reason": ("safety regression" if candidate.safety_regression
                        else "provider unavailable" if not
                        candidate.provider_available else None),
        "promotable": not vetoed,
    }


def routing_must_beat_baseline(*, simple_cost: float, routed_cost: float,
                               simple_correctness: float,
                               routed_correctness: float) -> dict:
    """C16: a routing candidate must prove value over the simpler baseline."""
    cheaper = routed_cost < simple_cost * 0.9  # >=10% cheaper to justify
    as_correct = routed_correctness >= simple_correctness
    return {
        "cheaper_than_baseline": cheaper,
        "at_least_as_correct": as_correct,
        "proven_value": cheaper and as_correct,
        "reason": ("routing justified" if cheaper and as_correct
                   else "routing NOT justified against simple baseline"),
    }


def routing_structured_output_guard(*, routed_model_structured_reliable: bool,
                                    task_requires_structured: bool) -> bool:
    """C29-9: routing must not choose a model lacking structured-output
    reliability for a task that requires it."""
    if task_requires_structured and not routed_model_structured_reliable:
        return False
    return True


# ---------------------------------------------------------------------
# C17 — Parser & retrieval
# ---------------------------------------------------------------------

def parser_eval(*, text_fidelity: float, heading_fidelity: float,
                table_fidelity: float, locator_lineage: float,
                extraction_errors: int, latency_ms: float, cost_usd: float,
                failure_detected: bool) -> dict:
    """C17: parser lanes measured on task-appropriate truth."""
    return {
        "text_fidelity": round(text_fidelity, 4),
        "heading_fidelity": round(heading_fidelity, 4),
        "table_fidelity": round(table_fidelity, 4),
        "locator_lineage": round(locator_lineage, 4),
        "extraction_errors": extraction_errors,
        "latency_ms": latency_ms,
        "cost_usd": cost_usd,
        "failure_detected": failure_detected,
        "passes_locator_hard_gate": locator_lineage >= 0.9,
    }


def parser_compare(baseline: dict, candidate: dict) -> dict:
    """C17: empirical comparison; locator lineage is the hard gate
    (Amendment 002 — no parser wins without location metadata for evidence
    lineage)."""
    candidate_wins = (
        candidate["table_fidelity"] >= baseline["table_fidelity"] and
        candidate["locator_lineage"] >= baseline["locator_lineage"] and
        candidate["extraction_errors"] <= baseline["extraction_errors"])
    return {
        "candidate_wins": candidate_wins,
        "candidate_passes_locator_gate": candidate["passes_locator_hard_gate"],
        "baseline": baseline,
        "candidate": candidate,
        "verdict": "CANDIDATE" if candidate_wins and
        candidate["passes_locator_hard_gate"] else "BASELINE",
    }


def retrieval_task_appropriateness(*, task_kind: str,
                                   semantic_used: bool) -> bool:
    """C17: do not reward semantic retrieval where exact lookup is the
    correct mechanism (e.g. exact identifier/deadline lookup)."""
    exact_tasks = ("exact_id_lookup", "deadline_lookup", "revision_lookup",
                   "identifier_resolution")
    if task_kind in exact_tasks and semantic_used:
        return False
    return True


def retrieval_compare(*, exact_recall: float, semantic_recall: float,
                      exact_precision: float, semantic_precision: float,
                      task_kind: str) -> dict:
    """C17: compare strategies on recall/precision; the appropriate strategy
    for the task wins. Semantic retrieval that returns stale authority fails
    (C29-6)."""
    if task_kind in ("exact_id_lookup", "deadline_lookup", "revision_lookup"):
        winner = "EXACT" if exact_recall >= semantic_recall else "SEMANTIC"
        return {"appropriate_winner": "EXACT",
                "measured_winner": winner,
                "task_kind": task_kind,
                "semantic_rewarded_inappropriately": winner == "SEMANTIC",
                "exact_recall": exact_recall,
                "semantic_recall": semantic_recall}
    return {"appropriate_winner": "TASK_DEPENDENT", "task_kind": task_kind,
            "exact_recall": exact_recall, "semantic_recall": semantic_recall,
            "semantic_rewarded_inappropriately": False}


def stale_authority_check(*, retrieved_freshness: list[str],
                          expected_current_revision: str) -> dict:
    """C29-6: semantic retrieval improving recall while returning stale
    authority is a hard failure."""
    stale = [r for r in retrieved_freshness if r != expected_current_revision]
    return {"pass": not stale, "stale_refs": stale}
