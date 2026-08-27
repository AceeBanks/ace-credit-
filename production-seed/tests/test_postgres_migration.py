"""G0-FINAL-REPAIR-01 — Postgres migration integration test.

The canonical production database is Postgres. This test applies the
production migration path (`migrations/postgres/`) to a REAL Postgres
server and verifies tables, FK integrity, timestamp validity, indexes, and
empty-DB reproducibility with representative inserts.

Environment contract:
  * PG_TEST_DSN (e.g. postgresql://postgres:pass@localhost:5432/g1test)
    — when set AND reachable, the test runs for real;
  * otherwise the suite reports BLOCKED_ENVIRONMENT explicitly and does
    NOT fake PASS.

SQLite (migrations/*.sql) is DEV_FAST_PATH only and is never used here.
"""
from __future__ import annotations

import os
import sys
from pathlib import Path

import pytest

_ROOT = Path(__file__).resolve().parents[1]

PG_DSN = os.environ.get("PG_TEST_DSN", "")
PG_DIR = _ROOT / "migrations" / "postgres"

REQUIRED_TABLES = [
    "tenants", "users", "principals", "capabilities", "grants",
    "approvals", "organizations", "opportunities", "opportunity_revisions",
    "application_projects", "requirements", "source_snapshots",
    "decision_records", "audit_events", "artifacts", "tasks",
    # Hermes runtime (002)
    "conversations", "messages", "intents", "task_plans", "worker_results",
]


def _pg_available() -> bool:
    if not PG_DSN:
        return False
    try:
        import psycopg2
        conn = psycopg2.connect(PG_DSN, connect_timeout=3)
        conn.close()
        return True
    except Exception:
        return False


PG_AVAILABLE = _pg_available()


def _pg_skip_reason() -> str:
    return ("BLOCKED_ENVIRONMENT: no reachable Postgres server "
            "(set PG_TEST_DSN to run for real)")


requires_pg = pytest.mark.skipif(not PG_AVAILABLE, reason=_pg_skip_reason())


def test_postgres_sql_static_structure():
    """Static guard for the Postgres migration files (runs without a
    server). Catches the failure class where an inline comment swallows a
    required comma (a real defect found during the P1-01 repair)."""
    for path in sorted(PG_DIR.glob("*.sql")):
        text = path.read_text(encoding="utf-8")
        assert "strftime" not in text, f"SQLite-only syntax in {path.name}"
        assert "TIMESTAMPTZ" in text, f"missing Postgres type in {path.name}"
        lines = text.splitlines()
        depth = 0
        for i, line in enumerate(lines, 1):
            stripped = line.strip()
            if not stripped or stripped.startswith("--"):
                continue
            # inline comment swallows the rest of the line: any DDL line
            # with '--' must be complete BEFORE the comment
            if "--" in stripped:
                before = stripped.split("--", 1)[0].rstrip()
                assert before.endswith((",", "(", ")", ";")), \
                    f"{path.name}:{i} inline comment may swallow syntax: " \
                    f"{stripped[:70]}"
            depth += stripped.count("(") - stripped.count(")")
            assert depth >= 0, f"{path.name}:{i} unbalanced parens"
        assert depth == 0, f"{path.name} unbalanced parentheses"


def test_postgres_environment_status():
    """Machine-readable environment contract: this test ALWAYS runs and
    states the truth about whether Postgres was actually exercised."""
    assert not PG_AVAILABLE or True
    if PG_AVAILABLE:
        print("postgres_integration_status: EXECUTED")
    else:
        raise pytest.skip(
            "BLOCKED_ENVIRONMENT: no reachable Postgres server; "
            "SQLite DEV_FAST_PATH tests are NOT Postgres evidence "
            "(set PG_TEST_DSN=postgresql://... to run for real)")


def _connect():
    import psycopg2
    return psycopg2.connect(PG_DSN)


def _apply(conn) -> None:
    cur = conn.cursor()
    for path in sorted(PG_DIR.glob("*.sql")):
        cur.execute(path.read_text(encoding="utf-8"))
    conn.commit()
    cur.close()


@pytest.fixture()
def pg():
    """Ephemeral test schema: create a unique schema, apply migrations,
    yield, then drop (teardown). Does not touch other schemas."""
    import psycopg2
    conn = _connect()
    cur = conn.cursor()
    schema = f"g1test_{os.getpid()}"
    cur.execute(f'CREATE SCHEMA "{schema}"')
    cur.execute(f'SET search_path TO "{schema}"')
    conn.commit()
    # apply with search_path pinned so tables land in the test schema
    _apply(conn)
    yield conn, schema
    cur = conn.cursor()
    cur.execute(f'DROP SCHEMA "{schema}" CASCADE')
    conn.commit()
    conn.close()


@requires_pg
def test_empty_db_builds_all_canonical_tables(pg):
    conn, schema = pg
    cur = conn.cursor()
    cur.execute("""
        SELECT table_name FROM information_schema.tables
        WHERE table_schema = %s AND table_type = 'BASE TABLE'
    """, (schema,))
    tables = {row[0] for row in cur.fetchall()}
    for t in REQUIRED_TABLES:
        assert t in tables, f"missing canonical table {t} in Postgres"
    cur.close()


@requires_pg
def test_timestamps_are_timestamptz_default_now(pg):
    conn, schema = pg
    cur = conn.cursor()
    cur.execute("""
        SELECT column_default, data_type
        FROM information_schema.columns
        WHERE table_schema = %s AND table_name = 'tenants'
          AND column_name = 'created_at'
    """, (schema,))
    row = cur.fetchone()
    assert row is not None
    default, dtype = row
    assert "now()" in (default or "").lower()
    assert dtype == "timestamp with time zone"
    cur.close()


@requires_pg
def test_representative_inserts_and_fk_enforcement(pg):
    conn, schema = pg
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO tenants (tenant_id, display_name) VALUES (%s, %s)",
        ("t1", "Test"))
    cur.execute(
        "INSERT INTO users (user_id, tenant_id, display_name) "
        "VALUES (%s, %s, %s)", ("u1", "t1", "U"))
    cur.execute(
        "INSERT INTO principals (principal_id, tenant_id, principal_type,"
        " authority_level, user_id) VALUES (%s, %s, %s, %s, %s)",
        ("p1", "t1", "USER", 4, "u1"))
    cur.execute(
        "INSERT INTO capabilities (capability_id, required_level, delegable)"
        " VALUES (%s, %s, %s)", ("cap1", 1, False))
    cur.execute(
        "INSERT INTO grants (grant_id, principal_id, capability_id,"
        " authority_level, tenant_id) VALUES (%s, %s, %s, %s, %s)",
        ("g1", "p1", "cap1", 4, "t1"))
    cur.execute(
        "INSERT INTO organizations (organization_id, tenant_id, legal_name)"
        " VALUES (%s, %s, %s)", ("o1", "t1", "Community Youth Works, Inc."))
    cur.execute(
        "INSERT INTO opportunities (opportunity_id, tenant_id, title,"
        " funding_ceiling, deadline) VALUES (%s, %s, %s, %s, %s)",
        ("opp1", "t1", "Georgia Rural Community Impact Grant FY2026",
         "50000.00", "2026-10-15"))
    cur.execute(
        "INSERT INTO opportunity_revisions (revision_id, opportunity_id,"
        " revision_number, changed_terms, material) VALUES (%s, %s, %s, %s,"
        " %s)", ("rev1", "opp1", 1, '["deadline"]', True))
    cur.execute(
        "INSERT INTO application_projects (project_id, tenant_id,"
        " organization_id, opportunity_id, revision_id, state) VALUES"
        " (%s, %s, %s, %s, %s, %s)",
        ("proj1", "t1", "o1", "opp1", "rev1", "DRAFTING"))
    cur.execute(
        "INSERT INTO tasks (task_id, tenant_id, task_type, state,"
        " capability_id) VALUES (%s, %s, %s, %s, %s)",
        ("task1", "t1", "research.community", "READY", "research.community"))
    conn.commit()

    # FK integrity: a project referencing a missing tenant must fail
    with pytest.raises(Exception):
        cur.execute(
            "INSERT INTO application_projects (project_id, tenant_id,"
            " organization_id, opportunity_id, revision_id) VALUES"
            " (%s, %s, %s, %s, %s)",
            ("bad", "missing-tenant", "o1", "opp1", "rev1"))
    conn.rollback()
    cur.close()


@requires_pg
def test_task_state_check_constraint_enforced(pg):
    conn, schema = pg
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO tenants (tenant_id, display_name) VALUES (%s, %s)",
        ("t1", "T"))
    with pytest.raises(Exception):
        cur.execute(
            "INSERT INTO tasks (task_id, tenant_id, task_type, state)"
            " VALUES (%s, %s, %s, %s)",
            ("t-bad", "t1", "x", "NOT_A_STATE"))
    conn.rollback()
    cur.close()


@requires_pg
def test_revision_append_only_unique_per_opportunity(pg):
    conn, schema = pg
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO tenants (tenant_id, display_name) VALUES (%s, %s)",
        ("t1", "T"))
    cur.execute(
        "INSERT INTO opportunities (opportunity_id, tenant_id, title)"
        " VALUES (%s, %s, %s)", ("opp1", "t1", "O"))
    cur.execute(
        "INSERT INTO opportunity_revisions (revision_id, opportunity_id,"
        " revision_number) VALUES (%s, %s, %s)", ("rev1", "opp1", 1))
    # duplicate revision_number for the same opportunity must be rejected
    with pytest.raises(Exception):
        cur.execute(
            "INSERT INTO opportunity_revisions (revision_id,"
            " opportunity_id, revision_number) VALUES (%s, %s, %s)",
            ("rev1b", "opp1", 1))
    conn.rollback()
    cur.close()


@requires_pg
def test_source_snapshot_content_dedup(pg):
    conn, schema = pg
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO tenants (tenant_id, display_name) VALUES (%s, %s)",
        ("t1", "T"))
    cur.execute(
        "INSERT INTO source_snapshots (snapshot_id, source_uri, fetched_at,"
        " content_hash, tenant_id, payload_ref) VALUES (%s, %s, now(), %s,"
        " %s, %s)", ("snap1", "https://grants.gov/x", "abc123", "t1", "p1"))
    with pytest.raises(Exception):
        cur.execute(
            "INSERT INTO source_snapshots (snapshot_id, source_uri,"
            " fetched_at, content_hash, tenant_id, payload_ref) VALUES"
            " (%s, %s, now(), %s, %s, %s)",
            ("snap1b", "https://grants.gov/x", "abc123", "t1", "p1"))
    conn.rollback()
    cur.close()


@requires_pg
def test_indexes_present(pg):
    conn, schema = pg
    cur = conn.cursor()
    cur.execute("""
        SELECT indexname FROM pg_indexes WHERE schemaname = %s
    """, (schema,))
    indexes = {row[0] for row in cur.fetchall()}
    for expected in ("idx_tasks_tenant", "idx_audit_tenant",
                     "idx_decisions_tenant", "idx_messages_conversation"):
        assert expected in indexes, f"missing index {expected}"
    cur.close()
