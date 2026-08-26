"""B4.C8-C9 — Worker sidechain isolation and CEO synthesis tests.

C8: a 50k-token worker trace returns a bounded parent payload; CEO can
retrieve exact source/artifact refs without transcript injection; secret
fixtures fail closed; failed/retried attempts keep unique attempt ids and
shared task lineage.
C9: conflicting worker results do not silently average into false consensus;
failed critical tasks prevent success status; outcomes pin the exact
application project + opportunity revision. Plus schema adversarial checks.
"""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

_ROOT = Path(__file__).resolve().parents[3]
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from prototype.g0.agents.result_reducer import (  # noqa: E402
    SidechainPolicyError,
    ToolCall,
    build_sidechain,
    make_worker_result,
    scan_for_secrets,
    synthesize,
)
from tools.g0.validate_sidechain_synthesis import (  # noqa: E402
    _load_schema,
)


def _big_trace() -> str:
    return " ".join(f"research step {i} output detail" for i in range(15000))


def _sidechain(task_id="task-1", attempt_id="attempt-1") -> dict:
    return build_sidechain(
        task_id=task_id, attempt_id=attempt_id,
        worker_identity="FunderResearchWorker",
        transcript_uri=f"sidechains/{task_id}/{attempt_id}/transcript.jsonl",
        transcript_preview="funding priorities: youth workforce",
        tool_calls=[ToolCall("tool.search", "research.funder",
                             "2026-08-26T10:00:00Z")],
        source_refs=["snapshot:georgia-opb:rev-3"],
        artifact_refs=["artifact:research-pack-1"],
        token_metrics={"input_tokens": 50000, "output_tokens": 12000},
    )


# --- C8 sidechain isolation -------------------------------------------------

def test_50k_trace_returns_bounded_parent_payload():
    trace = _big_trace()
    sidechain = build_sidechain(
        task_id="task-1", attempt_id="attempt-1",
        worker_identity="FunderResearchWorker",
        transcript_uri="sidechains/task-1/attempt-1/transcript.jsonl",
        transcript_preview=trace[:500],  # preview only, no secrets
        token_metrics={"input_tokens": 50000, "output_tokens": 12000},
    )
    result = make_worker_result(
        task_id="task-1", attempt_id="attempt-1", status="SUCCEEDED",
        summary=trace, structured_output_ref="so:research-pack-1",
        source_refs=["snapshot:georgia-opb:rev-3"],
        artifact_refs=["artifact:research-pack-1"],
        sidechain_ref=sidechain.transcript_uri)
    # Parent payload is bounded; full trace is not injected
    assert len(result.summary) < 3000
    assert "[truncated" in result.summary
    assert "research step 14999" not in result.summary
    # Full depth remains retrievable via the sidechain ref
    assert result.sidechain_ref == sidechain.transcript_uri
    assert sidechain.token_metrics["input_tokens"] == 50000


def test_ceo_retrieves_exact_refs_without_transcript_injection():
    sidechain = _sidechain()
    result = make_worker_result(
        task_id="task-1", attempt_id="attempt-1", status="SUCCEEDED",
        summary="funder prioritizes youth workforce", 
        structured_output_ref="so:research-pack-1",
        source_refs=sidechain.source_refs,
        artifact_refs=sidechain.artifact_refs,
        sidechain_ref=sidechain.transcript_uri)
    assert "snapshot:georgia-opb:rev-3" in result.source_refs
    assert "artifact:research-pack-1" in result.artifact_refs
    # no transcript body in the parent-facing payload
    assert "research step 0 output detail" not in result.summary
    assert "transcript.jsonl" not in result.summary


def test_secret_fixture_fails_closed():
    leaked = "the api key is sk-abcdef0123456789abcdef0123456789"
    assert scan_for_secrets(leaked) == ["api_key"]
    with pytest.raises(SidechainPolicyError, match="secret patterns"):
        build_sidechain(
            task_id="task-1", attempt_id="attempt-1",
            worker_identity="FunderResearchWorker",
            transcript_uri="sidechains/task-1/attempt-1/transcript.jsonl",
            transcript_preview=leaked)


def test_secret_scan_catches_private_key_and_bearer():
    assert scan_for_secrets("-----BEGIN PRIVATE KEY-----") == ["private_key"]
    assert scan_for_secrets("Bearer eyJhbGciOiJIUzI1NiJ9.eyJzdWIiOiIxMjM0NTY3ODkwIn0"
                            ".dozjgNryP4J3jVmNHl0w5N_XgL0n3I9PlFUP0THsR8U") == ["bearer_token"]


def test_retries_keep_lineage_unique_attempts():
    a1 = build_sidechain(task_id="task-9", attempt_id="attempt-1",
                         worker_identity="CitationQAWorker",
                         transcript_uri="u1", transcript_preview="clean")
    a2 = build_sidechain(task_id="task-9", attempt_id="attempt-2",
                         worker_identity="CitationQAWorker",
                         transcript_uri="u2", transcript_preview="clean",
                         errors=["timeout"], retries=1)
    assert a1.attempt_id == "attempt-1"
    assert a2.attempt_id == "attempt-2"
    assert a1.task_id == a2.task_id == "task-9"
    assert a2.retries == 1


# --- C9 synthesis ------------------------------------------------------------

def _result(task_id, status, findings, uncertainties=(), quality="PROVISIONAL"):
    return make_worker_result(
        task_id=task_id, attempt_id=f"{task_id}/attempt-1", status=status,
        summary="; ".join(findings), structured_output_ref=f"so:{task_id}",
        key_findings=list(findings), uncertainties=list(uncertainties),
        source_refs=["snapshot:georgia-opb:rev-3"],
        artifact_refs=[f"artifact:{task_id}"], quality_state=quality,
        sidechain_ref=f"sidechains/{task_id}")


def test_conflicting_results_not_averaged():
    r1 = _result("task-research-a", "SUCCEEDED",
                 ["opportunity.deadline = 2026-10-15 (official rev 3)"])
    r2 = _result("task-research-b", "SUCCEEDED",
                 ["opportunity.deadline = 2027-01-01 (secondary source)"])
    outcome = synthesize(
        outcome_id="oc-1", intent_id="int-1", plan_id="plan-1",
        application_project_id="proj-after-school",
        opportunity_revision_id="opp-rev-3", outcome_type="MATCH_ASSESSMENT",
        results=[r1, r2])
    assert outcome["status"] == "CONFLICTED"
    assert outcome["conflicts"] == ["opportunity.deadline"]
    # no silent average: the deadline was not resolved to a middle value
    assert "2026-11-01" not in outcome["executive_summary"]


def test_failed_critical_task_blocks_success():
    r1 = _result("critical:eligibility", "FAILED",
                 ["hard eligibility failure: not 501(c)(3)"])
    r2 = _result("task-research", "SUCCEEDED", ["funder prioritizes youth"])
    outcome = synthesize(
        outcome_id="oc-2", intent_id="int-1", plan_id="plan-1",
        application_project_id="proj-after-school",
        opportunity_revision_id="opp-rev-3", outcome_type="ELIGIBILITY_ASSESSMENT",
        results=[r1, r2], critical_task_ids={"critical:eligibility"})
    assert outcome["status"] == "FAILED"


def test_partial_results_incomplete():
    r1 = _result("task-a", "SUCCEEDED", ["finding a"])
    r2 = _result("task-b", "PARTIAL", ["finding b"], uncertainties=["missing data"])
    outcome = synthesize(
        outcome_id="oc-3", intent_id="int-1", plan_id="plan-1",
        application_project_id="proj-after-school",
        opportunity_revision_id="opp-rev-3", outcome_type="RESEARCH_PACK",
        results=[r1, r2])
    assert outcome["status"] == "INCOMPLETE"
    assert "missing data" in outcome["unresolved_questions"]


def test_outcome_pins_exact_opportunity_revision():
    outcome = synthesize(
        outcome_id="oc-4", intent_id="int-1", plan_id="plan-1",
        application_project_id="proj-after-school",
        opportunity_revision_id="opp-rev-3", outcome_type="MOCK_PROPOSAL",
        results=[_result("task-a", "SUCCEEDED", ["x"])])
    assert outcome["opportunity_revision_id"] == "opp-rev-3"
    assert outcome["application_project_id"] == "proj-after-school"
    assert outcome["status"] == "SUCCEEDED"


# --- schema adversarial checks -----------------------------------------------

def test_schemas_strict_and_complete():
    from tools.g0.validate_sidechain_synthesis import (
        WORKER_REQUIRED, SIDECHAIN_REQUIRED, OUTCOME_REQUIRED, _check)
    errors: list[str] = []
    _check("worker_result.schema.json", WORKER_REQUIRED, errors)
    _check("sidechain_manifest.schema.json", SIDECHAIN_REQUIRED, errors)
    _check("outcome_artifact.schema.json", OUTCOME_REQUIRED, errors)
    assert errors == []


def test_worker_result_requires_sidechain_ref():
    ok, schema = _load_schema("worker_result.schema.json")
    assert ok
    assert "sidechain_ref" in schema["required"]
    assert schema["properties"]["summary"]["maxLength"] <= 8000


def test_outcome_requires_revision_and_action_flags():
    ok, schema = _load_schema("outcome_artifact.schema.json")
    assert ok
    assert "opportunity_revision_id" in schema["required"]
    assert "client_action_required" in schema["properties"]


def test_sidechain_requires_secret_scan_and_redaction():
    ok, schema = _load_schema("sidechain_manifest.schema.json")
    assert ok
    props = schema["properties"]
    assert "secret_scan" in props
    assert "redaction_status" in props
    assert props["redaction_status"]["enum"] == ["CLEAN", "REDACTED",
                                                 "POLICY_FAILURE"]
