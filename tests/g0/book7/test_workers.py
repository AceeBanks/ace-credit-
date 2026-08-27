"""B7.C13 — Worker evaluation tests."""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

_ROOT = Path(__file__).resolve().parents[3]
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from prototype.g0.evaluation.agent_eval import worker_eval  # noqa: E402


def _clean_worker() -> dict:
    return dict(
        obeyed_task_contract=True,
        used_allowed_context_only=True,
        used_allowed_tools_only=True,
        returned_structured_result=True,
        preserved_evidence_refs=True,
        scope_expanded=False,
        contacted_client=False,
        mutated_policy_or_canonical=False,
        scratch_memory_promoted=False)


def test_worker_clean_pass():
    r = worker_eval(**_clean_worker())
    assert r["all_pass"] is True


def test_worker_scope_expansion_fails():
    kw = _clean_worker()
    kw["scope_expanded"] = True
    r = worker_eval(**kw)
    assert r["all_pass"] is False


def test_worker_client_contact_fails():
    kw = _clean_worker()
    kw["contacted_client"] = True
    r = worker_eval(**kw)
    assert r["all_pass"] is False


def test_worker_policy_mutation_fails():
    kw = _clean_worker()
    kw["mutated_policy_or_canonical"] = True
    r = worker_eval(**kw)
    assert r["all_pass"] is False


def test_worker_task_contract_violation_fails():
    kw = _clean_worker()
    kw["obeyed_task_contract"] = False
    r = worker_eval(**kw)
    assert r["all_pass"] is False


def test_worker_scratch_memory_promotion_fails():
    kw = _clean_worker()
    kw["scratch_memory_promoted"] = True
    r = worker_eval(**kw)
    assert r["all_pass"] is False
