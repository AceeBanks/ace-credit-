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
from collections.abc import Callable
from pathlib import Path

import hashlib
import uuid

from fastapi import Depends, FastAPI, File, HTTPException, UploadFile
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
from grant_platform.store.objects import LocalObjectStore  # noqa: E402

# Attachment governance (Appendix B §18)
ALLOWED_MIME_TYPES = {
    "application/pdf",
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    "text/plain",
}
MAX_FILE_SIZE_BYTES = 10 * 1024 * 1024  # 10 MB
OBJ_STORE = LocalObjectStore(_ROOT / "var" / "g1-objects")

# Cache factory results so produce returns the same results as chat
_FACTORY_CACHE: dict[str, "FactoryPackage"] = {}

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


class ModelSelectionPayload(BaseModel):
    mode: str = "AUTO"                    # AUTO | MANUAL
    provider_id: str | None = None
    model_id: str | None = None
    allow_fallback: bool = True


class ChatIn(BaseModel):
    message: str
    conversation_id: str | None = None
    requested_capabilities: list[str] = []
    model_selection: ModelSelectionPayload | None = None


class ChatOut(BaseModel):
    conversation_id: str
    intent_id: str
    reply: str
    plan_id: str | None = None
    task_ids: list[str] = []
    project_id: str = "proj-1"
    model_selection_mode: str = "AUTO"
    resolved_model_id: str | None = None


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
    # Link conversation to project for history
    store.conn.execute(
        "UPDATE conversations SET project_id=?"
        " WHERE conversation_id=? AND tenant_id=?",
        ("proj-1", conv, principal["tenant_id"]))
    store.conn.commit()

    # --- Inline task execution (DEV/PILOT path) ---
    # In production, workers would claim tasks via the durable kernel.
    # For the local pilot, we execute the factory immediately and mark
    # each task as SUCCEEDED so the frontend poll→produce flow triggers.
    ms = body.model_selection
    mode = ms.mode if ms else "AUTO"
    resolved = ms.model_id if ms and ms.mode == "MANUAL" else None
    try:
        # Resolve model invoke for live model path
        model_invoke, resolved_id = _resolve_model_invoke(
            ms, mode == "MANUAL")
        if resolved_id:
            resolved = resolved_id
        # Run the full factory pipeline
        tenant_id = principal["tenant_id"]
        for task_id in exec_.task_ids:
            store.claim_task(task_id, tenant_id, "WORKER")
        factory = run_factory(
            project_id="proj-1", model_invoke=model_invoke,
            model_id=resolved)
        # Persist artifacts
        for kind, render in (("proposal_docx", factory.docx),
                             ("proposal_pdf", factory.pdf)):
            store.create_artifact(Artifact(
                artifact_id=f"proj-1-{kind}",
                artifact_version_id=render.artifact_version_id,
                tenant_id=tenant_id, project_id="proj-1",
                kind=kind, payload_ref=f"obj:proj-1/{kind}",
                content_hash=render.content_hash, version_number=1))
        # Mark all tasks as SUCCEEDED with result refs
        for task_id in exec_.task_ids:
            store.complete_task(
                task_id, tenant_id, "WORKER",
                f"ref:result:{task_id}")
        # Store factory summary for produce endpoint
        _FACTORY_CACHE["proj-1"] = factory
    except Exception as exc:
        # Mark tasks as FAILED so the frontend shows the error
        for task_id in exec_.task_ids:
            store.set_task_state(task_id, "FAILED",
                                 worker="WORKER")
        # Still return the reply so the user sees context
        pass

    return ChatOut(conversation_id=conv, intent_id=reply.intent.intent_id,
                   reply=reply.text, plan_id=exec_.plan.plan_id,
                   task_ids=exec_.task_ids,
                   model_selection_mode=mode,
                   resolved_model_id=resolved)


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
    model_selection: ModelSelectionPayload | None = None


def _resolve_model_invoke(body_model: ModelSelectionPayload | None,
                          live_model_flag: bool
                          ) -> tuple[Callable | None, str | None]:
    """Resolve the model invocation path from the client request.
    Returns (model_invoke or None, resolved_model_id or None).
    
    Route logic:
    - If live_model flag is True, route through the governed model gateway
    - If model_selection.mode == 'MANUAL' and a model_id is given, route
      through governed gateway with that specific model
    - If model_selection.mode == 'AUTO' and live_model is True, use AUTO
    - Otherwise: deterministic baseline (None)
    """
    from grant_platform.model.registry import ModelRegistry
    from grant_platform.model.selection import SelectionContext, select_model

    use_live = live_model_flag
    resolved_model_id: str | None = None

    if body_model is not None and body_model.mode == "MANUAL" and body_model.model_id:
        use_live = True
        resolved_model_id = body_model.model_id
    elif body_model is not None and body_model.mode == "AUTO" and live_model_flag:
        use_live = True

    if not use_live:
        return None, None

    # Validate MANUAL selection against governed registry
    if resolved_model_id:
        reg = ModelRegistry.load_default()
        try:
            profile = reg.get(resolved_model_id)
        except KeyError:
            raise HTTPException(
                status_code=422,
                detail={"error": "model_not_governed",
                        "model_id": resolved_model_id,
                        "message": f"Model '{resolved_model_id}' is not in the "
                                   "governed ModelRegistry (deny-by-default)"})
        if not profile.enabled or profile.availability == "DISABLED":
            raise HTTPException(
                status_code=422,
                detail={"error": "model_disabled",
                        "model_id": resolved_model_id,
                        "message": f"Model '{resolved_model_id}' is "
                                   "disabled in the governed registry"})

    # Attempt governed model invoke via the runtime tool
    try:
        from tools.g1.run_w4_live import build_governed_model_invoke
        model_invoke, _gw, _c = build_governed_model_invoke()
        return model_invoke, resolved_model_id
    except Exception:
        raise HTTPException(
            status_code=503,
            detail="governed model runtime unavailable; use live_model=false")


@app.post("/projects/{project_id}/produce")
def produce(project_id: str, body: ProduceIn,
            store: Store = Depends(get_store),
            principal: dict = Depends(require_principal)):
    """Run the full Grant factory. Routes through governed model gateway
    when live_model=True or a MANUAL model selection is provided.
    Otherwise uses the honest deterministic lane (never faked as model
    output). Uses cached factory from chat when available (no re-run)."""
    # Always validate model selection (even with cached factory)
    model_invoke, resolved_model_id = _resolve_model_invoke(
        body.model_selection, body.live_model)
    # Use cached factory from the chat flow if available (avoids re-running)
    if project_id in _FACTORY_CACHE:
        factory = _FACTORY_CACHE[project_id]
    else:
        factory = run_factory(project_id=project_id,
                              model_invoke=model_invoke,
                              model_id=resolved_model_id)
    # Always persist artifact metadata (idempotent INSERT OR REPLACE)
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
    """Serve artifact payload (DOCX/PDF) on demand.
    Uses cached factory from chat when available (avoids re-running).
    PDF opens inline in browser; DOCX triggers download.
    Auth accepts ?principal_id= query param for browser-native links."""
    # Find artifact in any project for this tenant
    tenant_id = principal["tenant_id"]
    rows = []
    for pid in ["proj-1"]:
        rows = [a for a in store.artifacts_for(pid)
                if a["artifact_id"] == artifact_id]
        if rows:
            break
    if not rows:
        raise HTTPException(status_code=404, detail="unknown artifact")
    project_id = rows[0]["project_id"]
    kind = rows[0]["kind"]
    # Use cached factory if available, otherwise regenerate
    if project_id in _FACTORY_CACHE:
        factory = _FACTORY_CACHE[project_id]
    else:
        factory = run_factory(project_id=project_id)
    payload = factory.docx.payload if kind == "proposal_docx" \
        else factory.pdf.payload
    if not payload:
        raise HTTPException(status_code=404, detail="artifact payload empty")
    is_docx = kind == "proposal_docx"
    media = ("application/vnd.openxmlformats-officedocument."
             "wordprocessingml.document" if is_docx
             else "application/pdf")
    ext = "docx" if is_docx else "pdf"
    # PDF: inline for browser viewing; DOCX: attachment for download
    disposition = f'attachment; filename="{project_id}-{kind}.{ext}"' \
        if is_docx else f'inline; filename="{project_id}-{kind}.{ext}"'
    return Response(content=payload, media_type=media,
                    headers={"Content-Disposition": disposition})


@app.get("/conversations")
def list_conversations(store: Store = Depends(get_store),
                      principal: dict = Depends(require_principal)):
    """Return all conversations for the current tenant (DEV pilot)."""
    tenant_id = principal["tenant_id"]
    rows = store.conn.execute(
        "SELECT * FROM conversations WHERE tenant_id=?"
        " ORDER BY created_at DESC", (tenant_id,)).fetchall()
    return {"conversations": [dict(r) for r in rows]}


# --- Attachments (Appendix B §18) ----------------------------------------


@app.post("/attachments/upload")
async def upload_attachment(
    file: UploadFile = File(...),
    project_id: str | None = None,
    conversation_id: str | None = None,
    store: Store = Depends(get_store),
    principal: dict = Depends(require_principal),
):
    """Governed file upload. Validates MIME type, size limit, hashes content,
    stores in object store, records metadata with artifact provenance."""
    # 1. MIME type gate
    if file.content_type not in ALLOWED_MIME_TYPES:
        raise HTTPException(
            status_code=422,
            detail={"error": "unsupported_mime_type",
                    "mime_type": file.content_type,
                    "allowed": sorted(ALLOWED_MIME_TYPES)})
    # 2. Read and enforce size limit
    content = await file.read()
    if len(content) > MAX_FILE_SIZE_BYTES:
        raise HTTPException(
            status_code=422,
            detail={"error": "file_too_large",
                    "size_bytes": len(content),
                    "max_bytes": MAX_FILE_SIZE_BYTES})
    # 3. Content hash + object store
    content_hash = hashlib.sha256(content).hexdigest()
    filename = file.filename or "upload.bin"
    ext = filename.rsplit(".", 1)[-1] if "." in filename else "bin"
    attachment_id = f"att-{uuid.uuid4().hex[:12]}"
    object_key = f"attachments/{principal['tenant_id']}/{attachment_id}.{ext}"
    OBJ_STORE.put(object_key, content, file.content_type or "application/octet-stream")
    # 4. Parse text content for PDF/DOCX/TXT
    content_text: str | None = None
    parser_status = "PASSED"
    if file.content_type == "text/plain":
        content_text = content.decode("utf-8", errors="replace")
    elif file.content_type == "application/pdf":
        try:
            import fitz  # PyMuPDF
            doc = fitz.open(stream=content, filetype="pdf")
            content_text = "\n".join(page.get_text() for page in doc)
            doc.close()
        except Exception:
            parser_status = "PARSE_ERROR"
    elif "wordprocessingml" in (file.content_type or ""):
        try:
            import zipfile as _zf
            import xml.etree.ElementTree as ET
            with _zf.ZipFile(__import__("io").BytesIO(content)) as zf:
                doc_xml = zf.read("word/document.xml")
                root = ET.fromstring(doc_xml)
                ns = {"w": "http://schemas.openxmlformats.org/wordprocessingml/2006/main"}
                paragraphs = root.findall(".//w:p", ns)
                texts = []
                for p in paragraphs:
                    t = "".join(r.text or "" for r in p.findall(".//w:t", ns))
                    if t.strip():
                        texts.append(t.strip())
                content_text = "\n".join(texts)
        except Exception:
            parser_status = "PARSE_ERROR"
    # 5. Persist metadata
    store.create_attachment({
        "attachment_id": attachment_id,
        "tenant_id": principal["tenant_id"],
        "project_id": project_id,
        "conversation_id": conversation_id,
        "filename": filename,
        "mime_type": file.content_type or "application/octet-stream",
        "content_hash": content_hash,
        "file_size_bytes": len(content),
        "object_key": object_key,
        "parser_status": parser_status,
        "content_text": content_text,
        "uploaded_by": principal["principal_id"],
    })
    return {
        "attachment_id": attachment_id,
        "filename": filename,
        "mime_type": file.content_type,
        "content_hash": content_hash,
        "file_size_bytes": len(content),
        "parser_status": parser_status,
        "message": "uploaded",
    }


@app.get("/attachments")
def list_attachments(
    project_id: str | None = None,
    store: Store = Depends(get_store),
    principal: dict = Depends(require_principal),
):
    """List attachments for the current tenant/project."""
    tenant_id = principal["tenant_id"]
    attachments = store.attachments_for(tenant_id, project_id)
    # Strip content_text for listing (too large)
    safe = [{k: v for k, v in a.items() if k != "content_text"}
            for a in attachments]
    return {"attachments": safe}


@app.get("/attachments/{attachment_id}/content")
def get_attachment_content(
    attachment_id: str,
    store: Store = Depends(get_store),
    principal: dict = Depends(require_principal),
):
    """Return parsed text content of an attachment."""
    att = store.get_attachment(attachment_id, principal["tenant_id"])
    if not att:
        raise HTTPException(status_code=404, detail="attachment not found")
    return {
        "attachment_id": attachment_id,
        "filename": att["filename"],
        "content_text": att.get("content_text"),
        "parser_status": att["parser_status"],
    }


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
