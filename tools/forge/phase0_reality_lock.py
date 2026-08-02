#!/usr/bin/env python3
"""
Phase 0 Book 4: Reality Lock.

LEGACY/UNTRUSTED - P0-REPAIR-01
This tool is marked as legacy/untrusted until repaired per P0-REPAIR-01.
Do not use to approve Phase 0. Hardcodes Books 1-4 as "complete" and
sets ready_for_phase_1=true without proper evidence validation.
Must be repaired to fail-closed behavior.
"""

import argparse
import json
import os
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


SCHEMA_VERSION = "0.1.0"
PART_ID = "PHASE-00-BOOK-04"
DEFAULT_OUTPUT = Path("artifacts/forge/phase-00")


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def get_current_repo_sha(repo_root: Path) -> str:
    """Get current repository HEAD SHA."""
    try:
        result = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            cwd=repo_root,
            capture_output=True,
            text=True,
            timeout=10,
        )
        return result.stdout.strip() if result.returncode == 0 else "unknown"
    except Exception:
        return "unknown"


def load_artifact(repo_root: Path, artifact_name: str) -> dict[str, Any]:
    """Load an artifact JSON file."""
    artifact_path = repo_root / "artifacts" / "forge" / "phase-00" / artifact_name
    if not artifact_path.exists():
        return {"error": f"Artifact not found: {artifact_name}"}
    
    try:
        return json.loads(artifact_path.read_text(encoding="utf-8"))
    except Exception as e:
        return {"error": f"Failed to load {artifact_name}: {str(e)}"}


def generate_reality_lock(repo_root: Path) -> dict[str, Any]:
    """Generate comprehensive reality lock manifest."""
    
    current_sha = get_current_repo_sha(repo_root)
    
    # Load all Phase 0 artifacts
    repository_fingerprint = load_artifact(repo_root, "repository-fingerprint.json")
    core_component_inventory = load_artifact(repo_root, "core-component-inventory.json")
    environment_fingerprint = load_artifact(repo_root, "environment-fingerprint.json")
    test_discovery = load_artifact(repo_root, "test-discovery.json")
    test_collection = load_artifact(repo_root, "test-collection.json")
    test_execution = load_artifact(repo_root, "test-execution.json")
    service_readiness = load_artifact(repo_root, "service-readiness.json")
    backtest_reproduction = load_artifact(repo_root, "backtest-reproduction.json")
    claim_reconciliation = load_artifact(repo_root, "claim-reconciliation.json")
    baseline_report = load_artifact(repo_root, "baseline-report.json")
    component_classification = load_artifact(repo_root, "component-classification.json")
    
    # Build canonical path map
    canonical_paths = {}
    for component in core_component_inventory.get("components", []):
        component_id = component.get("component_id", "unknown")
        component_path = component.get("path", "")
        if component_path:
            canonical_paths[component_id] = {
                "canonical_path": component_path,
                "present": component.get("present", False),
                "operational_class": None,  # Will be filled from classification
            }
    
    # Merge classification into canonical paths
    for classification in component_classification.get("classifications", []):
        component_id = classification.get("component_id", "unknown")
        if component_id in canonical_paths:
            canonical_paths[component_id]["operational_class"] = classification.get("operational_class")
    
    # Build quarantine register
    quarantine_register = []
    for classification in component_classification.get("classifications", []):
        if classification.get("operational_class") == "quarantine":
            quarantine_register.append({
                "component_id": classification.get("component_id"),
                "component_path": classification.get("component_path"),
                "reason": classification.get("reasoning", ["Unknown"]),
            })
    
    # Validate evidence existence - fail closed if missing
    blocking_issues = []
    required_artifacts = {
        "repository_fingerprint": repository_fingerprint,
        "core_component_inventory": core_component_inventory,
        "environment_fingerprint": environment_fingerprint,
        "component_classification": component_classification,
    }
    
    for artifact_name, artifact_data in required_artifacts.items():
        if "error" in artifact_data:
            blocking_issues.append(f"Missing or invalid required artifact: {artifact_name}")
    
    # Check Book 1 completion (actual evidence, not hardcoded)
    book_1_complete = (
        "error" not in repository_fingerprint and
        "error" not in core_component_inventory and
        repository_fingerprint.get("generated_at") and
        core_component_inventory.get("components")
    )
    
    # Check Book 2 completion (actual evidence, not hardcoded)
    book_2_complete = (
        "error" not in environment_fingerprint and
        "error" not in test_discovery and
        "error" not in test_collection and
        "error" not in test_execution and
        "error" not in service_readiness and
        "error" not in backtest_reproduction
    )
    
    # Check Book 3 completion (actual evidence, not hardcoded)
    book_3_complete = (
        "error" not in component_classification and
        component_classification.get("classifications")
    )
    
    # Check Book 4 completion (this tool)
    book_4_complete = True  # This tool is running
    
    # Build decision register based on actual evidence
    decision_register = []
    
    if book_1_complete:
        decision_register.append({
            "decision_id": "DEC-001",
            "decision_type": "book_1_acceptance",
            "description": "Book 1 Inventory evidence validated",
            "rationale": "Required artifacts present and structurally valid",
            "made_by": "REALITY_LOCK_VALIDATION",
            "made_at": utc_now(),
        })
    else:
        blocking_issues.append("Book 1 Inventory incomplete: missing or invalid artifacts")
    
    if book_2_complete:
        decision_register.append({
            "decision_id": "DEC-002",
            "decision_type": "book_2_acceptance",
            "description": "Book 2 Baseline evidence validated",
            "rationale": "Required artifacts present and structurally valid",
            "made_by": "REALITY_LOCK_VALIDATION",
            "made_at": utc_now(),
        })
    else:
        blocking_issues.append("Book 2 Baseline incomplete: missing or invalid artifacts")
    
    if book_3_complete:
        decision_register.append({
            "decision_id": "DEC-003",
            "decision_type": "book_3_acceptance",
            "description": "Book 3 Classification evidence validated",
            "rationale": "Classification artifact present and structurally valid",
            "made_by": "REALITY_LOCK_VALIDATION",
            "made_at": utc_now(),
        })
    else:
        blocking_issues.append("Book 3 Classification incomplete: missing or invalid artifact")
    
    # Decision register for quarantine (always present if classification exists)
    if quarantine_register:
        decision_register.append({
            "decision_id": "DEC-004",
            "decision_type": "component_quarantine",
            "description": f"Quarantine {len(quarantine_register)} components",
            "rationale": "Components classified as quarantine per evidence-based rules",
            "made_by": "REALITY_LOCK_VALIDATION",
            "made_at": utc_now(),
        })
    
    return {
        "schema_version": SCHEMA_VERSION,
        "artifact_type": "RealityLock",
        "part_id": PART_ID,
        "generated_at": utc_now(),
        "repository_sha": current_sha,
        
        # Phase 0 completion status (evidence-based, not hardcoded)
        "phase_00_completion": {
            "book_1_inventory": "complete" if book_1_complete else "incomplete",
            "book_2_baseline": "complete" if book_2_complete else "incomplete",
            "book_3_classification": "complete" if book_3_complete else "incomplete",
            "book_4_lock": "complete" if book_4_complete else "incomplete",
        },
        
        # Canonical path map
        "canonical_path_map": canonical_paths,
        
        # Quarantine register
        "quarantine_register": quarantine_register,
        
        # Decision register
        "decision_register": decision_register,
        
        # Artifact references
        "artifacts": {
            "repository_fingerprint": "repository-fingerprint.json",
            "core_component_inventory": "core-component-inventory.json",
            "part_01_evidence": "part-01-evidence.json",
            "environment_fingerprint": "environment-fingerprint.json",
            "test_discovery": "test-discovery.json",
            "test_collection": "test-collection.json",
            "test_execution": "test-execution.json",
            "service_readiness": "service-readiness.json",
            "backtest_reproduction": "backtest-reproduction.json",
            "claim_reconciliation": "claim-reconciliation.json",
            "baseline_report": "baseline-report.json",
            "component_classification": "component-classification.json",
        },
        
        # Summary statistics
        "summary": {
            "total_components": len(canonical_paths),
            "quarantined_components": len(quarantine_register),
            "total_decisions": len(decision_register),
            "total_artifacts": 12,
            "baseline_status": baseline_report.get("baseline_status", "unknown"),
            "blockers_count": len(baseline_report.get("blockers", [])),
        },
        
        # Phase 1 inputs
        "phase_01_inputs": {
            "canonical_paths": canonical_paths,
            "quarantine_register": quarantine_register,
            "baseline_gaps": baseline_report.get("blockers", []),
            "environment_fingerprint": environment_fingerprint.get("environment", {}),
        },
        
        # Exit gate status (fail-closed)
        "exit_gate": {
            "ready_for_phase_1": (
                book_1_complete and
                book_2_complete and
                book_3_complete and
                book_4_complete and
                len(blocking_issues) == 0
            ),
            "blocking_issues": blocking_issues,
            "warnings": [
                "Backtest fixtures not available - must implement in Phase 3 or Phase 6",
                "Services not verified - must implement in Phase 2",
                "Classification requires evidence-based reimplementation per P0-REPAIR-01",
            ] if not blocking_issues else [],
        },
    }


def write_reality_lock(
    repo_root: Path,
    output_dir: Path,
) -> Path:
    """Generate and write reality lock manifest."""
    root = repo_root.resolve()
    destination = output_dir.resolve()

    lock = generate_reality_lock(root)
    output_path = destination / "reality-lock-manifest.json"

    output_path.parent.mkdir(parents=True, exist_ok=True)
    temporary = output_path.with_suffix(output_path.suffix + ".tmp")
    temporary.write_text(
        json.dumps(lock, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    os.replace(temporary, output_path)

    return output_path


def build_argument_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Generate Phase 0 Book 4 reality lock manifest.",
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
        help="Directory for reality lock JSON artifact.",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_argument_parser().parse_args(list(argv) if argv is not None else None)
    root = args.root.resolve()
    output_dir = args.output_dir
    if not output_dir.is_absolute():
        output_dir = root / output_dir

    try:
        path = write_reality_lock(root, output_dir)
    except Exception as exc:
        print(f"reality lock generation failed: {exc}", file=sys.stderr)
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
