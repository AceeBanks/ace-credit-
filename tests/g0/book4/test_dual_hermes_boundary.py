"""B4.C1 — Dual-Hermes Constitutional Boundary tests.

Proves the frozen boundary is executable:
  * no capability requires Personal Hermes to perform CEO execution;
  * no CEO workflow requires full raw client chat history;
  * no shared mutable memory store is the only source for either role;
and that the validator fails closed on every material violation (shared
namespace, CEO-only capability on Personal, submission-family capability,
raw transcript in CEO context, unknown capability, broken laws, missing
roles, worker static grants, missing overlaps/handoffs).
"""
from __future__ import annotations

import copy

import pytest

from tools.g0._common import POLICY_CONFIG_DIR, load_yaml
from tools.g0.validate_dual_hermes_boundary import (
    BOUNDARY_PATH,
    CEO_ONLY_CAPABILITIES,
    load,
    validate,
)

from tools.g0.validate_dual_hermes_boundary import _load_registry  # noqa: E402


@pytest.fixture(scope="module")
def boundary() -> dict:
    return load()


@pytest.fixture(scope="module")
def registry() -> dict:
    return _load_registry()


def _role(boundary: dict, role_id: str) -> dict:
    return next(r for r in boundary["roles"] if r["role_id"] == role_id)


# --- C1 required tests -----------------------------------------------------

def test_no_capability_requires_personal_to_perform_ceo_execution(boundary):
    personal = _role(boundary, "PERSONAL_HERMES")
    ceo = _role(boundary, "CEO_HERMES")
    overlap = set(personal["capabilities"]) & CEO_ONLY_CAPABILITIES
    assert overlap == set(), f"Personal Hermes references CEO-only: {overlap}"
    # Personal's registry capabilities must be executable at L1 or below
    registry = _load_registry()
    for cap in personal["capabilities"]:
        if cap in boundary["protocol_native_capabilities"]:
            continue
        assert registry[cap]["minimum_level"] in ("L0", "L1"), cap
        assert "ACTOR-HERMES-PERSONAL" in registry[cap]["allowed_actor_types"], cap
    # Every CEO-only capability actually exists in the registry (no drift)
    for cap in CEO_ONLY_CAPABILITIES:
        assert cap in registry, f"CEO-only capability not in registry: {cap}"
    # Personal and CEO capability lists are not identical
    assert set(personal["capabilities"]) != set(ceo["capabilities"])


def test_no_ceo_workflow_requires_full_raw_client_chat_history(boundary):
    ceo = _role(boundary, "CEO_HERMES")
    assert "RAW_CLIENT_TRANSCRIPT" in ceo["forbidden_context_classes"]
    assert "RAW_CLIENT_TRANSCRIPT_HISTORY" not in ceo["context_classes"]
    # CEO's stated non-responsibilities include holding conversation history
    assert "HOLD_FULL_USER_CONVERSATION_HISTORY" in ceo["non_responsibilities"]
    # The intent-feed-forward law requires raw conversation to stay linked, not embedded
    intent_law = next(l for l in boundary["laws"]
                      if l["law_id"] == "DUAL-LAW-011")
    assert "linked for audit" in intent_law["rule"]
    assert "never embedded" in intent_law["rule"]
    # Personal must never dump the raw transcript into CEO via context classes
    personal = _role(boundary, "PERSONAL_HERMES")
    assert "RAW_CLIENT_TRANSCRIPT_HISTORY" in personal["forbidden_context_classes"]


def test_no_shared_mutable_memory_store_is_only_source(boundary):
    namespaces = {r["memory_namespace"] for r in boundary["roles"]
                  if r["role_id"] != "WORKER_AGENT"}
    assert namespaces == {"personal_hermes", "ceo_hermes"}
    for r in boundary["roles"]:
        assert r["memory_is_canonical"] is False
    # Anti-collapse rule present and strict
    rule = boundary["anti_collapse_rule"]
    assert "permanent namespace" in rule["rule"]
    assert rule["enforcement"]
    # Explicit prohibited overlap records the merge prohibition
    overlaps = {o["overlap_id"]: o for o in boundary["prohibited_overlaps"]}
    assert overlaps["OV-003"]["prohibition"]  # shared mutable namespace


def test_laws_are_frozen_and_complete(boundary):
    ids = [l["law_id"] for l in boundary["laws"]]
    assert len(ids) == 20
    assert len(set(ids)) == 20
    assert all(l["status"] == "FROZEN" for l in boundary["laws"])
    expected = {f"DUAL-LAW-{n:03d}" for n in range(1, 21)}
    assert set(ids) == expected


# --- adversarial fail-closed tests -----------------------------------------

def test_personal_with_ceo_capability_fails():
    data = load()
    personal = _role(data, "PERSONAL_HERMES")
    personal["capabilities"] = personal["capabilities"] + ["research.funder"]
    ok, report = validate(data)
    assert not ok
    assert any("CEO-only" in e for e in report["errors"])


def test_submission_capability_fails():
    data = load()
    ceo = _role(data, "CEO_HERMES")
    ceo["capabilities"] = ceo["capabilities"] + ["application.submit"]
    ok, report = validate(data)
    assert not ok
    assert any("not ENABLED" in e or "submission" in e for e in report["errors"])


def test_shared_namespace_fails():
    data = load()
    ceo = _role(data, "CEO_HERMES")
    ceo["memory_namespace"] = "personal_hermes"
    ok, report = validate(data)
    assert not ok
    assert any("shared" in e for e in report["errors"])


def test_canonical_memory_flag_fails():
    data = load()
    _role(data, "CEO_HERMES")["memory_is_canonical"] = True
    ok, report = validate(data)
    assert not ok
    assert any("memory_is_canonical" in e for e in report["errors"])


def test_ceo_raw_transcript_context_fails():
    data = load()
    ceo = _role(data, "CEO_HERMES")
    ceo["forbidden_context_classes"].remove("RAW_CLIENT_TRANSCRIPT")
    ok, report = validate(data)
    assert not ok
    assert any("RAW_CLIENT_TRANSCRIPT" in e for e in report["errors"])


def test_unknown_capability_fails():
    data = load()
    _role(data, "PERSONAL_HERMES")["capabilities"].append("totally.bogus")
    ok, report = validate(data)
    assert not ok
    assert any("unknown capability" in e for e in report["errors"])


def test_worker_static_grants_fail():
    data = load()
    worker = _role(data, "WORKER_AGENT")
    worker["capabilities"] = ["research.funder"]
    ok, report = validate(data)
    assert not ok
    assert any("empty static" in e for e in report["errors"])


def test_missing_law_fails():
    data = copy.deepcopy(load())
    data["laws"] = [l for l in data["laws"] if l["law_id"] != "DUAL-LAW-009"]
    ok, report = validate(data)
    assert not ok
    assert any("exactly 20" in e for e in report["errors"])


def test_unfrozen_law_fails():
    data = copy.deepcopy(load())
    data["laws"][0]["status"] = "DRAFT"
    ok, report = validate(data)
    assert not ok
    assert any("FROZEN" in e for e in report["errors"])


def test_missing_role_fails():
    data = copy.deepcopy(load())
    data["roles"] = [r for r in data["roles"]
                     if r["role_id"] != "CEO_HERMES"]
    ok, report = validate(data)
    assert not ok
    assert any("missing roles" in e for e in report["errors"])


def test_missing_overlaps_fails():
    data = copy.deepcopy(load())
    data["prohibited_overlaps"] = []
    ok, report = validate(data)
    assert not ok
    assert any("prohibited_overlaps" in e for e in report["errors"])


def test_clean_boundary_passes():
    ok, report = validate(load())
    assert ok, report["errors"]
    assert report["law_count"] == 20
    assert report["role_count"] == 3
    assert report["distinct_namespaces"] == ["ceo_hermes", "personal_hermes"]
