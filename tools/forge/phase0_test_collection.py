#!/usr/bin/env python3
"""Phase 0 Book 2 Part 3: Test collection without execution."""

import argparse
import json
import os
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


SCHEMA_VERSION = "0.1.0"
PART_ID = "PHASE-00-BOOK-02-PART-03"
DEFAULT_OUTPUT = Path("artifacts/forge/phase-00")


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def collect_tests_pytest(repo_root: Path, test_path: str = "tests") -> dict[str, Any]:
    """Collect test IDs using pytest --collect-only."""
    test_dir = repo_root / test_path
    if not test_dir.exists():
        return {
            "group_id": f"pytest-{test_path}",
            "test_path": test_path,
            "collected": 0,
            "passed": 0,
            "failed": 0,
            "skipped": 0,
            "uncollected": 0,
            "collection_error": "test directory does not exist",
            "test_ids": [],
        }
    
    try:
        result = subprocess.run(
            ["python", "-m", "pytest", "--collect-only", str(test_dir)],
            cwd=repo_root,
            capture_output=True,
            text=True,
            timeout=30,
        )
        
        # Parse pytest output to extract test IDs
        test_ids = []
        for line in result.stdout.split('\n'):
            if '::' in line and not line.startswith('='):
                # Extract test ID like tests/test_file.py::test_function
                test_id = line.strip().split()[0] if line.strip() else ""
                if test_id and '::' in test_id:
                    test_ids.append(test_id)
        
        return {
            "group_id": f"pytest-{test_path}",
            "test_path": test_path,
            "collected": len(test_ids),
            "passed": 0,
            "failed": 0,
            "skipped": 0,
            "uncollected": 0,
            "collection_error": None,
            "test_ids": test_ids,
        }
        
    except subprocess.TimeoutExpired:
        return {
            "group_id": f"pytest-{test_path}",
            "test_path": test_path,
            "collected": 0,
            "passed": 0,
            "failed": 0,
            "skipped": 0,
            "uncollected": 0,
            "collection_error": "collection timeout",
            "test_ids": [],
        }
    except Exception as e:
        return {
            "group_id": f"pytest-{test_path}",
            "test_path": test_path,
            "collected": 0,
            "passed": 0,
            "failed": 0,
            "skipped": 0,
            "uncollected": 0,
            "collection_error": str(e),
            "test_ids": [],
        }


def collect_all_test_groups(repo_root: Path) -> dict[str, Any]:
    """Collect tests from all relevant test directories."""
    test_groups = []
    
    # Define test groups based on component structure
    test_paths = [
        "tests",
        "srrs_opc/tests",
        "oce/backend/tests",
        "projects/trading/backtests/tests",
        "tests/forge",
    ]
    
    for test_path in test_paths:
        test_dir = repo_root / test_path
        if test_dir.exists():
            group_result = collect_tests_pytest(repo_root, test_path)
            test_groups.append(group_result)
    
    return {
        "schema_version": SCHEMA_VERSION,
        "artifact_type": "TestCollection",
        "part_id": PART_ID,
        "generated_at": utc_now(),
        "test_groups": test_groups,
        "summary": {
            "total_groups": len(test_groups),
            "total_collected": sum(g["collected"] for g in test_groups),
            "total_errors": sum(1 for g in test_groups if g["collection_error"]),
        },
    }


def write_test_collection(
    repo_root: Path,
    output_dir: Path,
) -> Path:
    """Collect and write test collection."""
    root = repo_root.resolve()
    destination = output_dir.resolve()

    collection = collect_all_test_groups(root)
    output_path = destination / "test-collection.json"

    output_path.parent.mkdir(parents=True, exist_ok=True)
    temporary = output_path.with_suffix(output_path.suffix + ".tmp")
    temporary.write_text(
        json.dumps(collection, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    os.replace(temporary, output_path)

    return output_path


def build_argument_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Collect Phase 0 Book 2 Part 3 test collection without execution.",
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
        help="Directory for test collection JSON artifact.",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_argument_parser().parse_args(list(argv) if argv is not None else None)
    root = args.root.resolve()
    output_dir = args.output_dir
    if not output_dir.is_absolute():
        output_dir = root / output_dir

    try:
        path = write_test_collection(root, output_dir)
    except Exception as exc:
        print(f"test collection failed: {exc}", file=sys.stderr)
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
