#!/usr/bin/env python3
"""G1-QUALITY-PROD-LIVE-01 — AmeriCorps benchmark THROUGH THE REAL API.

Seeds a project whose revision resolves to the FY2026 AmeriCorps Georgia
benchmark into the REAL store, then drives the REAL running API over HTTP
(POST /projects/proj-bench/produce with AUTO) using the governed live model
(OPENROUTER_API_KEY). This proves the canonical quality pipeline runs in the
actual product production path — not a tool-only script.

Requires:
  - the API server running (start_grant_agent / uvicorn on :8000),
  - OPENROUTER_API_KEY exported (or in .env) for live generation.

Artifacts are written to docs/grant-sector/g1/quality-live/api/.
"""
from __future__ import annotations

import json
import sys
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[2]
for _p in (str(_ROOT), str(_ROOT / "production-seed")):
    if _p not in sys.path:
        sys.path.insert(0, _p)

from apps.api.deps import open_store  # noqa: E402
from apps.api.main import _seed_dev  # noqa: E402
from grant_platform.domain.records import (  # noqa: E402
    ApplicationProject, Opportunity, OpportunityRevision)

OUT_DIR = _ROOT / "docs" / "grant-sector" / "g1" / "quality-live" / "api"
# Overridable so the live run can target a dedicated instance without
# disturbing an already-running dev server.
import os as _os  # noqa: E402
API = _os.environ.get("G1_API_BASE", "http://127.0.0.1:8000")
AHEADER = {"X-Principal": "client-1", "Content-Type": "application/json"}


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _seed_real_store() -> None:
    store = open_store()  # same real file DB the running server uses
    _seed_dev(store)
    oid = "opp_americorps_ga_2026"
    rid = "ga_dca_nofp_2026"
    store.create_opportunity(Opportunity(
        opportunity_id=oid, tenant_id="tenant-a",
        title="FY2026 AmeriCorps State and National — Georgia Formula Grant"))
    store.create_revision(OpportunityRevision(
        revision_id=rid, opportunity_id=oid, revision_number=1))
    store.create_project(ApplicationProject(
        project_id="proj-bench", tenant_id="tenant-a",
        organization_id="org-a", opportunity_id=oid, revision_id=rid))
    store.close()
    print("[seed] proj-bench -> revision ga_dca_nofp_2026 ready", flush=True)


def _post(path: str, body: dict) -> tuple[int, object]:
    req = urllib.request.Request(API + path, method="POST",
                                 data=json.dumps(body).encode("utf-8"),
                                 headers=AHEADER)
    try:
        with urllib.request.urlopen(req, timeout=900) as resp:
            return resp.status, json.loads(resp.read().decode())
    except urllib.error.HTTPError as e:
        return e.code, json.loads(e.read().decode())


def main() -> int:
    import argparse
    parser = argparse.ArgumentParser(
        description="Run the AmeriCorps benchmark through the REAL API.")
    parser.add_argument("--model", default=None,
                        help="explicit model id (MANUAL mode); default AUTO")
    parser.add_argument("--rerun", action="store_true",
                        help="force a fresh live run (seed is idempotent)")
    args = parser.parse_args()
    _seed_real_store()
    sel = {"mode": "AUTO", "allow_fallback": True}
    if args.model:
        sel = {"mode": "MANUAL", "model_id": args.model,
               "allow_fallback": True}
    status, data = _post("/projects/proj-bench/produce", {
        "project_id": "proj-bench",
        "model_selection": sel,
    })
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    report = {"run_id": f"g1-quality-prod-live-{_now()}",
              "endpoint": "POST /projects/proj-bench/produce",
              "model_selection": sel,
              "http_status": status, "pipeline": data,
              "reproduce": ["python tools/g1/run_quality_api_benchmark.py",
                             "python tools/g1/run_quality_api_benchmark.py "
                             "--model z-ai/glm-5.2:free"]}
    (OUT_DIR / "G1_QUALITY_API_LIVE_REPORT.json").write_text(
        json.dumps(report, indent=2, default=str), encoding="utf-8")
    print(json.dumps({
        "http_status": status,
        "readiness_state": data.get("readiness_state"),
        "pipeline_label": data.get("pipeline_label"),
        "generation_mode": data.get("generation_mode"),
        "solicitation_id": data.get("solicitation_id"),
        "sections": data.get("sections"),
        "word_count": data.get("word_count"),
        "pdf_pages": data.get("pdf_pages"),
        "requirement_coverage_pct": data.get("requirement_coverage_pct"),
        "claims": data.get("claims"),
        "quality_score": data.get("quality_score", {}).get("overall_out_of_5"),
        "shallow_output": data.get("shallow_output", {}).get("shallow_output"),
    }, indent=2))
    print(f"Report: {OUT_DIR / 'G1_QUALITY_API_LIVE_REPORT.json'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())