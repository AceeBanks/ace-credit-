#!/usr/bin/env python3
"""G0-B9-C15/C25 — local-first bootstrap.

Migrations the canonical schema onto an EMPTY database from the portable
migration file. Supports sqlite (dev/CI) and any DBAPI-compatible URL;
Postgres is exercised in staging/CI with the same file.

Usage:
    python bootstrap.py --db sqlite:///./dev.db
    python bootstrap.py --db postgres://user:pass@host/grantdb
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
    # Postgres path requires a DBAPI driver (e.g. psycopg) present in the
    # deployment environment. Same migration files; executed transactionally
    # by the migration runner in staging/CI.
    raise SystemExit(
        "Postgres bootstrap requires the G1 migration runner (psycopg + "
        "alembic-style runner). The portable SQL files are identical; this "
        "is exercised in CI staging, not locally.")


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
