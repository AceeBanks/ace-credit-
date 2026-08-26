"""B4.C8-C9 — WorkerResult reduction and CEO synthesis (prototype).

  * SidechainManifest preserves full forensic depth without parent pollution;
    secret scan is fail-closed (a raw secret in a trace is a policy failure).
  * WorkerResult is the bounded parent-facing payload (summary truncated to a
    budget; full content lives behind transcript_uri).
  * synthesize: failed critical tasks prevent success; conflicting worker
    outputs surface as CONFLICTED (never silently averaged into consensus);
    the outcome pins the exact application project + OpportunityRevision.
"""
from __future__ import annotations

import re
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any

SUMMARY_BUDGET_CHARS = 2000

SECRET_PATTERNS = {
    "api_key": re.compile(r"sk-[A-Za-z0-9]{16,}"),
    "aws_secret": re.compile(r"AKIA[0-9A-Z]{16}"),
    "bearer_token": re.compile(r"Bearer\s+[A-Za-z0-9._~+/=-]{20,}"),
    "private_key": re.compile(r"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----"),
}

CRITICAL_TASK_PREFIX = "critical:"


class SidechainPolicyError(ValueError):
    """Raised when a sidechain would persist a raw secret."""


@dataclass
class ToolCall:
    tool_id: str
    capability_id: str
    timestamp: str


@dataclass
class SidechainManifest:
    task_id: str
    attempt_id: str
    worker_identity: str
    start_time: str
    end_time: str
    tool_calls: list[ToolCall]
    source_refs: list[str]
    artifact_refs: list[str]
    errors: list[str]
    retries: int
    transcript_uri: str
    redaction_status: str
    retention_class: str
    model_provider: str = "unknown"
    token_metrics: dict[str, int] = field(default_factory=dict)
    cost_metrics: dict[str, Any] = field(default_factory=dict)
    secret_scan: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict:
        return {
            "task_id": self.task_id,
            "attempt_id": self.attempt_id,
            "worker_identity": self.worker_identity,
            "model_provider": self.model_provider,
            "start_time": self.start_time,
            "end_time": self.end_time,
            "tool_calls": [t.__dict__ for t in self.tool_calls],
            "source_refs": list(self.source_refs),
            "artifact_refs": list(self.artifact_refs),
            "errors": list(self.errors),
            "retries": self.retries,
            "transcript_uri": self.transcript_uri,
            "token_metrics": dict(self.token_metrics),
            "cost_metrics": dict(self.cost_metrics),
            "redaction_status": self.redaction_status,
            "retention_class": self.retention_class,
            "secret_scan": dict(self.secret_scan),
        }


def scan_for_secrets(text: str) -> list[str]:
    """Return matched secret pattern names; empty when clean."""
    return [name for name, pattern in SECRET_PATTERNS.items()
            if pattern.search(text)]


@dataclass
class WorkerResult:
    task_id: str
    attempt_id: str
    status: str
    summary: str
    structured_output_ref: str
    key_findings: list[str]
    uncertainties: list[str]
    source_refs: list[str]
    artifact_refs: list[str]
    quality_state: str
    sidechain_ref: str
    recommended_followups: list[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "task_id": self.task_id,
            "attempt_id": self.attempt_id,
            "status": self.status,
            "summary": self.summary,
            "structured_output_ref": self.structured_output_ref,
            "key_findings": list(self.key_findings),
            "uncertainties": list(self.uncertainties),
            "source_refs": list(self.source_refs),
            "artifact_refs": list(self.artifact_refs),
            "quality_state": self.quality_state,
            "recommended_followups": list(self.recommended_followups),
            "sidechain_ref": self.sidechain_ref,
        }


def build_sidechain(*, task_id: str, attempt_id: str, worker_identity: str,
                    transcript_uri: str, transcript_preview: str = "",
                    tool_calls: list[ToolCall] | None = None,
                    source_refs: list[str] | None = None,
                    artifact_refs: list[str] | None = None,
                    errors: list[str] | None = None, retries: int = 0,
                    model_provider: str = "unknown",
                    retention_class: str = "D4_WORKER_TRACE",
                    token_metrics: dict[str, int] | None = None) -> SidechainManifest:
    """Build a sidechain, failing closed when a raw secret would be persisted."""
    matched = scan_for_secrets(transcript_preview)
    if matched:
        raise SidechainPolicyError(
            f"secret patterns matched in worker trace: {matched} — "
            "sidechain persistence refused")
    now = datetime.now(timezone.utc).isoformat()
    return SidechainManifest(
        task_id=task_id, attempt_id=attempt_id,
        worker_identity=worker_identity,
        start_time=now, end_time=now,
        tool_calls=list(tool_calls or []),
        source_refs=list(source_refs or []),
        artifact_refs=list(artifact_refs or []),
        errors=list(errors or []), retries=retries,
        transcript_uri=transcript_uri,
        redaction_status="CLEAN", retention_class=retention_class,
        model_provider=model_provider,
        token_metrics=dict(token_metrics or {}),
        secret_scan={"secret_detected": False, "matched_patterns": []},
    )


def make_worker_result(*, task_id: str, attempt_id: str, status: str,
                       summary: str, structured_output_ref: str,
                       key_findings: list[str] | None = None,
                       uncertainties: list[str] | None = None,
                       source_refs: list[str] | None = None,
                       artifact_refs: list[str] | None = None,
                       quality_state: str = "PROVISIONAL",
                       sidechain_ref: str,
                       recommended_followups: list[str] | None = None,
                       budget_chars: int = SUMMARY_BUDGET_CHARS) -> WorkerResult:
    """Produce a bounded parent-facing result.

    A 50k-token worker trace must NOT reach the parent: the summary is
    truncated to budget_chars and the full content lives in the sidechain.
    """
    bounded = summary[:budget_chars]
    if len(summary) > budget_chars:
        bounded = bounded + "…[truncated; see sidechain transcript]"
    return WorkerResult(
        task_id=task_id, attempt_id=attempt_id, status=status,
        summary=bounded, structured_output_ref=structured_output_ref,
        key_findings=list(key_findings or []),
        uncertainties=list(uncertainties or []),
        source_refs=list(source_refs or []),
        artifact_refs=list(artifact_refs or []),
        quality_state=quality_state, sidechain_ref=sidechain_ref,
        recommended_followups=list(recommended_followups or []),
    )


def _predicate_of(finding: str) -> str:
    """Rough claim predicate extraction for conflict detection (prototype)."""
    # e.g. "opportunity.deadline = 2026-10-15 (official rev 3)"
    parts = finding.split("=")
    return parts[0].strip().lower()


def synthesize(*, outcome_id: str, intent_id: str, plan_id: str,
               application_project_id: str, opportunity_revision_id: str,
               outcome_type: str, results: list[WorkerResult],
               critical_task_ids: set[str] | None = None) -> dict[str, Any]:
    """CEO synthesis from bounded worker results.

    * a FAILED critical task => status FAILED (or BLOCKED if only some fail);
    * two results with conflicting predicates => CONFLICTED, never averaged;
    * outcome pins the exact application project + OpportunityRevision.
    """
    critical_task_ids = critical_task_ids or set()
    critical_failed = [r for r in results
                       if r.task_id in critical_task_ids and r.status == "FAILED"]
    any_failed = [r for r in results if r.status == "FAILED"]
    any_partial = [r for r in results if r.status == "PARTIAL"]

    # conflict detection across key findings
    claims: dict[str, list[str]] = {}
    for r in results:
        for finding in r.key_findings:
            pred = _predicate_of(finding)
            claims.setdefault(pred, []).append(finding)
    conflicts = [findings for findings in claims.values()
                 if len({f for f in findings}) > 1]
    # only treat as conflict when findings disagree on the same predicate
    conflicting = [pred for pred, findings in claims.items()
                   if len(set(findings)) > 1]

    if critical_failed:
        status = "FAILED"
    elif conflicting:
        status = "CONFLICTED"
    elif any_failed:
        status = "BLOCKED"
    elif any_partial:
        status = "INCOMPLETE"
    else:
        status = "SUCCEEDED"

    key_decisions = []
    for r in results:
        key_decisions.append({
            "decision": r.summary[:200],
            "basis": f"worker {r.task_id} attempt {r.attempt_id} "
                     f"quality {r.quality_state}",
        })

    return {
        "outcome_id": outcome_id,
        "intent_id": intent_id,
        "plan_id": plan_id,
        "application_project_id": application_project_id,
        "opportunity_revision_id": opportunity_revision_id,
        "outcome_type": outcome_type,
        "status": status,
        "executive_summary": " ".join(r.summary for r in results)[:2000],
        "key_decisions": key_decisions,
        "recommended_actions": [],
        "research_pack_refs": [r.structured_output_ref for r in results],
        "artifact_refs": [a for r in results for a in r.artifact_refs],
        "unresolved_questions": [u for r in results for u in r.uncertainties],
        "risks": [],
        "qa_refs": [],
        "evidence_refs": [s for r in results for s in r.source_refs],
        "client_action_required": False,
        "conflicts": conflicting,
        "created_at": datetime.now(timezone.utc).isoformat(),
    }
