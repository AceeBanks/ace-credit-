"""G0-B9-C7..C30 — production architecture artifacts.

Verifies: canonical ownership frozen with no ambiguous dual ownership;
topology is modular-monolith-first; repository structure has hard rules;
seed manifest has lineage for every seeded item; G1 backlog classifies
every component (PROMOTE/HARDEN/REIMPLEMENT/NEW, no unnecessary rebuild);
architecture freeze has no P0 TBD; contradiction sweep passes; the
reconstruction guide answers the north-star questions.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

_ROOT = Path(__file__).resolve().parents[3]
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

SEED_DIR = _ROOT / "docs/grant-sector/g0/09-production-seed"
OWNERSHIP = SEED_DIR / "G0_B9_CANONICAL_STATE_OWNERSHIP.md"
TOPOLOGY = SEED_DIR / "G0_B9_PRODUCTION_SERVICE_TOPOLOGY.md"
REPO = SEED_DIR / "G0_B9_REPOSITORY_STRUCTURE.md"
MANIFEST = SEED_DIR / "G0_B9_SEED_MANIFEST.json"
BACKLOG = SEED_DIR / "G0_B9_G1_IMPLEMENTATION_BACKLOG.md"
BACKLOG_JSON = SEED_DIR / "G0_B9_G1_IMPLEMENTATION_BACKLOG.json"
FREEZE = SEED_DIR / "G0_B9_ARCHITECTURE_FREEZE.md"
SWEEP = SEED_DIR / "G0_B9_CONTRADICTION_SWEEP.md"
RECON = SEED_DIR / "G0_B9_RECONSTRUCTION_GUIDE.md"


def test_ownership_frozen_no_dual_ownership():
    text = OWNERSHIP.read_text(encoding="utf-8")
    assert "No ambiguous dual ownership" in text
    assert "Postgres is the only owner of workflow truth" in text
    assert "Object storage is the only owner of immutable payloads" in text
    assert "Redis/queue never owns consequential state" in text
    assert "Hermes memory is curated continuity, not truth" in text
    assert "Model runtime holds execution state only" in text


def test_topology_is_modular_monolith_first():
    text = TOPOLOGY.read_text(encoding="utf-8")
    assert "modular monolith" in text.lower()
    assert "extraction" in text.lower()
    assert "microservices merely to appear enterprise-grade" in text


def test_repo_structure_hard_rules():
    text = REPO.read_text(encoding="utf-8")
    assert "No trading directories" in text
    assert "migrations" in text
    assert "secrets never in" in text.lower() or "Secrets are never" in text


def test_seed_manifest_lineage_complete():
    data = json.loads(MANIFEST.read_text(encoding="utf-8"))
    assert data["repo_creation"] == "CLEAN_REPO_CREATION_PENDING_OPERATOR_ACTION"
    for item in data["seed_items"]:
        for field in ("seed_item_id", "destination", "source_type",
                      "owner_module", "reason"):
            assert item.get(field), f"{item.get('seed_item_id')} missing {field}"


def test_backlog_classifies_every_component():
    data = json.loads(BACKLOG_JSON.read_text(encoding="utf-8"))
    allowed = {"PROMOTE_FROM_G0", "HARDEN_FROM_G0",
               "REIMPLEMENT_PRODUCTION", "NEW"}
    seen_promote = False
    for epic in data["epics"]:
        for item in epic["items"]:
            assert item["classification"] in allowed, item
            if item["classification"] == "PROMOTE_FROM_G0":
                seen_promote = True
    assert seen_promote, "backlog must promote working G0 code, not rebuild it"
    # the three REIMPLEMENT items are the known production boundary
    text = BACKLOG.read_text(encoding="utf-8")
    assert "REIMPLEMENT_PRODUCTION" in text


def test_backlog_priority_rules():
    text = BACKLOG.read_text(encoding="utf-8")
    assert "correctness foundations" in text.lower()
    assert "client-visible vertical slice" in text.lower()
    assert "automatic submission" in text  # explicitly not prioritized


def test_architecture_freeze_no_p0_tbd():
    text = FREEZE.read_text(encoding="utf-8")
    assert "no unresolved P0 TBD" in text
    assert "RATIFIED" in text
    assert "REJECTED permanently" in text  # automatic submission
    # every decision has a status
    for line in text.splitlines():
        if line.strip().startswith("| ") and "Decision" not in line \
                and "---" not in line:
            assert any(s in line for s in (
                "RATIFIED", "PROVISIONAL_G1_VALIDATE", "DEFERRED",
                "REJECTED")), f"decision without status: {line}"


def test_contradiction_sweep_passes():
    text = SWEEP.read_text(encoding="utf-8")
    assert "no p0 contradiction" in text.lower()
    assert "PASS" in text


def test_reconstruction_guide_answers_all_questions():
    text = RECON.read_text(encoding="utf-8")
    for question in ("What product are we building?",
                     "Who is Personal Hermes?",
                     "Who is CEO Hermes?",
                     "Where is truth?",
                     "How is eligibility determined?",
                     "How are decisions replayed?",
                     "What runtime won?",
                     "Why were alternatives rejected?"):
        assert question in text, f"missing north-star question: {question}"
    assert "no tribal knowledge required" in text.lower()


def test_seed_directory_exists_with_migrations_and_tests():
    seed = _ROOT / "production-seed"
    assert (seed / "migrations").exists()
    assert (seed / "tests").exists()
    assert (seed / "bootstrap.py").exists()
    assert (seed / "config/env.example").exists()
