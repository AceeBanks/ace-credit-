#!/usr/bin/env python3
"""Phase 0 Book 3: Component classification."""

import argparse
import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


SCHEMA_VERSION = "0.1.0"
PART_ID = "PHASE-00-BOOK-03"
DEFAULT_OUTPUT = Path("artifacts/forge/phase-00")


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def load_component_inventory(repo_root: Path) -> dict[str, Any]:
    """Load component inventory from Book 1."""
    inventory_path = repo_root / "artifacts" / "forge" / "phase-00" / "core-component-inventory.json"
    if not inventory_path.exists():
        return {"components": []}
    
    try:
        return json.loads(inventory_path.read_text(encoding="utf-8"))
    except Exception as e:
        print(f"Warning: Failed to load component inventory: {e}", file=sys.stderr)
        return {"components": []}


def classify_component(component_id: str, component_path: str, declared_purpose: str, repo_root: Path) -> dict[str, Any]:
    """Classify a single component based on its purpose and content."""
    component_dir = repo_root / component_path
    has_content = component_dir.exists() and any(component_dir.iterdir())
    
    # Classification rules based on component ID and declared purpose
    classification = {
        "component_id": component_id,
        "component_path": component_path,
        "declared_purpose": declared_purpose,
        "has_content": has_content,
        "operational_class": None,
        "confidence": "low",
        "reasoning": [],
    }
    
    # OCE components
    if "OCE" in component_id.upper():
        if "BACKEND" in component_id.upper():
            classification["operational_class"] = "service"
            classification["confidence"] = "high"
            classification["reasoning"].append("OCE backend is a service component")
        elif "FRONTEND" in component_id.upper():
            classification["operational_class"] = "service"
            classification["confidence"] = "high"
            classification["reasoning"].append("OCE frontend is a service component")
        else:
            classification["operational_class"] = "unknown"
            classification["reasoning"].append("OCE component type unclear")
    
    # SRRA-OPH components
    elif "SRRA" in component_id.upper() or "OPH" in component_id.upper():
        classification["operational_class"] = "agent"
        classification["confidence"] = "medium"
        classification["reasoning"].append("SRRA-OPH appears to be agent-related")
    
    # Trading components
    elif "TRADING" in component_id.upper():
        if "BACKTEST" in component_id.upper():
            classification["operational_class"] = "engine"
            classification["confidence"] = "high"
            classification["reasoning"].append("Trading backtests suggest engine component")
        elif "STRATEGY" in component_id.upper():
            classification["operational_class"] = "strategy"
            classification["confidence"] = "high"
            classification["reasoning"].append("Trading strategies are strategy components")
        elif "ADAPTER" in component_id.upper() or "MT5" in component_id.upper():
            classification["operational_class"] = "adapter"
            classification["confidence"] = "high"
            classification["reasoning"].append("Trading adapters are adapter components")
        else:
            classification["operational_class"] = "unknown"
            classification["reasoning"].append("Trading component type unclear")
    
    # Data components
    elif "DATA" in component_id.upper():
        classification["operational_class"] = "data"
        classification["confidence"] = "high"
        classification["reasoning"].append("Data components are data pipeline")
    
    # Default classification
    else:
        classification["operational_class"] = "unknown"
        classification["reasoning"].append("Unable to classify from component ID")
    
    # Override if component is empty (cleaned for FORGE build)
    if not has_content:
        classification["operational_class"] = "quarantine"
        classification["confidence"] = "high"
        classification["reasoning"].append("Component is empty - quarantined until FORGE implementation")
    
    return classification


def classify_all_components(repo_root: Path) -> dict[str, Any]:
    """Classify all components from inventory."""
    inventory = load_component_inventory(repo_root)
    
    classifications = []
    contradictions = []
    
    for component in inventory.get("components", []):
        component_id = component.get("component_id", "unknown")
        component_path = component.get("path", "")
        declared_purpose = component.get("declared_purpose", "")
        
        classification = classify_component(component_id, component_path, declared_purpose, repo_root)
        classifications.append(classification)
        
        # Check for potential contradictions
        if classification["confidence"] == "low" and classification["operational_class"] != "quarantine":
            contradictions.append({
                "component_id": component_id,
                "contradiction": f"Low confidence classification: {classification['operational_class']}",
                "resolution": "Manual review required during FORGE implementation",
            })
    
    return {
        "schema_version": SCHEMA_VERSION,
        "artifact_type": "ComponentClassification",
        "part_id": PART_ID,
        "generated_at": utc_now(),
        "classifications": classifications,
        "contradictions": contradictions,
        "summary": {
            "total_components": len(classifications),
            "by_class": {
                "engine": sum(1 for c in classifications if c["operational_class"] == "engine"),
                "simulator": sum(1 for c in classifications if c["operational_class"] == "simulator"),
                "strategy": sum(1 for c in classifications if c["operational_class"] == "strategy"),
                "adapter": sum(1 for c in classifications if c["operational_class"] == "adapter"),
                "data": sum(1 for c in classifications if c["operational_class"] == "data"),
                "agent": sum(1 for c in classifications if c["operational_class"] == "agent"),
                "service": sum(1 for c in classifications if c["operational_class"] == "service"),
                "quarantine": sum(1 for c in classifications if c["operational_class"] == "quarantine"),
                "unknown": sum(1 for c in classifications if c["operational_class"] == "unknown"),
            },
            "total_contradictions": len(contradictions),
        },
    }


def write_classification(
    repo_root: Path,
    output_dir: Path,
) -> Path:
    """Classify components and write report."""
    root = repo_root.resolve()
    destination = output_dir.resolve()

    classification = classify_all_components(root)
    output_path = destination / "component-classification.json"

    output_path.parent.mkdir(parents=True, exist_ok=True)
    temporary = output_path.with_suffix(output_path.suffix + ".tmp")
    temporary.write_text(
        json.dumps(classification, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    os.replace(temporary, output_path)

    return output_path


def build_argument_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Generate Phase 0 Book 3 component classification.",
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
        help="Directory for classification JSON artifact.",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_argument_parser().parse_args(list(argv) if argv is not None else None)
    root = args.root.resolve()
    output_dir = args.output_dir
    if not output_dir.is_absolute():
        output_dir = root / output_dir

    try:
        path = write_classification(root, output_dir)
    except Exception as exc:
        print(f"component classification failed: {exc}", file=sys.stderr)
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
