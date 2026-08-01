#!/usr/bin/env python3
"""Phase 0 Book 2: Test Command Discovery.

This module discovers test commands from various sources in the repository.
It uses only the Python standard library and path introspection.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

SCHEMA_VERSION = "0.1.0"
PART_ID = "PHASE-00-BOOK-02-TEST-DISCOVERY"
DEFAULT_OUTPUT = Path("artifacts/forge/phase-00/book-02")


def discover_commands_from_pyproject(root: Path) -> list[dict[str, Any]]:
    """Discover commands from pyproject.toml."""
    commands = []
    pyproject = root / "pyproject.toml"
    
    if not pyproject.exists():
        return commands
    
    try:
        content = pyproject.read_text()
        
        # Extract pytest commands
        pytest_matches = re.findall(r'pytest\s*["\']([^"\']+)["\']', content)
        for match in pytest_matches:
            commands.append({
                "command_id": f"PYPROJECT-PYTEST-{len(commands)}",
                "command": f"pytest {match}",
                "source": "pyproject.toml",
                "owner": "general",
                "environment": "python",
                "destructive": False,
                "safe_to_run": True,
            })
        
        # Extract script commands
        script_matches = re.findall(r'["\']([^"\']+?)["\']\s*=\s*["\']([^"\']*pytest[^"\']*)["\']', content)
        for name, cmd in script_matches:
            commands.append({
                "command_id": f"PYPROJECT-SCRIPT-{len(commands)}",
                "command": cmd,
                "source": "pyproject.toml",
                "owner": "general",
                "environment": "python",
                "destructive": False,
                "safe_to_run": True,
            })
    except Exception:
        pass
    
    return commands


def discover_commands_from_pytest_ini(root: Path) -> list[dict[str, Any]]:
    """Discover commands from pytest.ini."""
    commands = []
    pytest_ini = root / "pytest.ini"
    
    if not pytest_ini.exists():
        return commands
    
    try:
        content = pytest_ini.read_text()
        
        # Extract addopts
        addopts_match = re.search(r'addopts\s*=\s*(.+)', content)
        if addopts_match:
            addopts = addopts_match.group(1).strip()
            commands.append({
                "command_id": f"PYTEST-INI-ADDOPTS-{len(commands)}",
                "command": f"pytest {addopts}",
                "source": "pytest.ini",
                "owner": "general",
                "environment": "python",
                "destructive": False,
                "safe_to_run": True,
            })
    except Exception:
        pass
    
    return commands


def discover_commands_from_ci(root: Path) -> list[dict[str, Any]]:
    """Discover commands from CI workflow files."""
    commands = []
    github_dir = root / ".github" / "workflows"
    
    if not github_dir.exists():
        return commands
    
    for workflow_file in github_dir.glob("*.yml"):
        try:
            content = workflow_file.read_text()
            
            # Extract pytest commands
            pytest_matches = re.findall(r'pytest\s*([^\s\n]+)', content)
            for match in pytest_matches:
                commands.append({
                    "command_id": f"CI-{workflow_file.stem}-PYTEST-{len(commands)}",
                    "command": f"pytest {match}",
                    "source": f".github/workflows/{workflow_file.name}",
                    "owner": "ci",
                    "environment": "python",
                    "destructive": False,
                    "safe_to_run": True,
                })
        except Exception:
            pass
    
    return commands


def discover_forge_test_commands(root: Path) -> list[dict[str, Any]]:
    """Discover Phase 0 Forge test commands."""
    commands = []
    forge_tests_dir = root / "tests" / "forge" / "phase_00"
    
    if not forge_tests_dir.exists():
        return commands
    
    # Add explicit Phase 0 test commands
    test_files = list(forge_tests_dir.glob("test_*.py"))
    for test_file in test_files:
        commands.append({
            "command_id": f"FORGE-PHASE00-{test_file.stem}",
            "command": f"python -m unittest tests.forge.phase_00.{test_file.stem}",
            "source": "forge/test_structure",
            "owner": "forge",
            "environment": "python",
            "destructive": False,
            "safe_to_run": True,
        })
    
    # Add aggregate command
    commands.append({
        "command_id": "FORGE-PHASE00-ALL",
        "command": "python -m unittest discover -s tests/forge/phase_00 -p 'test_*.py'",
        "source": "forge/test_structure",
        "owner": "forge",
        "environment": "python",
        "destructive": False,
        "safe_to_run": True,
    })
    
    return commands


def discover_commands(root: Path) -> dict[str, Any]:
    """Discover all test commands from repository."""
    all_commands = []
    
    # Discover from various sources
    all_commands.extend(discover_commands_from_pyproject(root))
    all_commands.extend(discover_commands_from_pytest_ini(root))
    all_commands.extend(discover_commands_from_ci(root))
    all_commands.extend(discover_forge_test_commands(root))
    
    # Deduplicate by command string
    seen = set()
    unique_commands = []
    for cmd in all_commands:
        cmd_str = cmd["command"]
        if cmd_str not in seen:
            seen.add(cmd_str)
            unique_commands.append(cmd)
    
    return {
        "schema_version": SCHEMA_VERSION,
        "part_id": PART_ID,
        "generated_at": datetime.now(UTC).isoformat(),
        "repository_root": str(root).replace("\\", "/"),
        "total_commands": len(unique_commands),
        "safe_commands": len([c for c in unique_commands if c["safe_to_run"]]),
        "destructive_commands": len([c for c in unique_commands if c["destructive"]]),
        "commands": unique_commands,
    }


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Phase 0 Book 2: Test Command Discovery"
    )
    parser.add_argument(
        "--root",
        type=Path,
        default=Path.cwd(),
        help="Repository root directory",
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
    
    # Discover commands
    discovery = discover_commands(args.root)
    
    # Write artifact
    discovery_path = args.output_dir / "test-discovery.json"
    with open(discovery_path, "w") as f:
        json.dump(discovery, f, indent=2)
    
    # Generate part evidence
    part_evidence = {
        "part_id": PART_ID,
        "schema_version": SCHEMA_VERSION,
        "generated_at": datetime.now(UTC).isoformat(),
        "status": "implemented_unverified",
        "artifacts": {
            "test_discovery": str(discovery_path).replace("\\", "/"),
        },
    }
    
    evidence_path = args.output_dir / "part-02-test-discovery-evidence.json"
    with open(evidence_path, "w") as f:
        json.dump(part_evidence, f, indent=2)
    
    print(json.dumps(part_evidence, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())