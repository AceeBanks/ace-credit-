#!/usr/bin/env python3
"""Phase 0 Book 2: Environment Fingerprinting.

This module collects environment fingerprint data for Phase 0 Book 2 baseline.
It uses only the Python standard library and common system introspection.
"""

from __future__ import annotations

import argparse
import json
import os
import platform
import sys
from datetime import UTC, datetime
from pathlib import Path
from typing import Any
import subprocess
import shutil

SCHEMA_VERSION = "0.1.0"
PART_ID = "PHASE-00-BOOK-02-ENV-FINGERPRINT"
DEFAULT_OUTPUT = Path("artifacts/forge/phase-00/book-02")


def get_tool_version(tool_name: str) -> dict[str, Any]:
    """Get version information for a command-line tool."""
    result = {
        "name": tool_name,
        "present": False,
        "version": None,
        "path": None,
    }
    
    tool_path = shutil.which(tool_name)
    if tool_path:
        result["present"] = True
        result["path"] = tool_path
        
        try:
            if tool_name == "python":
                result["version"] = platform.python_version()
            elif tool_name == "python3":
                result["version"] = platform.python_version()
            elif tool_name == "node":
                completed = subprocess.run(
                    [tool_name, "--version"],
                    capture_output=True,
                    text=True,
                    timeout=5
                )
                result["version"] = completed.stdout.strip()
            elif tool_name == "npm":
                completed = subprocess.run(
                    [tool_name, "--version"],
                    capture_output=True,
                    text=True,
                    timeout=5
                )
                result["version"] = completed.stdout.strip()
            elif tool_name == "uv":
                completed = subprocess.run(
                    [tool_name, "--version"],
                    capture_output=True,
                    text=True,
                    timeout=5
                )
                result["version"] = completed.stdout.strip()
            elif tool_name == "pip":
                completed = subprocess.run(
                    [tool_name, "--version"],
                    capture_output=True,
                    text=True,
                    timeout=5
                )
                result["version"] = completed.stdout.strip()
            elif tool_name == "docker":
                completed = subprocess.run(
                    [tool_name, "--version"],
                    capture_output=True,
                    text=True,
                    timeout=5
                )
                result["version"] = completed.stdout.strip()
            elif tool_name == "podman":
                completed = subprocess.run(
                    [tool_name, "--version"],
                    capture_output=True,
                    text=True,
                    timeout=5
                )
                result["version"] = completed.stdout.strip()
        except (subprocess.TimeoutExpired, FileNotFoundError, OSError):
            pass
    
    return result


def get_environment_fingerprint() -> dict[str, Any]:
    """Collect comprehensive environment fingerprint."""
    
    # Tools to check
    tools_to_check = [
        "python",
        "python3",
        "uv",
        "pip",
        "node",
        "npm",
        "docker",
        "podman",
    ]
    
    tool_versions = {tool: get_tool_version(tool) for tool in tools_to_check}
    
    # Environment variables (names only, never values)
    env_vars = list(os.environ.keys())
    
    # Disk space
    disk_info = {}
    try:
        disk_usage = shutil.disk_usage(Path.cwd())
        disk_info = {
            "total_gb": round(disk_usage.total / (1024**3), 2),
            "free_gb": round(disk_usage.free / (1024**3), 2),
            "used_gb": round(disk_usage.used / (1024**3), 2),
        }
    except OSError:
        pass
    
    return {
        "schema_version": SCHEMA_VERSION,
        "part_id": PART_ID,
        "generated_at": datetime.now(UTC).isoformat(),
        "repository": {
            "root": str(Path.cwd()).replace("\\", "/"),
        },
        "system": {
            "os": platform.system(),
            "os_version": platform.version(),
            "os_release": platform.release(),
            "architecture": platform.machine(),
            "processor": platform.processor(),
            "hostname": platform.node(),
        },
        "python": {
            "version": platform.python_version(),
            "implementation": platform.python_implementation(),
            "executable": sys.executable,
            "compiler": platform.python_compiler(),
        },
        "tools": tool_versions,
        "environment": {
            "timezone": os.environ.get("TZ", "unknown"),
            "locale": os.environ.get("LANG", "unknown"),
            "variable_count": len(env_vars),
            "variable_names": sorted(env_vars),
        },
        "resources": {
            "disk": disk_info,
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Phase 0 Book 2: Environment Fingerprinting"
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
    
    # Generate fingerprint
    fingerprint = get_environment_fingerprint()
    
    # Write artifact
    fingerprint_path = args.output_dir / "environment-fingerprint.json"
    with open(fingerprint_path, "w") as f:
        json.dump(fingerprint, f, indent=2)
    
    # Generate part evidence
    part_evidence = {
        "part_id": PART_ID,
        "schema_version": SCHEMA_VERSION,
        "generated_at": datetime.now(UTC).isoformat(),
        "status": "implemented_unverified",
        "artifacts": {
            "environment_fingerprint": str(fingerprint_path).replace("\\", "/"),
        },
    }
    
    evidence_path = args.output_dir / "part-02-env-evidence.json"
    with open(evidence_path, "w") as f:
        json.dump(part_evidence, f, indent=2)
    
    print(json.dumps(part_evidence, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())