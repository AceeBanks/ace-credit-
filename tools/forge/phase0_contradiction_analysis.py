#!/usr/bin/env python3
"""Phase 0 Book 1 Part 3: Contradiction Analysis.

This module deduplicates, groups, and severity-ranks contradictions
from the claims-secrets inventory. It uses only the Python standard library.
"""

from __future__ import annotations

import argparse
import json
import sys
from collections import defaultdict
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

SCHEMA_VERSION = "0.1.0"
PART_ID = "PHASE-00-BOOK-01-PART-03-ANALYSIS"
DEFAULT_OUTPUT = Path("artifacts/forge/phase-00/book-01-part-03")


def load_contradictions(register_path: Path) -> list[dict[str, Any]]:
    """Load contradictions from register."""
    with open(register_path, "r") as f:
        data = json.load(f)
        return data.get("contradictions", [])


def deduplicate_contradictions(contradictions: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Deduplicate contradictions by pattern and claim pair."""
    seen = set()
    deduplicated = []
    
    for contradiction in contradictions:
        # Create a signature for deduplication
        claim1_text = contradiction.get("claim_1", {}).get("claim", "")
        claim2_text = contradiction.get("claim_2", {}).get("claim", "")
        pattern = contradiction.get("pattern", "")
        
        signature = f"{pattern}:{claim1_text[:50]}:{claim2_text[:50]}"
        
        if signature not in seen:
            seen.add(signature)
            deduplicated.append(contradiction)
    
    return deduplicated


def group_by_category(contradictions: list[dict[str, Any]]) -> dict[str, list[dict[str, Any]]]:
    """Group contradictions by category."""
    groups = defaultdict(list)
    
    for contradiction in contradictions:
        category = contradiction.get("claim_1", {}).get("category", "general")
        groups[category].append(contradiction)
    
    return dict(groups)


def group_by_pattern(contradictions: list[dict[str, Any]]) -> dict[str, list[dict[str, Any]]]:
    """Group contradictions by pattern."""
    groups = defaultdict(list)
    
    for contradiction in contradictions:
        pattern = contradiction.get("pattern", "unknown")
        groups[pattern].append(contradiction)
    
    return dict(groups)


def group_by_source(contradictions: list[dict[str, Any]]) -> dict[str, list[dict[str, Any]]]:
    """Group contradictions by source document."""
    groups = defaultdict(list)
    
    for contradiction in contradictions:
        source = contradiction.get("claim_1", {}).get("source", "unknown")
        groups[source].append(contradiction)
    
    return dict(groups)


def severity_rank(contradictions: list[dict[str, Any]]) -> dict[str, list[dict[str, Any]]]:
    """Rank contradictions by severity."""
    severity = {
        "critical": [],
        "high": [],
        "medium": [],
        "low": [],
        "noise": [],
    }
    
    for contradiction in contradictions:
        pattern = contradiction.get("pattern", "")
        category = contradiction.get("claim_1", {}).get("category", "general")
        source = contradiction.get("claim_1", {}).get("source", "")
        
        # Severity logic - more conservative
        # Critical: authority, security, capital only
        if category in ["authority", "security", "capital"]:
            severity["critical"].append(contradiction)
        # High: architecture only (not generic is/is not or can/cannot)
        elif category == "architecture":
            severity["high"].append(contradiction)
        # Medium: performance, integration
        elif category in ["performance", "integration"]:
            severity["medium"].append(contradiction)
        # Low: status, dependency
        elif category in ["status", "dependency"]:
            severity["low"].append(contradiction)
        # Noise: general category, generic patterns, documentation contradictions
        elif category == "general" or pattern in ["is vs is not", "can vs cannot", "will vs will not"]:
            severity["noise"].append(contradiction)
        else:
            severity["noise"].append(contradiction)
    
    return severity


def analyze_contradictions(register_path: Path) -> dict[str, Any]:
    """Perform complete contradiction analysis."""
    contradictions = load_contradictions(register_path)
    
    # Deduplicate
    deduplicated = deduplicate_contradictions(contradictions)
    
    # Group
    by_category = group_by_category(deduplicated)
    by_pattern = group_by_pattern(deduplicated)
    by_source = group_by_source(deduplicated)
    
    # Severity rank
    severity = severity_rank(deduplicated)
    
    return {
        "schema_version": SCHEMA_VERSION,
        "part_id": PART_ID,
        "generated_at": datetime.now(UTC).isoformat(),
        "register_path": str(register_path).replace("\\", "/"),
        "raw_count": len(contradictions),
        "deduplicated_count": len(deduplicated),
        "deduplication_rate": f"{(1 - len(deduplicated) / len(contradictions)) * 100:.1f}%",
        "by_category": {k: len(v) for k, v in by_category.items()},
        "by_pattern": {k: len(v) for k, v in by_pattern.items()},
        "by_source": {k: len(v) for k, v in by_source.items()},
        "severity": {k: len(v) for k, v in severity.items()},
        "critical_count": len(severity["critical"]),
        "high_count": len(severity["high"]),
        "medium_count": len(severity["medium"]),
        "low_count": len(severity["low"]),
        "noise_count": len(severity["noise"]),
        "material_for_mad": len(severity["critical"]) + len(severity["high"]),
    }


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Phase 0 Book 1 Part 3: Contradiction Analysis"
    )
    parser.add_argument(
        "--register",
        type=Path,
        default=Path("artifacts/forge/phase-00/book-01-part-03/contradictions-register.json"),
        help="Contradictions register path",
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
    
    # Analyze contradictions
    analysis = analyze_contradictions(args.register)
    
    # Write analysis
    analysis_path = args.output_dir / "contradiction-analysis.json"
    with open(analysis_path, "w") as f:
        json.dump(analysis, f, indent=2)
    
    print(json.dumps(analysis, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())