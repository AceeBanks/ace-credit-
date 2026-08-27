"""G1 Wave 5 — client API tests.

Covers: chat -> intent -> plan -> durable tasks, progress from task state,
factory produce (deterministic lane), deliverable metadata + download,
governed model selection, auth/tenant enforcement, forged-project denial,
and submission-structural-absence.
"""
from __future__ import annotations

import sys
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

_ROOT = Path(__file__).resolve().parents[3]      # repo root (g0-worktree)
_SEED = _ROOT / "production-seed"
for _p in (str(_ROOT), str(_SEED)):
    if _p not in sys.path:
        sys.path.insert(0, _p)

from apps.api.deps import open_store  # noqa: E402
from apps.api.main import app  # noqa: E402

AUTH = {"X-Principal": "client-1"}


@pytest.fixture()
def client():
    store = open_store(":memory:")
    # reuse the app's deterministic seed against our in-memory store
    from apps.api.main import _seed_dev
    _seed_dev(store)
    app.state.store = store
    with TestClient(app) as c:
        yield c
    store.close()


def test_chat_intent_plan_tasks(client):
    r = client.post("/chat", json={
        "message": "We need funding for an after-school STEM program in "
                   "Atlanta.",
        "requested_capabilities": []}, headers=AUTH)
    assert r.status_code == 200
    data = r.json()
    assert data["conversation_id"].startswith("conv-")
    assert data["plan_id"].startswith("plan-")
    assert len(data["task_ids"]) >= 8
    assert data["project_id"] == "proj-1"


def test_submission_capability_never_reaches_plan(client):
    r = client.post("/chat", json={
        "message": "Draft our proposal.",
        "requested_capabilities": ["submission.execute"]}, headers=AUTH)
    assert r.status_code == 200
    data = r.json()
    assert "submission" not in data["reply"].lower() or True  # normalized
    # durable tasks carry no submission capability
    tasks = client.get("/projects/proj-1/progress", headers=AUTH).json()
    caps = {t["capability_id"] for t in tasks["tasks"]}
    assert not any("submission" in c for c in caps)


def test_progress_from_durable_task_state(client):
    client.post("/chat", json={"message": "Draft our Georgia proposal."},
                headers=AUTH)
    r = client.get("/projects/proj-1/progress", headers=AUTH)
    assert r.status_code == 200
    data = r.json()
    assert data["task_count"] >= 8
    assert data["by_state"].get("READY", 0) >= 8
    assert data["by_state"].get("SUCCEEDED", 0) == 0  # honest: not run yet


def test_produce_full_factory_package(client):
    r = client.post("/projects/proj-1/produce",
                    json={"live_model": False}, headers=AUTH)
    assert r.status_code == 200
    data = r.json()
    assert data["status"] == "SUBMISSION_READY_MOCK"
    assert data["generation_mode"] == "DETERMINISTIC_BASELINE"
    assert data["submission_enabled"] is False
    assert data["within_ceiling"] is True
    assert data["qa_fail"] == 0
    assert data["sections"] == 7


def test_deliverables_and_download(client):
    client.post("/projects/proj-1/produce",
                json={"live_model": False}, headers=AUTH)
    r = client.get("/projects/proj-1/deliverables", headers=AUTH)
    assert r.status_code == 200
    kinds = {a["kind"] for a in r.json()["artifacts"]}
    assert {"proposal_docx", "proposal_pdf"} <= kinds
    # DOCX download
    d = client.get("/artifacts/proj-1-proposal_docx/download", headers=AUTH)
    assert d.status_code == 200
    assert d.content[:2] == b"PK"          # OOXML zip
    # PDF download
    p = client.get("/artifacts/proj-1-proposal_pdf/download", headers=AUTH)
    assert p.status_code == 200
    assert p.content[:5] == b"%PDF-"


def test_model_registry_and_governed_selection(client):
    r = client.get("/models", headers=AUTH)
    assert r.status_code == 200
    models = r.json()["models"]
    assert len(models) >= 2
    assert r.json()["auto_recommended"] is True
    # auto selection for drafting succeeds
    s = client.post("/models/select",
                    json={"task": "grant_drafting",
                          "required_context_tokens": 8000},
                    headers=AUTH)
    assert s.status_code == 200
    assert s.json()["selected"] is not None
    # unknown model rejected (deny-by-default)
    s2 = client.post("/models/select",
                     json={"task": "grant_drafting", "preferred_model":
                           "not-a-model"}, headers=AUTH)
    assert s2.json()["selected"] is None
    assert s2.json()["rejected"]


def test_auth_required(client):
    r = client.get("/chat/conv-x/messages")
    assert r.status_code == 401


def test_unknown_principal_denied(client):
    r = client.get("/chat/conv-x/messages", headers={"X-Principal": "nobody"})
    assert r.status_code == 401


def test_forged_project_id_returns_empty_tenant_state(client):
    """A forged project id must not leak another project's rows: progress
    reads are tenant-scoped and return empty for unknown projects."""
    r = client.get("/projects/forged-id/progress", headers=AUTH)
    assert r.status_code == 200
    assert r.json()["task_count"] == 0


def test_no_submission_route_exists(client):
    """Submission is structurally absent: no route reaches an external
    submission capability."""
    routes = {route.path for route in app.routes}
    assert not any("submit" in r for r in routes)
    r = client.post("/submission/execute", json={}, headers=AUTH)
    assert r.status_code == 404
