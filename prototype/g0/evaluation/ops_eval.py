"""G0-B7-C24/C25 — Cost/latency/reliability and privacy/leakage evaluation.

Cost optimization cannot bypass correctness/evidence/security floors. Cross-
tenant leakage and holdout contamination are P0. Statistical discipline
(C28) reports sample size, uncertainty and failure counts by severity rather
than fake precision from tiny sets.
"""
from __future__ import annotations

from dataclasses import dataclass


@dataclass
class OperationalRun:
    capability_id: str
    tokens_in: int
    tokens_out: int
    model_cost_usd: float
    external_api_cost_usd: float
    p50_latency_ms: float
    p95_latency_ms: float
    timeouts: int
    retries: int
    schema_failures: int
    tool_failures: int
    context_tokens: int

    @property
    def total_cost(self) -> float:
        return self.model_cost_usd + self.external_api_cost_usd

    @property
    def timeout_rate(self) -> float:
        return 0.0


def operational_report(runs: list[OperationalRun]) -> dict:
    """C24: per-capability cost/latency/reliability telemetry."""
    if not runs:
        return {"capabilities": {}, "total_cost_usd": 0.0, "total_calls": 0}
    by_cap: dict[str, list[OperationalRun]] = {}
    for run in runs:
        by_cap.setdefault(run.capability_id, []).append(run)
    caps = {}
    for cap, cap_runs in by_cap.items():
        total = len(cap_runs)
        caps[cap] = {
            "calls": total,
            "total_cost_usd": round(sum(r.total_cost for r in cap_runs), 4),
            "tokens_in": sum(r.tokens_in for r in cap_runs),
            "tokens_out": sum(r.tokens_out for r in cap_runs),
            "p50_latency_ms": round(sum(r.p50_latency_ms for r in cap_runs)
                                    / total, 1),
            "p95_latency_ms": round(sum(r.p95_latency_ms for r in cap_runs)
                                    / total, 1),
            "timeouts": sum(r.timeouts for r in cap_runs),
            "retries": sum(r.retries for r in cap_runs),
            "schema_failures": sum(r.schema_failures for r in cap_runs),
            "tool_failures": sum(r.tool_failures for r in cap_runs),
            "context_tokens": max(r.context_tokens for r in cap_runs),
        }
    return {
        "capabilities": caps,
        "total_cost_usd": round(sum(r.total_cost for r in runs), 4),
        "total_calls": len(runs),
    }


def cost_guard(*, cost_improvement: bool, correctness_ok: bool,
               security_ok: bool, evidence_ok: bool) -> dict:
    """C24 cost guard: cost optimization cannot bypass floors."""
    floors = correctness_ok and security_ok and evidence_ok
    return {
        "allowed": cost_improvement and floors,
        "reason": "cost optimization cannot bypass correctness/evidence/"
                  "security floors" if not floors else "",
    }


def latency_acceptability(*, p95_ms: float, budget_ms: float) -> dict:
    return {"acceptable": p95_ms <= budget_ms,
            "p95_ms": p95_ms, "budget_ms": budget_ms}


def reliability_metrics(*, runs: list[OperationalRun]) -> dict:
    total = len(runs)
    if not total:
        return {"success_rate": 0.0, "timeout_rate": 0.0, "retry_rate": 0.0}
    failures = sum(r.timeouts + r.schema_failures + r.tool_failures
                   for r in runs)
    return {
        "success_rate": round(1 - failures / total, 4),
        "timeout_rate": round(sum(r.timeouts for r in runs) / total, 4),
        "retry_rate": round(sum(r.retries for r in runs) / total, 4),
        "schema_failure_rate": round(sum(r.schema_failures for r in runs)
                                     / total, 4),
    }


# ---------------------------------------------------------------------
# C25 — privacy & leakage
# ---------------------------------------------------------------------

def privacy_leakage_scan(*, text: str, redact_required: list[str]) -> dict:
    """Detect PII/secret leakage in eval text. Redaction-required PII must
    never appear in evaluation prompts/logs."""
    leaked = [token for token in redact_required if token in text]
    return {"leakage_found": bool(leaked), "leaked_tokens": leaked}


def cross_tenant_leakage_check(*, case_tenant: str,
                               corpus_tenant_scope: str | None) -> dict:
    """EVAL-LAW-011: cross-tenant leakage is P0 regardless of other scores."""
    if corpus_tenant_scope is not None and case_tenant != corpus_tenant_scope:
        return {"pass": False, "severity": "P0",
                "reason": f"case tenant {case_tenant} outside corpus scope "
                          f"{corpus_tenant_scope}"}
    return {"pass": True, "severity": None}


def holdout_contamination_check(*, case_ids: list[str],
                                holdout_case_ids: set[str]) -> dict:
    """PRIV-003: holdout cases never join dev/eval corpora."""
    overlap = [c for c in case_ids if c in holdout_case_ids]
    return {"pass": not overlap, "overlap": overlap,
            "severity": "P0" if overlap else None}


def memorization_not_capability(*, case_hash_seen_in_training: bool,
                                claimed_capability: str) -> dict:
    """PRIV-007: memorization of eval examples is not treated as capability."""
    if case_hash_seen_in_training:
        return {"pass": False,
                "reason": f"candidate likely memorized eval example; "
                          f"{claimed_capability} claim requires holdout "
                          "verification"}
    return {"pass": True}


# ---------------------------------------------------------------------
# C26 — failure harvesting
# ---------------------------------------------------------------------

def harvest_failure_case(*, capability_id: str, input_refs: list[str],
                         observed_output_ref: str,
                         expected_behavior: str | None,
                         failure_taxonomy: str, severity: str,
                         reproducible: bool,
                         candidate_lesson_refs: list[str] | None = None) -> dict:
    """FailureCase: structured input side of future improvement. Feedback is
    NOT direct training truth (EVAL-LAW-012) — it becomes candidate evidence."""
    return {
        "failure_case_id": f"fc-{abs(hash((capability_id, observed_output_ref))) % 10**6}",
        "capability_id": capability_id,
        "input_refs": list(input_refs),
        "observed_output_ref": observed_output_ref,
        "expected_behavior": expected_behavior,
        "failure_taxonomy": failure_taxonomy,
        "severity": severity,
        "reproducible": reproducible,
        "candidate_lesson_refs": list(candidate_lesson_refs or []),
        "is_training_truth": False,  # EVAL-LAW-012: not direct ground truth
    }


def feedback_is_not_training_truth(*, outcome: str,
                                   feedback_type: str) -> dict:
    """EVAL-LAW-012: client dislikes tone -> preference signal, not a label;
    grant loss -> not proof the draft was bad; reviewer deadline correction
    -> factual error candidate."""
    return {
        "feedback_type": feedback_type,
        "interpretation": {
            "tone_dislike": "preference signal",
            "grant_lost": "not proof of draft quality",
            "deadline_correction": "factual error candidate",
            "requirement_miss": "regression candidate",
        }.get(feedback_type, "requires interpretation"),
        "outcome": outcome,
        "direct_training_truth": False,
    }
