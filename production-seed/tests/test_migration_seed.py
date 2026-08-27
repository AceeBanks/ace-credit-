"""G0-B9-C13 — migration seed must build from an EMPTY database.

Runs the SQLite TEST_ONLY / DEV_FAST_PATH schema (migrations/*.sql) against
a fresh in-memory sqlite DB and asserts every canonical table exists. This
is NOT Postgres evidence (P1-01 migration-truth repair): the canonical
production path is migrations/postgres/, exercised by
tests/test_postgres_migration.py. Proves no dependency on local historical
DB state.
"""
from __future__ import annotations

import sqlite3
import sys
from pathlib import Path

import pytest

_ROOT = Path(__file__).resolve().parents[1]
MIGRATIONS_DIR = _ROOT / "migrations"

REQUIRED_TABLES = [
    "tenants", "users", "principals", "capabilities", "grants",
    "approvals", "organizations", "opportunities", "opportunity_revisions",
    "application_projects", "requirements", "source_snapshots",
    "decision_records", "audit_events", "artifacts", "tasks",
]
# G1 Wave 3 Hermes runtime tables (migration 002)
REQUIRED_TABLES += [
    "conversations", "messages", "intents", "task_plans", "worker_results",
]


def _apply_migrations(conn: sqlite3.Connection) -> None:
    for path in sorted(MIGRATIONS_DIR.glob("*.sql")):
        conn.executescript(path.read_text(encoding="utf-8"))
    conn.commit()


def test_empty_db_builds_canonical_schema():
    conn = sqlite3.connect(":memory:")
    _apply_migrations(conn)
    cur = conn.execute(
        "SELECT name FROM sqlite_master WHERE type='table'")
    tables = {row[0] for row in cur.fetchall()}
    for t in REQUIRED_TABLES:
        assert t in tables, f"missing canonical table {t}"
    conn.close()


def test_schema_has_no_submission_capability():
    """Submission is structurally impossible: the seed defines no
    submission table and no submission capability anywhere."""
    conn = sqlite3.connect(":memory:")
    _apply_migrations(conn)
    cur = conn.execute(
        "SELECT name FROM sqlite_master WHERE type='table'")
    tables = {row[0] for row in cur.fetchall()}
    assert not any("submit" in t.lower() for t in tables)
    for path in sorted(MIGRATIONS_DIR.glob("*.sql")):
        sql = path.read_text(encoding="utf-8").lower()
        assert "application.submit" not in sql
        assert "application_submit" not in sql
    conn.close()


def test_foreign_keys_enforced():
    conn = sqlite3.connect(":memory:")
    conn.execute("PRAGMA foreign_keys=ON")
    _apply_migrations(conn)
    with pytest.raises(Exception):
        conn.execute(
            "INSERT INTO application_projects (project_id, tenant_id,"
            " organization_id, opportunity_id, revision_id)"
            " VALUES ('p1', 'missing-tenant', 'o1', 'opp1', 'rev1')")
    conn.close()


def test_sqlite_migrations_relabeled_dev_fast_path():
    """P1-01 repair: the SQLite schema must be labeled TEST_ONLY /
    DEV_FAST_PATH, never claiming Postgres portability, and the canonical
    Postgres migration path must exist."""
    for name in ("001_initial_schema.sql", "002_hermes_runtime.sql"):
        sql = (MIGRATIONS_DIR / name).read_text(encoding="utf-8")
        assert "TEST_ONLY" in sql, f"{name} missing TEST_ONLY label"
        assert "DEV_FAST_PATH" in sql, f"{name} missing DEV_FAST_PATH label"
        assert "portable SQL" not in sql.lower(), \
            f"{name} still claims portability"
        assert "portable" not in sql.lower()
    pg_dir = MIGRATIONS_DIR / "postgres"
    assert (pg_dir / "001_initial_schema.sql").exists()
    assert (pg_dir / "002_hermes_runtime.sql").exists()
    pg = (pg_dir / "001_initial_schema.sql").read_text(encoding="utf-8")
    assert "TIMESTAMPTZ" in pg and "now()" in pg
    assert "strftime" not in pg


def test_seed_rows_insert_and_query():
    conn = sqlite3.connect(":memory:")
    _apply_migrations(conn)
    conn.execute(
        "INSERT INTO tenants (tenant_id, display_name) VALUES ('t1', 'T')")
    conn.execute(
        "INSERT INTO users (user_id, tenant_id, display_name)"
        " VALUES ('u1', 't1', 'U')")
    conn.execute(
        "INSERT INTO principals (principal_id, tenant_id, principal_type,"
        " authority_level, user_id) VALUES ('p1', 't1', 'USER', 4, 'u1')")
    row = conn.execute("SELECT principal_type, authority_level FROM"
                       " principals WHERE principal_id='p1'").fetchone()
    assert row == ("USER", 4)
    conn.close()
