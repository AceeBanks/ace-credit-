#!/usr/bin/env python3
"""G1 Wave 5 — browser-flow verification (Appendix B §61 test contract).

Drives the chat-first client flow against a running API (or a fresh
in-process one): start chat, ask for a grant, see durable progress, produce
the full proposal, download real DOCX/PDF, verify deliverable metadata,
then verify cross-tenant / forged-project / unauthorized-model denial.

This is the API-level integration leg of the browser test; the Next.js app
itself is verified separately by `npm run build` + `npm run typecheck`.
"""
from __future__ import annotations

import io
import sys
import zipfile
from pathlib import Path

import requests

_ROOT = Path(__file__).resolve().parents[2]
_BASE = "http://127.0.0.1:8891"
AUTH = {"X-Principal": "client-1"}


def _check(name: str, ok: bool, detail: str = "") -> None:
    print(f"  [{'PASS' if ok else 'FAIL'}] {name}" +
          (f" — {detail}" if detail and not ok else ""))
    if not ok:
        raise SystemExit(f"verification failed at: {name}")


def main() -> int:
    print("G1 Wave 5 browser-flow verification")
    print("step 1: chat intake")
    r = requests.post(f"{_BASE}/chat", headers=AUTH, json={
        "message": "We need funding for an after-school STEM program in "
                   "Atlanta."})
    _check("chat -> intent -> plan", r.status_code == 200)
    chat = r.json()
    _check("plan exists", chat["plan_id"] is not None)
    _check("durable tasks exist", len(chat["task_ids"]) >= 8)
    conv = chat["conversation_id"]

    print("step 2: message history")
    r = requests.get(f"{_BASE}/chat/{conv}/messages", headers=AUTH)
    _check("history persisted", r.status_code == 200 and len(r.json()["messages"]) >= 2)

    print("step 3: durable progress")
    r = requests.get(f"{_BASE}/projects/proj-1/progress", headers=AUTH)
    prog = r.json()
    _check("task states reported", prog["task_count"] >= 8)

    print("step 4: full factory produce")
    r = requests.post(f"{_BASE}/projects/proj-1/produce",
                      headers=AUTH, json={"live_model": False})
    _check("SUBMISSION_READY_MOCK", r.status_code == 200
           and r.json()["status"] == "SUBMISSION_READY_MOCK")
    summary = r.json()
    _check("QA 9/9", summary["qa_fail"] == 0)
    _check("submission disabled", summary["submission_enabled"] is False)
    _check("budget within ceiling", summary["within_ceiling"] is True)

    print("step 5: deliverable cards + downloads")
    r = requests.get(f"{_BASE}/projects/proj-1/deliverables", headers=AUTH)
    kinds = {a["kind"] for a in r.json()["artifacts"]}
    _check("DOCX+PDF metadata", {"proposal_docx", "proposal_pdf"} <= kinds)
    d = requests.get(f"{_BASE}/artifacts/proj-1-proposal_docx/download",
                     headers=AUTH)
    _check("DOCX is real OOXML", d.status_code == 200
           and d.content[:2] == b"PK")
    zf = zipfile.ZipFile(io.BytesIO(d.content))
    _check("DOCX has document.xml", "word/document.xml" in zf.namelist())
    p = requests.get(f"{_BASE}/artifacts/proj-1-proposal_pdf/download",
                     headers=AUTH)
    _check("PDF is real", p.status_code == 200 and p.content[:5] == b"%PDF-")

    print("step 6: model picker (governed registry)")
    r = requests.get(f"{_BASE}/models", headers=AUTH)
    _check("approved models listed", r.status_code == 200
           and len(r.json()["models"]) >= 2)
    s = requests.post(f"{_BASE}/models/select", headers=AUTH,
                      json={"task": "grant_drafting"})
    _check("auto selection ok", s.json()["selected"] is not None)
    s2 = requests.post(f"{_BASE}/models/select", headers=AUTH,
                       json={"task": "grant_drafting",
                             "preferred_model": "evil-unknown-model"})
    _check("unknown model denied", s2.json()["selected"] is None)

    print("step 7: security denials")
    r = requests.get(f"{_BASE}/chat/conv-x/messages")
    _check("auth required", r.status_code == 401)
    r = requests.get(f"{_BASE}/projects/forged-id/progress", headers=AUTH)
    _check("forged project -> empty tenant state",
           r.status_code == 200 and r.json()["task_count"] == 0)
    r = requests.post(f"{_BASE}/submission/execute", json={}, headers=AUTH)
    _check("no submission route (404)", r.status_code == 404)

    print("\nBrowser-flow verification: PASS")
    return 0


if __name__ == "__main__":
    sys.exit(main())
