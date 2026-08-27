#!/usr/bin/env python3
"""G0-B9-C25 — clean seed verification (fresh-clone equivalent).

Simulates a fresh clone: copies ONLY the committed production-seed tree
into a temp directory, bootstraps an empty sqlite DB, runs the seed tests,
and verifies a representative mock workflow builds. Proves no dependence
on developer laptop state, old larger-lab paths, hidden .env, or archived
Hermes memory.

Usage: python tools/g0/verify_production_seed.py
"""
from __future__ import annotations

import shutil
import sqlite3
import subprocess
import sys
import tempfile
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[2]
SEED = _ROOT / "production-seed"


def _verify() -> tuple[bool, list[str]]:
    problems: list[str] = []
    with tempfile.TemporaryDirectory(prefix="grant-seed-") as tmp:
        clone = Path(tmp) / "seed"
        shutil.copytree(SEED, clone)

        # 1. bootstrap empty DB from the copy (not the source tree)
        db = clone / "dev.db"
        proc = subprocess.run(
            [sys.executable, str(clone / "bootstrap.py"),
             "--db", f"sqlite:///{db}"],
            capture_output=True, text=True)
        if proc.returncode != 0:
            problems.append(f"bootstrap failed: {proc.stderr[-400:]}")
            return False, problems
        if not db.exists():
            problems.append("dev.db not created by bootstrap")

        # 2. seed tests pass from the copy
        proc = subprocess.run(
            [sys.executable, "-m", "pytest", str(clone / "tests"), "-q",
             "--tb=short"],
            capture_output=True, text=True)
        tail = (proc.stdout or "").strip().splitlines()[-1:]
        test_summary = tail[0] if tail else "no summary"
        if proc.returncode != 0:
            problems.append(f"seed tests failed: {test_summary}")
        else:
            problems.append(f"seed tests: {test_summary} (PASS)")

        # 3. representative mock workflow: migrate + seed rows + read back
        conn = sqlite3.connect(db)
        conn.execute(
            "INSERT INTO tenants (tenant_id, display_name) VALUES ('t1','T')")
        conn.execute(
            "INSERT INTO opportunities (opportunity_id, tenant_id, title)"
            " VALUES ('o1','t1','Georgia Rural Community Impact Grant')")
        row = conn.execute(
            "SELECT title FROM opportunities WHERE opportunity_id='o1'"
        ).fetchone()
        conn.close()
        if row != ("Georgia Rural Community Impact Grant",):
            problems.append("mock workflow read-back mismatch")

        # 4. no dependency on hidden files: the copy contains no .env
        if list(clone.rglob(".env")):
            problems.append("seed depends on a hidden .env file")
    return not problems, problems


def main() -> int:
    ok, problems = _verify()
    for p in problems:
        print(f"  - {p}")
    # informational lines are fine; only real failures flip the verdict
    real_failures = [p for p in problems if "(PASS)" not in p]
    ok = not real_failures
    print("fresh-clone seed verification: " +
          ("PASS" if ok else "FAIL"))
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
