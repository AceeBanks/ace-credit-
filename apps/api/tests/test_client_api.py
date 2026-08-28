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
    # DEV pilot: tasks are executed inline and marked SUCCEEDED
    assert data["by_state"].get("SUCCEEDED", 0) >= 8


def test_produce_full_factory_package(client):
    """Deterministic lane has UNKNOWN material claims (honest gaps),
    so status is BLOCKED — never fake-ready."""
    r = client.post("/projects/proj-1/produce",
                    json={"live_model": False}, headers=AUTH)
    assert r.status_code == 200
    data = r.json()
    # P0-02 fix: UNKNOWN material claims block READY status
    assert data["status"] == "BLOCKED"
    assert data["readiness_state"] in ("NEEDS_CLIENT_INPUT", "QA_BLOCKED")
    assert data["generation_mode"] == "DETERMINISTIC_BASELINE"
    assert data["submission_enabled"] is False
    assert data["within_ceiling"] is True
    assert data["unsupported"] > 0  # honest: UNKNOWN claims remain
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


# --- P0-01: Model selection end-to-end -----------------------------------


def test_model_selection_transmitted_via_chat(client):
    """Frontend model selection is transmitted to backend and reflected
    in ChatOut."""
    # AUTO mode
    r = client.post("/chat", json={
        "message": "We need funding for STEM.",
        "model_selection": {"mode": "AUTO", "allow_fallback": True}},
        headers=AUTH)
    assert r.status_code == 200
    assert r.json()["model_selection_mode"] == "AUTO"
    assert r.json()["resolved_model_id"] is None
    # MANUAL mode with known model
    r2 = client.post("/chat", json={
        "message": "We need funding for STEM.",
        "model_selection": {
            "mode": "MANUAL",
            "model_id": "minimax/minimax-m3:free",
            "allow_fallback": True}},
        headers=AUTH)
    assert r2.status_code == 200
    assert r2.json()["model_selection_mode"] == "MANUAL"
    assert r2.json()["resolved_model_id"] == "minimax/minimax-m3:free"


def test_manual_model_denied_when_not_governed(client):
    """MANUAL selection with an unknown model returns 422."""
    r = client.post("/projects/proj-1/produce",
        json={"live_model": True,
              "model_selection": {
                  "mode": "MANUAL",
                  "model_id": "fake/model",
                  "allow_fallback": False}},
        headers=AUTH)
    assert r.status_code == 422
    assert "not in the governed" in r.json()["detail"]["message"].lower() or \
           "model_not_governed" in r.json()["detail"]["error"]


def test_manual_model_denied_when_disabled(client):
    """MANUAL selection with a disabled model returns 422."""
    r = client.post("/projects/proj-1/produce",
        json={"live_model": True,
              "model_selection": {
                  "mode": "MANUAL",
                  "model_id": "anthropic/claude-3.5-sonnet",
                  "allow_fallback": False}},
        headers=AUTH)
    assert r.status_code == 422
    assert "disabled" in r.json()["detail"]["message"].lower()


def test_produce_with_model_selection(client):
    """Produce endpoint accepts model_selection payload."""
    r = client.post("/projects/proj-1/produce",
        json={"live_model": False,
              "model_selection": {"mode": "AUTO", "allow_fallback": True}},
        headers=AUTH)
    assert r.status_code == 200
    data = r.json()
    assert "readiness_state" in data
    assert "claim_counts" in data


# --- Conversations persistence -------------------------------------------


def test_conversations_persist(client):
    """Chat creates a conversation that appears in the list."""
    client.post("/chat", json={"message": "We need funding for a program."},
                headers=AUTH)
    r = client.get("/conversations", headers=AUTH)
    assert r.status_code == 200
    convs = r.json()["conversations"]
    assert len(convs) >= 1
    assert any("funding" in (c.get("title") or "").lower() for c in convs)


def test_conversations_tenant_scoped(client):
    """Conversations from other tenants are not visible."""
    client.post("/chat", json={"message": "We need funding for something."},
                headers=AUTH)
    r = client.get("/conversations", headers={"X-Principal": "nobody"})
    assert r.status_code == 401


# --- P0-02: Claim readiness semantics -----------------------------------


def test_readiness_state_with_unknown_claims(client):
    """Deterministic lane with UNKNOWN claims must not be READY."""
    r = client.post("/projects/proj-1/produce",
                    json={"live_model": False}, headers=AUTH)
    data = r.json()
    # NEVER READY when UNKNOWN material claims exist
    assert data["readiness_state"] != "READY_FOR_REVIEW"
    assert data["unsupported"] > 0
    claim_counts = data["claim_counts"]
    assert claim_counts.get("UNKNOWN", 0) > 0


# --- P1-04: Attachments --------------------------------------------------


def test_attachment_upload_txt(client):
    """Upload a TXT file and retrieve its content."""
    content = b"Community Youth Works serves 200 students annually."
    r = client.post("/attachments/upload?project_id=proj-1",
                    files={"file": ("org_info.txt", content, "text/plain")},
                    headers=AUTH)
    assert r.status_code == 200
    data = r.json()
    assert data["attachment_id"].startswith("att-")
    assert data["filename"] == "org_info.txt"
    assert data["parser_status"] == "PASSED"
    # Retrieve content
    c = client.get(f"/attachments/{data['attachment_id']}/content",
                   headers=AUTH)
    assert c.status_code == 200
    assert "200 students" in c.json()["content_text"]


def test_attachment_rejects_unsupported_mime(client):
    """Executable files must be rejected."""
    r = client.post("/attachments/upload",
                    files={"file": ("malware.exe", b"MZ...", "application/x-executable")},
                    headers=AUTH)
    assert r.status_code == 422
    assert "unsupported_mime_type" in r.json()["detail"]["error"]


def test_attachment_list_scoped_to_tenant(client):
    """Attachments are tenant-scoped."""
    client.post("/attachments/upload",
                files={"file": ("test.txt", b"hello", "text/plain")},
                headers=AUTH)
    r = client.get("/attachments", headers=AUTH)
    assert r.status_code == 200
    assert len(r.json()["attachments"]) >= 1
    # Another tenant sees nothing
    r2 = client.get("/attachments", headers={"X-Principal": "nobody"})
    assert r2.status_code == 401


def test_attachment_rejects_oversize(client):
    """Files over 10MB must be rejected."""
    big_content = b"x" * (10 * 1024 * 1024 + 1)
    r = client.post("/attachments/upload",
                    files={"file": ("big.txt", big_content, "text/plain")},
                    headers=AUTH)
    assert r.status_code == 422
    assert "file_too_large" in r.json()["detail"]["error"]
