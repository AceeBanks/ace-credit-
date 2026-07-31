#!/usr/bin/env python3
"""Phase 0 Book 2 Part 6: Known-data backtest reproduction."""

import argparse
import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


SCHEMA_VERSION = "0.1.0"
PART_ID = "PHASE-00-BOOK-02-PART-06"
DEFAULT_OUTPUT = Path("artifacts/forge/phase-00")


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def check_backtest_fixtures(repo_root: Path) -> dict[str, Any]:
    """Check for available backtest fixtures."""
    fixture_paths = [
        "projects/trading/backtests/fixtures",
        "projects/trading/nautilus/fixtures",
        "projects/trading/strategies/fixtures",
        "data/fixtures",
    ]
    
    available_fixtures = []
    for fixture_path in fixture_paths:
        fixture_dir = repo_root / fixture_path
        if fixture_dir.exists():
            fixtures = list(fixture_dir.glob("*"))
            available_fixtures.extend([
                {
                    "path": str(f.relative_to(repo_root)),
                    "type": "file" if f.is_file() else "directory",
                    "size_bytes": f.stat().st_size if f.is_file() else 0,
                }
                for f in fixtures
            ])
    
    return {
        "available_fixtures": available_fixtures,
        "fixture_paths_checked": fixture_paths,
        "total_fixtures": len(available_fixtures),
    }


def document_backtest_gap(repo_root: Path) -> dict[str, Any]:
    """Document the critical gap in backtest reproduction capability."""
    fixtures = check_backtest_fixtures(repo_root)
    
    if fixtures["total_fixtures"] == 0:
        return {
            "schema_version": SCHEMA_VERSION,
            "artifact_type": "BacktestReproduction",
            "part_id": PART_ID,
            "generated_at": utc_now(),
            "engine_class": "unknown",
            "run_1_id": None,
            "run_2_id": None,
            "stable_fields_equal": None,
            "gap_identified": True,
            "gap_reason": "No backtest fixtures found in workspace",
            "gap_severity": "critical",
            "gap_impact": "Cannot satisfy canonical-engine requirement for Phase 0 baseline",
            "fixtures_check": fixtures,
            "recommendation": "Implement bounded backtest fixture in Phase 3 Data Forge or Phase 6 Strategy Forge",
        }
    
    # If fixtures exist, would attempt reproduction here
    return {
        "schema_version": SCHEMA_VERSION,
        "artifact_type": "BacktestReproduction",
        "part_id": PART_ID,
        "generated_at": utc_now(),
        "engine_class": "unknown",
        "run_1_id": None,
        "run_2_id": None,
        "stable_fields_equal": None,
        "gap_identified": True,
        "gap_reason": "Fixtures found but reproduction not implemented in Phase 0",
        "gap_severity": "medium",
        "fixtures_check": fixtures,
    }


def write_backtest_reproduction(
    repo_root: Path,
    output_dir: Path,
) -> Path:
    """Document backtest reproduction status."""
    root = repo_root.resolve()
    destination = output_dir.resolve()

    reproduction = document_backtest_gap(root)
    output_path = destination / "backtest-reproduction.json"

    output_path.parent.mkdir(parents=True, exist_ok=True)
    temporary = output_path.with_suffix(output_path.suffix + ".tmp")
    temporary.write_text(
        json.dumps(reproduction, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    os.replace(temporary, output_path)

    return output_path


def build_argument_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Collect Phase 0 Book 2 Part 6 backtest reproduction documentation.",
    )
    parser.add_argument(
        "--root",
        type=Path,
        default=Path.cwd(),
        help="Git repository root. Defaults to the current directory.",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=DEFAULT_OUTPUT,
        help="Directory for backtest reproduction JSON artifact.",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_argument_parser().parse_args(list(argv) if argv is not None else None)
    root = args.root.resolve()
    output_dir = args.output_dir
    if not output_dir.is_absolute():
        output_dir = root / output_dir

    try:
        path = write_backtest_reproduction(root, output_dir)
    except Exception as exc:
        print(f"backtest reproduction documentation failed: {exc}", file=sys.stderr)
        return 1

    result = {
        "part_id": PART_ID,
        "status": "implemented_unverified",
        "artifact": str(path.relative_to(root) if path.is_relative_to(root) else str(path)),
    }
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    sys.exit(main())
