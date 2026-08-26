"""G0-B5-C7 — DecisionRecord contract tests."""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

_ROOT = Path(__file__).resolve().parents[3]
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from prototype.g0.evidence.decisions import (  # noqa: E402
    DecisionError,
    DecisionInputRef,
    build_decision,
    supersede_decision,
)


def _eligibility_inputs() -> list[DecisionInputRef]:
    return [
        DecisionInputRef(input_role="opportunity_revision",
                         ref="opp-rev-3", version_or_revision_id="rev-3"),
        DecisionInputRef(input_role="eligibility_rule",
                         ref="rule/eligibility-v2"),
        DecisionInputRef(input_role="evidence_claim",
                         ref="claim-org-status"),
    ]


def test_eligibility_decision_pins_exact_revision():
    record = build_decision(
        decision_id="dec-1", decision_type="ELIGIBILITY",
        tenant_id="tenant-a", project_id="proj-1", actor_ref="ceo-hermes",
        capability_id="eligibility.evaluate", input_refs=_eligibility_inputs(),
        policy_ref="policy/eligibility-v2",
        model_or_engine_ref="deterministic-service/eligibility-v2",
        result={"eligible": True, "rule_results": []})
    rev_inputs = [i for i in record.input_refs
                  if i.input_role == "opportunity_revision"]
    assert rev_inputs and rev_inputs[0].ref == "opp-rev-3"
    assert rev_inputs[0].version_or_revision_id == "rev-3"


def test_decision_missing_revision_fails():
    with pytest.raises(DecisionError, match="opportunity revision"):
        build_decision(
            decision_id="dec-2", decision_type="ELIGIBILITY",
            tenant_id="tenant-a", project_id="proj-1", actor_ref="ceo",
            capability_id="eligibility.evaluate",
            input_refs=[DecisionInputRef(input_role="eligibility_rule",
                                         ref="rule/eligibility-v2")],
            policy_ref="policy/eligibility-v2", result={"eligible": True})


def test_unknown_decision_type_fails():
    with pytest.raises(DecisionError, match="unknown decision_type"):
        build_decision(
            decision_id="dec-3", decision_type="WILD_GUESS",
            tenant_id="tenant-a", project_id="proj-1", actor_ref="ceo",
            capability_id="x", input_refs=_eligibility_inputs(),
            policy_ref="p", result={})


def test_supersession_does_not_mutate_old_decision():
    old = build_decision(
        decision_id="dec-old", decision_type="ELIGIBILITY",
        tenant_id="tenant-a", project_id="proj-1", actor_ref="ceo",
        capability_id="eligibility.evaluate", input_refs=_eligibility_inputs(),
        policy_ref="policy/eligibility-v2", result={"eligible": False})
    new = build_decision(
        decision_id="dec-new", decision_type="ELIGIBILITY",
        tenant_id="tenant-a", project_id="proj-1", actor_ref="ceo",
        capability_id="eligibility.evaluate", input_refs=_eligibility_inputs(),
        policy_ref="policy/eligibility-v2", result={"eligible": True})
    supersede_decision(old, new)
    assert old.status == "SUPERSEDED"
    assert new.supersedes_decision_id == old.decision_id
    assert old.result == {"eligible": False}  # untouched


def test_model_assisted_decision_pins_context_refs():
    record = build_decision(
        decision_id="dec-4", decision_type="QA_FACTUALITY",
        tenant_id="tenant-a", project_id="proj-1", actor_ref="qa-worker",
        capability_id="qa.factuality", input_refs=_eligibility_inputs(),
        policy_ref="policy/qa-v1", model_or_engine_ref="model/provider-b/v2",
        result={"passed": True})
    assert record.model_or_engine_ref == "model/provider-b/v2"
    assert len(record.input_refs) >= 3  # structured context refs pinned
