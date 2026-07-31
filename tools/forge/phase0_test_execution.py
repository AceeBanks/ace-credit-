#!/usr/bin/env python3
"""Phase 0 Book 2 Part 4: Bounded test execution."""

import argparse
import json
import os
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


SCHEMA_VERSION = "0.1.0"
PART_ID = "PHASE-00-BOOK-02-PART-04"
DEFAULT_OUTPUT = Path("artifacts/forge/phase-00")


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def run_test_group(repo_root: Path, test_path: str, group_id: str) -> dict[str, Any]:
    """Run a test group and collect results."""
    test_dir = repo_root / test_path
    if not test_dir.exists():
        return {
            "group_id": group_id,
            "test_path": test_path,
            "collected": 0,
            "passed": 0,
            "failed": 0,
            "skipped": 0,
            "xfailed": 0,
            "xpassed": 0,
            "uncollected": 0,
            "duration_seconds": 0,
            "execution_error": "test directory does not exist",
            "log_path": None,
        }
    
    try:
        result = subprocess.run(
            ["python", "-m", "pytest", "-v", str(test_dir)],
            cwd=repo_root,
            capture_output=True,
            text=True,
            timeout=60,
        )
        
        # Parse pytest output for counts
        passed = result.stdout.count("PASSED")
        failed = result.stdout.count("FAILED")
        skipped = result.stdout.count("SKIPPED")
        xfailed = result.stdout.count("XFAIL")
        xpassed = result.stdout.count("XPASS")
        
        # Save log
        log_dir = repo_root / "artifacts" / "forge" / "phase-00" / "logs"
        log_dir.mkdir(parents=True, exist_ok=True)
        log_path = log_dir / f"{group_id}.log"
        log_path.write_text(result.stdout + "\n" + result.stderr, encoding="utf-8")
        
        return {
            "group_id": group_id,
            "test_path": test_path,
            "collected": passed + failed + skipped + xfailed + xpassed,
            "passed": passed,
            "failed": failed,
            "skipped": skipped,
            "xfailed": xfailed,
            "xpassed": xpassed,
            "uncollected": 0,
            "duration_seconds": 0,  # Would need to parse timing output
            "execution_error": None,
            "log_path": str(log_path.relative_to(repo_root)),
        }
        
    except subprocess.TimeoutExpired:
        return {
            "group_id": group_id,
            "test_path": test_path,
            "collected": 0,
            "passed": 0,
            "failed": 0,
            "skipped": 0,
            "xfailed": 0,
            "xpassed": 0,
            "uncollected": 0,
            "duration_seconds": 60,
            "execution_error": "execution timeout",
            "log_path": None,
        }
    except Exception as e:
        return {
            "group_id": group_id,
            "test_path": test_path,
            "collected": 0,
            "passed": 0,
            "failed": 0,
            "skipped": 0,
            "xfailed": 0,
            "xpassed": 0,
            "uncollected": 0,
            "duration_seconds": 0,
            "execution_error": str(e),
            "log_path": None,
        }


def run_all_test_groups(repo_root: Path) -> dict[str, Any]:
    """Run all safe test groups independently."""
    test_groups = []
    
    # Define test groups based on component structure
    test_configs = [
        ("tests", "ROOT-CORE"),
        ("srrs_opc/tests", "SRRA-OPH"),
        ("oce/backend/tests", "OCE-BACKEND"),
        ("projects/trading/backtests/tests", "TRADING-LAB"),
        ("tests/forge", "FORGE-TOOLS"),
    ]
    
    for test_path, group_id in test_configs:
        group_result = run_test_group(repo_root, test_path, group_id)
        test_groups.append(group_result)
    
    return {
        "schema_version": SCHEMA_VERSION,
        "artifact_type": "TestExecution",
        "part_id": PART_ID,
        "generated_at": utc_now(),
        "test_groups": test_groups,
        "summary": {
            "total_groups": len(test_groups),
            "total_collected": sum(g["collected"] for g in test_groups),
            "total_passed": sum(g["passed"] for g in test_groups),
            "total_failed": sum(g["failed"] for g in test_groups),
            "total_skipped": sum(g["skipped"] for g in test_groups),
            "total_errors": sum(1 for g in test_groups if g["execution_error"]),
        },
    }


def write_test_execution(
    repo_root: Path,
    output_dir: Path,
) -> Path:
    """Run tests and write execution results."""
    root = repo_root.resolve()
    destination = output_dir.resolve()

    execution = run_all_test_groups(root)
    output_path = destination / "test-execution.json"

    output_path.parent.mkdir(parents=True, exist_ok=True)
    temporary = output_path.with_suffix(output_path.suffix + ".tmp")
    temporary.write_text(
        json.dumps(execution, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    os.replace(temporary, output_path)

    return output_path


def build_argument_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Collect Phase 0 Book 2 Part 4 bounded test execution.",
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
        help="Directory for test execution JSON artifact.",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_argument_parser().parse_args(list(argv) if argv is not None else None)
    root = args.root.resolve()
    output_dir = args.output_dir
    if not output_dir.is_absolute():
        output_dir = root / output_dir

    try:
        path = write_test_execution(root, output_dir)
    except Exception as exc:
        print(f"test execution failed: {exc}", file=sys.stderr)
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
