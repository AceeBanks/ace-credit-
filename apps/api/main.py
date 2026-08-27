"""G1 Wave 5 — client API main app.

Routes (Appendix B §52):
- POST /chat            client message -> Personal intent -> CEO plan -> tasks
- GET  /chat/{conv}/messages
- GET  /projects/{id}/progress      durable task states (never fake timers)
- POST /projects/{id}/produce       full Grant factory -> deliverables
- GET  /projects/{id}/deliverables  artifact metadata
- GET  /artifacts/{id}/download     DOCX/PDF payloads
- GET  /models                      governed Model Registry (Appendix A)
- POST /models/select               governed selection (auto/fallback)
- GET  /consoles                    Personal/CEO Hermes console refs

Submission is structurally absent — no route can reach an external
submission capability.
"""
from __future__ import annotations

import io
import json
import sys
from pathlib import Path

from fastapi import Depends, FastAPI, HTTPException
from fastapi.responses import Response
from pydantic import BaseModel

_ROOT = Path(__file__).resolve().parents[2]      # repo root (g0-worktree)
_SEED = _ROOT / "production-seed"
for _p in (str(_ROOT), str(_SEED)):
    if _p not in sys.path:
        sys.path.insert(0, _p)

from apps.api.deps import get_store, open_store, require_principal  # noqa: E402
from grant_platform.agents.ceo import CeoHermes  # noqa: E402
from grant_platform.agents.personal import PersonalHermes  # noqa: E402
from grant_platform.domain.records import (  # noqa: E402
    ApplicationProject,
    Artifact,
    Opportunity,
    OpportunityRevision,
    Organization,
    Principal,
    Tenant,
)
from grant_platform.factory.orchestrator import run_factory  # noqa: E402
from grant_platform.model.registry import ModelRegistry  # noqa: E402
from grant_platform.model.selection import (  # noqa: E402
    SelectionContext,
    select_model,
)
from grant_platform.runtime.tasks import TaskRunner  # noqa: E402
from grant_platform.store.db import Store  # noqa: E402

app = FastAPI(title="Grant Platform — G1 Client API",
              version="0.1.0",
              description="Chat-first client API. Submission disabled.")


@app.on_event("startup")
def _startup() -> None:
    app.state.store = open_store()
    _seed_dev(app.state.store)


@app.on_event("shutdown")
def _shutdown() -> None:
    store: Store = app.state.store
    if store is not None:
        store.close()


def _seed_dev(store: Store) -> None:
    """Deterministic dev seed: one tenant, client principal, the governed
    Georgia opportunity/revision/project. Test data, never production."""
    if store.get_tenant("tenant-a"):
        return
    store.create_tenant(Tenant(tenant_id="tenant-a", display_name="Dev"))
    store.create_principal(Principal(
        principal_id="client-1", tenant_id="tenant-a",
        principal_type="USER", authority_level=4))
    store.create_principal(Principal(
        principal_id="HERMES_CEO", tenant_id="tenant-a",
        principal_type="HERMES_CEO", authority_level=3))
    store.create_principal(Principal(
        principal_id="WORKER", tenant_id="tenant-a",
        principal_type="WORKER", authority_level=2))
    store.create_organization(Organization(
        organization_id="org-a", tenant_id="tenant-a",
        legal_name="Community Youth Works, Inc.",
        jurisdiction="Georgia", ein="58-2345671"))
    store.create_opportunity(Opportunity(
        opportunity_id="opp_ga_501", tenant_id="tenant-a",
        title="Georgia Rural Community Impact Grant FY2026",
        funding_ceiling="50000.00", deadline="2026-10-15"))
    store.create_revision(OpportunityRevision(
        revision_id="opp_rev_ga_501_1", opportunity_id="opp_ga_501",
        revision_number=1))
    store.create_project(ApplicationProject(
        project_id="proj-1", tenant_id="tenant-a", organization_id="org-a",
        opportunity_id="opp_ga_501", revision_id="opp_rev_ga_501_1"))


class ChatIn(BaseModel):
    message: str
    conversation_id: str | None = None
    requested_capabilities: list[str] = []


class ChatOut(BaseModel):
    conversation_id: str
    intent_id: str
    reply: str
    plan_id: str | None = None
    task_ids: list[str] = []
    project_id: str = "proj-1"


@app.post("/chat", response_model=ChatOut)
def chat(body: ChatIn, store: Store = Depends(get_store),
         principal: dict = Depends(require_principal)):
    """Chat-first entry: message -> Personal intent -> CEO plan -> tasks."""
    if principal["tenant_id"] != "tenant-a":
        raise HTTPException(status_code=403, detail="tenant not seeded")
    conv = body.conversation_id or f"conv-{principal['principal_id']}-0"
    ph = PersonalHermes(store)
    reply = ph.receive_message(
        conversation_id=conv, tenant_id=principal["tenant_id"],
        client_actor_id=principal["principal_id"], organization_id="org-a",
        content=body.message,
        requested_capabilities=body.requested_capabilities)
    ceo = CeoHermes(store)
    exec_ = ceo.plan(reply.intent, project_id="proj-1")
    return ChatOut(conversation_id=conv, intent_id=reply.intent.intent_id,
                   reply=reply.text, plan_id=exec_.plan.plan_id,
                   task_ids=exec_.task_ids)


@app.get("/chat/{conversation_id}/messages")
def messages(conversation_id: str, store: Store = Depends(get_store),
             principal: dict = Depends(require_principal)):
    rows = store.messages_for(conversation_id)
    return {"conversation_id": conversation_id, "messages": rows}


@app.get("/projects/{project_id}/progress")
def progress(project_id: str, store: Store = Depends(get_store),
             principal: dict = Depends(require_principal)):
    """Durable task states — progress is never timer-faked."""
    tasks = [t for t in store.tasks_for(principal["tenant_id"])
             if t.get("project_id") == project_id]
    counts: dict[str, int] = {}
    for t in tasks:
        counts[t["state"]] = counts.get(t["state"], 0) + 1
    return {"project_id": project_id, "task_count": len(tasks),
            "by_state": counts,
            "tasks": [{"task_id": t["task_id"], "state": t["state"],
                       "capability_id": t["capability_id"]} for t in tasks]}


class ProduceIn(BaseModel):
    project_id: str = "proj-1"
    live_model: bool = False


@app.post("/projects/{project_id}/produce")
def produce(project_id: str, body: ProduceIn,
            store: Store = Depends(get_store),
            principal: dict = Depends(require_principal)):
    """Run the full Grant factory. live_model=True routes through the
    governed Model Gateway when a runtime is configured; otherwise the
    honest deterministic lane is used (never faked as model output)."""
    if body.live_model:
        try:
            from tools.g1.run_w4_live import build_governed_model_invoke
            model_invoke, _gw, _c = build_governed_model_invoke()
        except Exception:
            raise HTTPException(
                status_code=503,
                detail="governed model runtime unavailable; use live_model=false")
    else:
        model_invoke = None
    factory = run_factory(project_id=project_id, model_invoke=model_invoke)
    # persist artifact metadata
    for kind, render in (("proposal_docx", factory.docx),
                         ("proposal_pdf", factory.pdf)):
        store.create_artifact(Artifact(
            artifact_id=f"{project_id}-{kind}",
            artifact_version_id=render.artifact_version_id,
            tenant_id=principal["tenant_id"], project_id=project_id,
            kind=kind, payload_ref=f"obj:{project_id}/{kind}",
            content_hash=render.content_hash, version_number=1))
    return factory.summary()


@app.get("/projects/{project_id}/deliverables")
def deliverables(project_id: str, store: Store = Depends(get_store),
                 principal: dict = Depends(require_principal)):
    return {"project_id": project_id,
            "artifacts": store.artifacts_for(project_id)}


@app.get("/artifacts/{artifact_id}/download")
def download(artifact_id: str, store: Store = Depends(get_store),
             principal: dict = Depends(require_principal)):
    """Regenerate the requested artifact payload (DOCX/PDF) on demand.
    Payloads are derivable from the durable draft; this is the dev/CI
    object-store stand-in (S3 adapter is G1.10)."""
    rows = [a for a in store.artifacts_for("proj-1")
            if a["artifact_id"] == artifact_id]
    if not rows:
        raise HTTPException(status_code=404, detail="unknown artifact")
    kind = rows[0]["kind"]
    factory = run_factory(project_id="proj-1")
    payload = factory.docx.payload if kind == "proposal_docx" \
        else factory.pdf.payload
    media = ("application/vnd.openxmlformats-officedocument."
             "wordprocessingml.document" if kind == "proposal_docx"
             else "application/pdf")
    return Response(content=payload, media_type=media,
                    headers={"Content-Disposition":
                             f'attachment; filename="{artifact_id}.'
                             f'{"docx" if kind == "proposal_docx" else "pdf"}"'})


class ModelSelectIn(BaseModel):
    task: str = "grant_drafting"
    required_context_tokens: int | None = None
    preferred_model: str | None = None
    fallback_enabled: bool = False


@app.get("/models")
def models(store: Store = Depends(get_store),
           principal: dict = Depends(require_principal)):
    reg = ModelRegistry.load_default()
    return {"models": [{"model_id": m.model_id,
                         "provider_id": m.provider_id,
                         "context_window_tokens": m.context_window_tokens,
                         "max_output_tokens": m.max_output_tokens,
                         "cost_tier": m.cost_tier,
                         "quality_tier": m.quality_tier,
                         "availability": m.availability,
                         "enabled": m.enabled}
                        for m in reg.all()],
            "auto_recommended": True}


@app.post("/models/select")
def select(body: ModelSelectIn, store: Store = Depends(get_store),
           principal: dict = Depends(require_principal)):
    """Governed selection (Appendix A): backend retains final authority.
    Unknown/incompatible models are rejected or safely fall back."""
    reg = ModelRegistry.load_default()
    est_in = body.required_context_tokens or 6000
    ctx = SelectionContext(
        task=body.task, estimated_input_tokens=est_in,
        expected_output_tokens=1500, system_overhead_tokens=500,
        long_form=body.task in ("grant_drafting", "full_proposal"),
        user_model=body.preferred_model, allow_fallback=body.fallback_enabled)
    result = select_model(ctx, reg.all())
    if not result.ok:
        return {"selected": None,
                "rejected": result.rejected_reasons,
                "message": "no eligible model; selection is governed"}
    return {"selected": {"model_id": result.selected.model_id,
                          "provider_id": result.selected.provider_id,
                          "fallback_used": result.fallback_used},
            "message": "model selection is governed; provider "
                       "neutrality preserved"}


@app.get("/consoles")
def consoles(store: Store = Depends(get_store),
             principal: dict = Depends(require_principal)):
    """Advanced Hermes console refs — normal users never pick Personal vs
    CEO; the system routes automatically (Appendix B §18)."""
    return {
        "personal_hermes": {"label": "Personal Hermes",
                            "console_ref": "hermes://personal",
                            "scope": "client relationship, intent, "
                                     "explanations"},
        "ceo_hermes": {"label": "CEO Hermes",
                       "console_ref": "hermes://ceo",
                       "scope": "plans, tasks, workers, execution"},
        "note": "Workers are never exposed as user-facing chats.",
    }
