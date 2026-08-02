#!/usr/bin/env python3
"""
Phase 0 Book 2: Bounded Test Execution.

This module runs bounded test groups for Phase 0 baseline.
It uses the discovered test commands and executes them in groups.

SECURITY: P0-REPAIR-01 - Uses strict approved-command allowlist and shell=False
Do not infer commands from repository text. Only approved commands may execute.
"""

from __future__ import annotations

import argparse
import json
import shlex
import subprocess
import sys
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

# Windows-specific subprocess flags (ERR-0007)
try:
    CREATE_NO_WINDOW = subprocess.CREATE_NO_WINDOW if sys.platform == 'win32' else 0
except AttributeError:
    CREATE_NO_WINDOW = 0

SCHEMA_VERSION = "0.1.0"
PART_ID = "PHASE-00-BOOK-02-BOUNDED-EXECUTION"
DEFAULT_OUTPUT = Path("artifacts/forge/phase-00/book-02")

# Strict approved-command allowlist (P0-REPAIR-01)
# Only these base commands are permitted for execution
APPROVED_COMMANDS = {
    "python",
    "python3",
    "pytest",
    "python3-m",
    "pip",
    "pip3",
}


def parse_command(cmd_str: str) -> list[str] | None:
    """
    Parse command string into list of arguments.
    Returns None if command is not in approved allowlist.
    """
    try:
        # Parse the command safely
        args = shlex.split(cmd_str)
        if not args:
            return None
        
        # Check if base command is approved
        base_cmd = args[0]
        if base_cmd not in APPROVED_COMMANDS:
            return None
        
        return args
    except (ValueError, shlex.Error):
        return None


def run_command(cmd: str, timeout: int = 300) -> dict[str, Any]:
    """
    Run a command and capture results.
    Uses shell=False and strict allowlist per P0-REPAIR-01.
    Windows subprocess flags prevent window flashing (ERR-0007).
    """
    # Parse and validate command
    args = parse_command(cmd)
    if args is None:
        return {
            "command": cmd,
            "exit_code": -2,
            "stdout": "",
            "stderr": "Command not in approved allowlist or invalid syntax",
            "success": False,
            "blocked": True,
        }
    
    # Windows-specific flags to prevent window flashing (ERR-0007)
    creation_flags = CREATE_NO_WINDOW
    
    try:
        result = subprocess.run(
            args,
            shell=False,  # P0-REPAIR-01: security fix
            capture_output=True,
            text=True,
            timeout=timeout,
            creationflags=creation_flags,  # ERR-0007: prevent window flashing
        )
        return {
            "command": cmd,
            "exit_code": result.returncode,
            "stdout": result.stdout,
            "stderr": result.stderr,
            "success": result.returncode == 0,
        }
    except subprocess.TimeoutExpired:
        return {
            "command": cmd,
            "exit_code": -1,
            "stdout": "",
            "stderr": "Command timed out",
            "success": False,
            "timed_out": True,
        }
    except Exception as e:
        return {
            "command": cmd,
            "exit_code": -1,
            "stdout": "",
            "stderr": str(e),
            "success": False,
        }


def run_bounded_tests(discovery_path: Path) -> dict[str, Any]:
    """Run bounded test groups from discovery."""
    # Load discovery
    with open(discovery_path, "r") as f:
        discovery = json.load(f)
    
    commands = discovery.get("commands", [])
    
    # Group by type
    forge_tests = [c for c in commands if c["command_id"].startswith("FORGE-PHASE00")]
    
    # Run groups
    results = {
        "forge_phase_00": {
            "collected": len(forge_tests),
            "passed": 0,
            "failed": 0,
            "skipped": 0,
            "duration_seconds": 0,
            "results": [],
        }
    }
    
    # Run Phase 0 tests
    start_time = datetime.now(UTC)
    
    for cmd in forge_tests:
        cmd_str = cmd["command"]
        print(f"Running: {cmd_str}")
        
        result = run_command(cmd_str, timeout=120)
        results["forge_phase_00"]["results"].append(result)
        
        if result["success"]:
            results["forge_phase_00"]["passed"] += 1
        else:
            results["forge_phase_00"]["failed"] += 1
    
    duration = (datetime.now(UTC) - start_time).total_seconds()
    results["forge_phase_00"]["duration_seconds"] = duration
    
    return {
        "schema_version": SCHEMA_VERSION,
        "part_id": PART_ID,
        "generated_at": datetime.now(UTC).isoformat(),
        "discovery_path": str(discovery_path).replace("\\", "/"),
        "test_groups": results,
        "total_tests": len(forge_tests),
        "total_passed": results["forge_phase_00"]["passed"],
        "total_failed": results["forge_phase_00"]["failed"],
        "total_duration": duration,
    }


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Phase 0 Book 2: Bounded Test Execution"
    )
    parser.add_argument(
        "--discovery",
        type=Path,
        default=Path("artifacts/forge/phase-00/book-02/test-discovery.json"),
        help="Test discovery path",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=DEFAULT_OUTPUT,
        help="Output directory for artifacts",
    )
    
    args = parser.parse_args()
    
    # Ensure output directory exists
    args.output_dir.mkdir(parents=True, exist_ok=True)
    
    # Run bounded tests
    execution = run_bounded_tests(args.discovery)
    
    # Write artifact
    execution_path = args.output_dir / "bounded-test-execution.json"
    with open(execution_path, "w") as f:
        json.dump(execution, f, indent=2)
    
    # Generate part evidence
    part_evidence = {
        "part_id": PART_ID,
        "schema_version": SCHEMA_VERSION,
        "generated_at": datetime.now(UTC).isoformat(),
        "status": "implemented_unverified",
        "artifacts": {
            "bounded_test_execution": str(execution_path).replace("\\", "/"),
        },
    }
    
    evidence_path = args.output_dir / "part-02-bounded-execution-evidence.json"
    with open(evidence_path, "w") as f:
        json.dump(part_evidence, f, indent=2)
    
    print(json.dumps(part_evidence, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())