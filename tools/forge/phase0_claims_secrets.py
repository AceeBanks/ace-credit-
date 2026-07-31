#!/usr/bin/env python3
"""Phase 0 Book 1 Part 3: Claims, Contradictions, and Secret Redaction.

This module scans documentation for material claims, identifies contradictions,
and produces a redacted secret finding inventory. It intentionally uses only the
Python standard library.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

SCHEMA_VERSION = "0.1.0"
PART_ID = "PHASE-00-BOOK-01-PART-03"
DEFAULT_OUTPUT = Path("artifacts/forge/phase-00/book-01-part-03")

# Secret patterns to detect (redacted matches only)
SECRET_PATTERNS = [
    r"ghp_[a-zA-Z0-9]{36}",  # GitHub PAT
    r"github\.com/[^/]+/[^:]+:[^@]+@",  # GitHub remote with credentials
    r"access_token\s*=\s*[^\s]+",  # Access token patterns
    r"api[_-]?key\s*[:=]\s*[^\s]+",  # API key patterns
    r"secret[_-]?key\s*[:=]\s*[^\s]+",  # Secret key patterns
    r"password\s*[:=]\s*[^\s]+",  # Password patterns
    r"[a-zA-Z0-9]{32,}",  # Long hex strings (possible keys)
]

# Documentation patterns to scan
DOC_PATTERNS = [
    r"\.md$",
    r"\.rst$",
    r"\.txt$",
    r"README",
    r"CHANGELOG",
    r"CONTRIBUTING",
]

# Claim categories
CLAIM_CATEGORIES = [
    "architecture",
    "authority",
    "security",
    "performance",
    "status",
    "integration",
    "dependency",
]


def detect_secrets(content: str, filepath: Path) -> list[dict[str, Any]]:
    """Detect secret patterns in content, returning redacted matches only."""
    findings = []
    
    for pattern in SECRET_PATTERNS:
        matches = re.finditer(pattern, content, re.IGNORECASE)
        for match in matches:
            # Redact the actual match
            redacted = f"[REDACTED:{len(match.group())}chars]"
            findings.append({
                "pattern": pattern,
                "redacted_match": redacted,
                "line_number": content[:match.start()].count('\n') + 1,
                "column": match.start() - content.rfind('\n', 0, match.start()),
            })
    
    return findings


def extract_claims(content: str, filepath: Path) -> list[dict[str, Any]]:
    """Extract material claims from documentation content."""
    claims = []
    
    # Look for claim-like patterns (subject + assertion)
    claim_patterns = [
        r"(?:The system|This module|The application|We|I) (?:will|must|shall|should|can|is|are) [^.!?]+[.!?]",
        r"(?:supports|provides|implements|enables|requires) [^.!?]+[.!?]",
        r"(?:not|never|no) [^.!?]+[.!?]",
    ]
    
    for pattern in claim_patterns:
        matches = re.finditer(pattern, content, re.IGNORECASE)
        for match in matches:
            claims.append({
                "claim_text": match.group().strip(),
                "line_number": content[:match.start()].count('\n') + 1,
                "category": categorize_claim(match.group()),
            })
    
    return claims


def categorize_claim(claim_text: str) -> str:
    """Categorize a claim based on keywords."""
    claim_lower = claim_text.lower()
    
    for category in CLAIM_CATEGORIES:
        if category in claim_lower:
            return category
    
    return "general"


def scan_documentation(root: Path) -> list[dict[str, Any]]:
    """Scan documentation files for claims and secrets."""
    doc_files = []
    
    for filepath in root.rglob("*"):
        if not filepath.is_file():
            continue
        
        # Skip excluded directories
        if any(part in filepath.parts for part in [".git", "__pycache__", ".venv", "node_modules", ".windsurf", ".cursor", "artifacts"]):
            continue
        
        # Check if file matches documentation patterns
        filename = filepath.name
        if any(re.search(pattern, filename, re.IGNORECASE) for pattern in DOC_PATTERNS):
            try:
                content = filepath.read_text(encoding="utf-8", errors="ignore")
                rel_path = filepath.relative_to(root)
                
                claims = extract_claims(content, filepath)
                secrets = detect_secrets(content, filepath)
                
                if claims or secrets:
                    doc_files.append({
                        "path": str(rel_path).replace("\\", "/"),
                        "size_bytes": filepath.stat().st_size,
                        "claims": claims,
                        "secrets": secrets,
                        "claim_count": len(claims),
                        "secret_count": len(secrets),
                    })
            except (OSError, IOError):
                continue
    
    return sorted(doc_files, key=lambda x: x["path"])


def identify_contradictions(claims_data: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Identify potential contradictions in claims."""
    contradictions = []
    
    # Collect all claims
    all_claims = []
    for doc in claims_data:
        for claim in doc["claims"]:
            all_claims.append({
                "source": doc["path"],
                "claim": claim["claim_text"],
                "category": claim["category"],
                "line": claim["line_number"],
            })
    
    # Look for contradictory patterns
    contradiction_pairs = [
        (r"supports", r"does not support"),
        (r"enables", r"disables"),
        (r"requires", r"does not require"),
        (r"will", r"will not"),
        (r"can", r"cannot"),
        (r"is", r"is not"),
    ]
    
    for i, claim1 in enumerate(all_claims):
        for claim2 in all_claims[i+1:]:
            # Same category but different assertions
            if claim1["category"] == claim2["category"]:
                for pos_pattern, neg_pattern in contradiction_pairs:
                    if pos_pattern in claim1["claim"].lower() and neg_pattern in claim2["claim"].lower():
                        contradictions.append({
                            "contradiction_id": f"CONTR-{len(contradictions) + 1:03d}",
                            "claim_1": claim1,
                            "claim_2": claim2,
                            "pattern": f"{pos_pattern} vs {neg_pattern}",
                            "status": "unresolved",
                        })
    
    return contradictions


def generate_claims_inventory(root: Path) -> dict[str, Any]:
    """Generate claims and secrets inventory."""
    doc_files = scan_documentation(root)
    contradictions = identify_contradictions(doc_files)
    
    # Count by category
    category_counts = {}
    for doc in doc_files:
        for claim in doc["claims"]:
            category = claim["category"]
            category_counts[category] = category_counts.get(category, 0) + 1
    
    return {
        "schema_version": SCHEMA_VERSION,
        "part_id": PART_ID,
        "generated_at": datetime.now(UTC).isoformat(),
        "root_path": str(root).replace("\\", "/"),
        "total_documents": len(doc_files),
        "total_claims": sum(doc["claim_count"] for doc in doc_files),
        "total_secrets": sum(doc["secret_count"] for doc in doc_files),
        "category_counts": category_counts,
        "contradictions": contradictions,
        "documents": doc_files,
    }


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Phase 0 Book 1 Part 3: Claims, Secrets, and Contradictions"
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
    claims_inventory = generate_claims_inventory(args.root)
    
    # Write artifacts
    claims_path = args.output_dir / "claims-secrets-inventory.json"
    contradictions_path = args.output_dir / "contradictions-register.json"
    
    with open(claims_path, "w") as f:
        json.dump(claims_inventory, f, indent=2)
    
    with open(contradictions_path, "w") as f:
        json.dump({
            "schema_version": SCHEMA_VERSION,
            "part_id": PART_ID,
            "generated_at": datetime.now(UTC).isoformat(),
            "contradictions": claims_inventory["contradictions"],
        }, f, indent=2)
    
    # Generate part evidence
    part_evidence = {
        "part_id": PART_ID,
        "schema_version": SCHEMA_VERSION,
        "generated_at": datetime.now(UTC).isoformat(),
        "status": "implemented_unverified",
        "artifacts": {
            "claims_inventory": str(claims_path).replace("\\", "/"),
            "contradictions_register": str(contradictions_path).replace("\\", "/"),
        },
        "counts": {
            "documents": claims_inventory["total_documents"],
            "claims": claims_inventory["total_claims"],
            "secrets": claims_inventory["total_secrets"],
            "contradictions": len(claims_inventory["contradictions"]),
        },
    }
    
    evidence_path = args.output_dir / "part-03-evidence.json"
    with open(evidence_path, "w") as f:
        json.dump(part_evidence, f, indent=2)
    
    print(json.dumps(part_evidence, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())