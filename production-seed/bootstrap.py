#!/usr/bin/env python3
"""G0-B9-C15/C25 — local-first bootstrap (SQLite TEST_ONLY / DEV_FAST_PATH).

Applies the SQLite migration files (migrations/*.sql) onto an EMPTY sqlite
database for dev/CI and local seed verification. These SQLite files are
NOT production Postgres SQL — per the P1-01 migration-truth repair the
canonical production path is migrations/postgres/ (TIMESTAMPTZ/now()/jsonb),
exercised by the G1 migration runner and tests/test_postgres_migration.py.

Usage:
    python bootstrap.py --db sqlite:///./dev.db
"""
from __future__ import annotations

import argparse
import sqlite3
import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parent
MIGRATIONS = sorted((_ROOT / "migrations").glob("*.sql"))


def _migrate_sqlite(path: str) -> None:
    conn = sqlite3.connect(path.replace("sqlite:///", ""))
    for m in MIGRATIONS:
        conn.executescript(m.read_text(encoding="utf-8"))
    conn.commit()
    conn.close()
    print(f"migrated {len(MIGRATIONS)} migration(s) into {path}")


def _migrate_postgres(url: str) -> None:
    # Postgres is NOT bootstrapped from the SQLite files: they use
    # SQLite-only strftime() defaults and are TEST_ONLY / DEV_FAST_PATH.
    # The canonical production path is migrations/postgres/, applied by the
    # G1 migration runner in staging/CI (needs a DBAPI driver, e.g. psycopg).
    raise SystemExit(
        "Postgres bootstrap requires the G1 migration runner (psycopg + "
        "alembic-style runner) applying migrations/postgres/ — the SQLite "
        "DEV_FAST_PATH files are not Postgres SQL and must not be run "
        "against a Postgres server.")


def main() -> int:
    ap = argparse.ArgumentParser(description="Bootstrap the seed DB")
    ap.add_argument("--db", default="sqlite:///./dev.db")
    args = ap.parse_args()
    if args.db.startswith("sqlite"):
        _migrate_sqlite(args.db)
    elif args.db.startswith("postgres"):
        _migrate_postgres(args.db)
    else:
        raise SystemExit(f"unsupported db URL: {args.db}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
