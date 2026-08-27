"""G1 Wave 5 — API dependencies.

Store is wired per-request from an app state factory (sqlite file in dev,
Postgres adapter in production — same repository interface). Auth is a
minimal session token -> principal lookup; tenant scope is enforced
structurally on every query (never client-supplied trust).
"""
from __future__ import annotations

import os
from pathlib import Path

from fastapi import Depends, Header, HTTPException, Request

from grant_platform.store.db import Store

# dev/CI default; production overrides via env (Postgres adapter)
DEFAULT_DB = Path(__file__).resolve().parents[1] / "var" / "g1.db"


def get_store(request: Request) -> Store:
    store: Store | None = request.app.state.store
    if store is None:
        raise HTTPException(status_code=503, detail="store not initialized")
    return store


def require_principal(store: Store = Depends(get_store),
                      x_principal: str | None = Header(default=None)) -> dict:
    """Minimal session gate: a principal header for dev; real session/JWT
    is the G1.10 hardening item. Tenant scope still comes from the
    principal's durable row, never from the client for reads."""
    if not x_principal:
        raise HTTPException(status_code=401, detail="missing principal")
    row = store.get_principal(x_principal)
    if row is None:
        raise HTTPException(status_code=401, detail="unknown principal")
    return dict(row)


def open_store(db_path: str | None = None) -> Store:
    """Create the Store with the migrations applied (empty-DB build)."""
    path = db_path or os.environ.get("G1_DB", ":memory:")
    if path != ":memory:":
        Path(path).parent.mkdir(parents=True, exist_ok=True)
    return Store.open(path)
