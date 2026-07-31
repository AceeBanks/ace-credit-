#!/usr/bin/env python3
"""Phase 0 Book 2 Part 2: Test command discovery."""

import argparse
import json
import os
import re
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


SCHEMA_VERSION = "0.1.0"
PART_ID = "PHASE-00-BOOK-02-PART-02"
DEFAULT_OUTPUT = Path("artifacts/forge/phase-00")


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def scan_pyproject_toml(repo_root: Path) -> list[dict[str, Any]]:
    """Scan pyproject.toml for test commands."""
    pyproject = repo_root / "pyproject.toml"
    if not pyproject.exists():
        return []
    
    commands = []
    try:
        content = pyproject.read_text(encoding="utf-8")
        
        # Look for pytest commands in tool.pytest section
        pytest_match = re.search(r'\[tool\.pytest\](.*?)\n\[', content, re.DOTALL)
        if pytest_match:
            pytest_section = pytest_match.group(1)
            if 'addopts' in pytest_section:
                addopts = re.search(r'addopts\s*=\s*["\']([^"\']+)["\']', pytest_section)
                if addopts:
                    commands.append({
                        "command_id": "pytest-addopts",
                        "owning_component": "root",
                        "source": "pyproject.toml",
                        "command": f"pytest {addopts.group(1)}",
                        "environment_requirements": ["python"],
                        "destructive_risk": False,
                        "expected_duration": "unknown",
                        "safe_to_run": True,
                    })
        
        # Look for test scripts in scripts section
        scripts_match = re.search(r'\[tool\.poetry\.scripts\](.*?)\n\[', content, re.DOTALL)
        if not scripts_match:
            scripts_match = re.search(r'\[project\.scripts\](.*?)\n\[', content, re.DOTALL)
        
        if scripts_match:
            scripts_section = scripts_match.group(1)
            for line in scripts_section.split('\n'):
                if '=' in line and 'test' in line.lower():
                    name, cmd = line.split('=', 1)
                    commands.append({
                        "command_id": f"script-{name.strip()}",
                        "owning_component": "root",
                        "source": "pyproject.toml",
                        "command": cmd.strip().strip('"\''),
                        "environment_requirements": ["python"],
                        "destructive_risk": False,
                        "expected_duration": "unknown",
                        "safe_to_run": True,
                    })
        
    except Exception as e:
        print(f"Warning: Failed to parse pyproject.toml: {e}", file=sys.stderr)
    
    return commands


def scan_pytest_ini(repo_root: Path) -> list[dict[str, Any]]:
    """Scan pytest.ini for test commands."""
    pytest_ini = repo_root / "pytest.ini"
    if not pytest_ini.exists():
        return []
    
    commands = []
    try:
        content = pytest_ini.read_text(encoding="utf-8")
        
        # Look for addopts
        addopts_match = re.search(r'addopts\s*=\s*(.+)', content)
        if addopts_match:
            commands.append({
                "command_id": "pytest-addopts",
                "owning_component": "root",
                "source": "pytest.ini",
                "command": f"pytest {addopts_match.group(1).strip()}",
                "environment_requirements": ["python"],
                "destructive_risk": False,
                "expected_duration": "unknown",
                "safe_to_run": True,
            })
        
    except Exception as e:
        print(f"Warning: Failed to parse pytest.ini: {e}", file=sys.stderr)
    
    return commands


def scan_ci_files(repo_root: Path) -> list[dict[str, Any]]:
    """Scan CI workflow files for test commands."""
    commands = []
    github_dir = repo_root / ".github" / "workflows"
    
    if not github_dir.exists():
        return commands
    
    for workflow_file in github_dir.glob("*.yml"):
        try:
            content = workflow_file.read_text(encoding="utf-8")
            
            # Look for pytest commands
            pytest_matches = re.findall(r'pytest[^\n]*', content)
            for match in pytest_matches:
                if 'run:' in content or 'script:' in content:
                    commands.append({
                        "command_id": f"ci-{workflow_file.stem}",
                        "owning_component": "ci",
                        "source": str(workflow_file.relative_to(repo_root)),
                        "command": match.strip(),
                        "environment_requirements": ["python", "github-actions"],
                        "destructive_risk": False,
                        "expected_duration": "unknown",
                        "safe_to_run": True,
                    })
            
        except Exception as e:
            print(f"Warning: Failed to parse {workflow_file}: {e}", file=sys.stderr)
    
    return commands


def scan_readme(repo_root: Path) -> list[dict[str, Any]]:
    """Scan README files for test commands."""
    commands = []
    readme = repo_root / "README.md"
    
    if not readme.exists():
        return commands
    
    try:
        content = readme.read_text(encoding="utf-8")
        
        # Look for common test command patterns
        patterns = [
            r'pytest[^\n]*',
            r'python -m pytest[^\n]*',
            r'test[^\n]*',
            r'coverage[^\n]*',
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, content)
            for match in matches:
                if '```' not in match:  # Skip code blocks for now
                    commands.append({
                        "command_id": f"readme-pattern-{len(commands)}",
                        "owning_component": "documentation",
                        "source": "README.md",
                        "command": match.strip(),
                        "environment_requirements": ["python"],
                        "destructive_risk": False,
                        "expected_duration": "unknown",
                        "safe_to_run": True,
                    })
        
    except Exception as e:
        print(f"Warning: Failed to parse README.md: {e}", file=sys.stderr)
    
    return commands


def discover_test_commands(repo_root: Path) -> dict[str, Any]:
    """Discover all test commands from configuration files."""
    all_commands = []
    
    all_commands.extend(scan_pyproject_toml(repo_root))
    all_commands.extend(scan_pytest_ini(repo_root))
    all_commands.extend(scan_ci_files(repo_root))
    all_commands.extend(scan_readme(repo_root))
    
    # Deduplicate by command_id
    seen_ids = set()
    unique_commands = []
    for cmd in all_commands:
        if cmd["command_id"] not in seen_ids:
            seen_ids.add(cmd["command_id"])
            unique_commands.append(cmd)
    
    return {
        "schema_version": SCHEMA_VERSION,
        "artifact_type": "TestCommandDiscovery",
        "part_id": PART_ID,
        "generated_at": utc_now(),
        "commands": unique_commands,
        "summary": {
            "total_commands": len(unique_commands),
            "safe_to_run": sum(1 for cmd in unique_commands if cmd["safe_to_run"]),
            "destructive_risk": sum(1 for cmd in unique_commands if cmd["destructive_risk"]),
        },
    }


def write_test_discovery(
    repo_root: Path,
    output_dir: Path,
) -> Path:
    """Collect and write test command discovery."""
    root = repo_root.resolve()
    destination = output_dir.resolve()

    discovery = discover_test_commands(root)
    output_path = destination / "test-discovery.json"

    output_path.parent.mkdir(parents=True, exist_ok=True)
    temporary = output_path.with_suffix(output_path.suffix + ".tmp")
    temporary.write_text(
        json.dumps(discovery, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    os.replace(temporary, output_path)

    return output_path


def build_argument_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Collect Phase 0 Book 2 Part 2 test command discovery.",
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
        help="Directory for test discovery JSON artifact.",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_argument_parser().parse_args(list(argv) if argv is not None else None)
    root = args.root.resolve()
    output_dir = args.output_dir
    if not output_dir.is_absolute():
        output_dir = root / output_dir

    try:
        path = write_test_discovery(root, output_dir)
    except Exception as exc:
        print(f"test discovery failed: {exc}", file=sys.stderr)
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
