#!/usr/bin/env python3
"""Phase 0 Book 1 Part 2: Trading Census, Dependencies, and Data Metadata.

This module extends Part 1 with an observable-form census of trading files,
dependency manifests, native/runtime requirements, and bounded metadata for
data and result files. It intentionally uses only the Python standard library.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import sys
from collections import Counter
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

SCHEMA_VERSION = "0.1.0"
PART_ID = "PHASE-00-BOOK-01-PART-02"
DEFAULT_OUTPUT = Path("artifacts/forge/phase-00/book-01-part-02")
MAX_FILE_READ_BYTES = 10 * 1024 * 1024
TRADING_PATTERNS = [
    r"\.py$",
    r"\.ipynb$",
    r"\.csv$",
    r"\.parquet$",
    r"\.json$",
    r"\.yaml$",
    r"\.yml$",
    r"\.toml$",
    r"\.txt$",
]

DEPENDENCY_MANIFESTS = [
    "requirements.txt",
    "pyproject.toml",
    "setup.py",
    "setup.cfg",
    "Pipfile",
    "poetry.lock",
    "uv.lock",
    "environment.yml",
    "conda.yml",
]

DATA_PATTERNS = [
    r"\.csv$",
    r"\.parquet$",
    r"\.feather$",
    r"\.h5$",
    r"\.hdf5$",
    r"\.pkl$",
    r"\.pickle$",
    r"\.npy$",
    r"\.npz$",
]


def compute_file_hash(filepath: Path, max_bytes: int = MAX_FILE_READ_BYTES) -> str:
    """Compute SHA-256 hash of file contents, bounded by max_bytes."""
    sha256 = hashlib.sha256()
    try:
        # Skip hashing for very large files to improve performance
        file_size = filepath.stat().st_size
        if file_size > 100 * 1024 * 1024:  # Skip files > 100MB
            return "skipped_large_file"
        
        with open(filepath, "rb") as f:
            data = f.read(max_bytes)
            sha256.update(data)
    except (OSError, IOError):
        return "hash_error"
    return sha256.hexdigest()


def scan_trading_files(root: Path) -> list[dict[str, Any]]:
    """Scan for trading-related files across the repository."""
    trading_files = []
    processed = 0
    
    # Limit scan to relevant directories for performance
    relevant_dirs = ["forge", "srrs_opc", "nautilus", "agent-lab", "oce", "tools"]
    
    for filepath in root.rglob("*"):
        if not filepath.is_file():
            continue
        
        # Skip excluded directories
        if any(part in filepath.parts for part in [".git", "__pycache__", ".venv", "node_modules", ".windsurf", ".cursor"]):
            continue
        
        # Only scan relevant directories
        if not any(part in filepath.parts for part in relevant_dirs):
            continue
        
        processed += 1
        if processed % 1000 == 0:
            print(f"Processed {processed} files...", file=sys.stderr)
        
        # Check if file matches trading patterns
        filename = filepath.name
        if any(re.search(pattern, filename, re.IGNORECASE) for pattern in TRADING_PATTERNS):
            rel_path = filepath.relative_to(root)
            trading_files.append({
                "path": str(rel_path).replace("\\", "/"),
                "size_bytes": filepath.stat().st_size,
                "hash": compute_file_hash(filepath),
                "component": "unknown",
                "tracked": True,  # Simplified - all files in our scan are tracked
            })
    
    print(f"Total files processed: {processed}", file=sys.stderr)
    return sorted(trading_files, key=lambda x: x["path"])


def scan_dependency_manifests(root: Path) -> list[dict[str, Any]]:
    """Scan for dependency manifest files."""
    manifests = []
    
    # Limit scan to relevant directories for performance
    relevant_dirs = ["forge", "srrs_opc", "nautilus", "agent-lab", "oce", "tools", ""]
    
    for manifest_name in DEPENDENCY_MANIFESTS:
        for filepath in root.rglob(manifest_name):
            if not filepath.is_file():
                continue
            
            # Skip excluded directories
            if any(part in filepath.parts for part in [".git", "__pycache__", ".venv", "node_modules", ".windsurf", ".cursor"]):
                continue
            
            # Only scan relevant directories
            if not any(part in filepath.parts for part in relevant_dirs):
                continue
            
            rel_path = filepath.relative_to(root)
            manifests.append({
                "path": str(rel_path).replace("\\", "/"),
                "name": manifest_name,
                "size_bytes": filepath.stat().st_size,
                "hash": compute_file_hash(filepath),
                "component": "unknown",
            })
    
    return sorted(manifests, key=lambda x: x["path"])


def scan_data_files(root: Path) -> list[dict[str, Any]]:
    """Scan for data files with bounded metadata."""
    data_files = []
    
    # Limit scan to relevant directories for performance
    relevant_dirs = ["forge", "srrs_opc", "nautilus", "agent-lab", "oce", "tools"]
    
    for filepath in root.rglob("*"):
        if not filepath.is_file():
            continue
        
        # Skip excluded directories
        if any(part in filepath.parts for part in [".git", "__pycache__", ".venv", "node_modules", ".windsurf", ".cursor"]):
            continue
        
        # Only scan relevant directories
        if not any(part in filepath.parts for part in relevant_dirs):
            continue
        
        # Check if file matches data patterns
        filename = filepath.name
        if any(re.search(pattern, filename, re.IGNORECASE) for pattern in DATA_PATTERNS):
            rel_path = filepath.relative_to(root)
            data_files.append({
                "path": str(rel_path).replace("\\", "/"),
                "size_bytes": filepath.stat().st_size,
                "hash": compute_file_hash(filepath),
                "symbol": "unknown",
                "timeframe": "unknown",
                "timezone": "unknown",
                "adjustment": "unknown",
                "provenance": "unknown",
                "reproduction_state": "unknown",
            })
    
    return sorted(data_files, key=lambda x: x["path"])


def generate_trading_census(root: Path) -> dict[str, Any]:
    """Generate trading file census."""
    trading_files = scan_trading_files(root)
    
    # Count by component (placeholder - will be assigned in Book 3)
    component_counts = Counter(f["component"] for f in trading_files)
    
    return {
        "schema_version": SCHEMA_VERSION,
        "part_id": PART_ID,
        "generated_at": datetime.now(UTC).isoformat(),
        "root_path": str(root).replace("\\", "/"),
        "total_files": len(trading_files),
        "component_counts": dict(component_counts),
        "files": trading_files,
    }


def generate_dependency_inventory(root: Path) -> dict[str, Any]:
    """Generate dependency inventory."""
    manifests = scan_dependency_manifests(root)
    
    return {
        "schema_version": SCHEMA_VERSION,
        "part_id": PART_ID,
        "generated_at": datetime.now(UTC).isoformat(),
        "root_path": str(root).replace("\\", "/"),
        "total_manifests": len(manifests),
        "manifests": manifests,
    }


def generate_data_inventory(root: Path) -> dict[str, Any]:
    """Generate data inventory."""
    data_files = scan_data_files(root)
    
    return {
        "schema_version": SCHEMA_VERSION,
        "part_id": PART_ID,
        "generated_at": datetime.now(UTC).isoformat(),
        "root_path": str(root).replace("\\", "/"),
        "total_files": len(data_files),
        "files": data_files,
    }


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Phase 0 Book 1 Part 2: Trading Census, Dependencies, and Data Metadata"
    )
    parser.add_argument(
        "--root",
        type=Path,
        default=Path.cwd(),
        help="Repository root path (default: current directory)",
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
    
    # Generate artifacts
    trading_census = generate_trading_census(args.root)
    dependency_inventory = generate_dependency_inventory(args.root)
    data_inventory = generate_data_inventory(args.root)
    
    # Write artifacts
    trading_census_path = args.output_dir / "trading-file-census.json"
    dependency_inventory_path = args.output_dir / "dependency-inventory.json"
    data_inventory_path = args.output_dir / "data-inventory.json"
    
    with open(trading_census_path, "w") as f:
        json.dump(trading_census, f, indent=2)
    
    with open(dependency_inventory_path, "w") as f:
        json.dump(dependency_inventory, f, indent=2)
    
    with open(data_inventory_path, "w") as f:
        json.dump(data_inventory, f, indent=2)
    
    # Generate part evidence
    part_evidence = {
        "part_id": PART_ID,
        "schema_version": SCHEMA_VERSION,
        "generated_at": datetime.now(UTC).isoformat(),
        "status": "implemented_unverified",
        "artifacts": {
            "trading_census": str(trading_census_path).replace("\\", "/"),
            "dependency_inventory": str(dependency_inventory_path).replace("\\", "/"),
            "data_inventory": str(data_inventory_path).replace("\\", "/"),
        },
        "counts": {
            "trading_files": trading_census["total_files"],
            "dependency_manifests": dependency_inventory["total_manifests"],
            "data_files": data_inventory["total_files"],
        },
    }
    
    part_evidence_path = args.output_dir / "part-02-evidence.json"
    with open(part_evidence_path, "w") as f:
        json.dump(part_evidence, f, indent=2)
    
    print(json.dumps({
        "part_id": PART_ID,
        "status": "implemented_unverified",
        "artifacts": {
            "trading_census": str(trading_census_path).replace("\\", "/"),
            "dependency_inventory": str(dependency_inventory_path).replace("\\", "/"),
            "data_inventory": str(data_inventory_path).replace("\\", "/"),
            "part_evidence": str(part_evidence_path).replace("\\", "/"),
        },
    }, indent=2))
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
