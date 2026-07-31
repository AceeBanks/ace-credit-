#!/usr/bin/env python3
"""Phase 0 Book 2 Part 5: Service readiness verification."""

import argparse
import json
import os
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


SCHEMA_VERSION = "0.1.0"
PART_ID = "PHASE-00-BOOK-02-PART-05"
DEFAULT_OUTPUT = Path("artifacts/forge/phase-00")


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def check_service_readiness(repo_root: Path, service_id: str, service_path: str) -> dict[str, Any]:
    """Check if a service is ready to run."""
    service_dir = repo_root / service_path
    if not service_dir.exists():
        return {
            "service_id": service_id,
            "service_path": service_path,
            "status": "not_found",
            "process_starts": False,
            "port_listens": False,
            "readiness_endpoint": False,
            "required_model": False,
            "representative_operation": False,
            "clean_shutdown": False,
            "notes": "service directory does not exist",
        }
    
    # Check for service entrypoint files
    main_files = list(service_dir.glob("main.py")) + list(service_dir.glob("app.py")) + list(service_dir.glob("server.py"))
    if not main_files:
        return {
            "service_id": service_id,
            "service_path": service_path,
            "status": "no_entrypoint",
            "process_starts": False,
            "port_listens": False,
            "readiness_endpoint": False,
            "required_model": False,
            "representative_operation": False,
            "clean_shutdown": False,
            "notes": "no main.py, app.py, or server.py found",
        }
    
    # For Phase 0 baseline, we document the service exists but don't actually start it
    # Starting services would require dependencies and configuration
    return {
        "service_id": service_id,
        "service_path": service_path,
        "status": "documented_not_tested",
        "process_starts": None,
        "port_listens": None,
        "readiness_endpoint": None,
        "required_model": None,
        "representative_operation": None,
        "clean_shutdown": None,
        "notes": "service documented but not started in Phase 0 baseline",
        "entrypoint_files": [str(f.relative_to(repo_root)) for f in main_files],
    }


def check_all_services(repo_root: Path) -> dict[str, Any]:
    """Check readiness of all claimed services."""
    services = []
    
    # Define services based on component structure
    service_configs = [
        ("OCE-BACKEND", "oce/backend"),
        ("OCE-FRONTEND", "oce/frontend"),
        ("SRRA-OPH-SERVER", "srrs_opc"),
        ("TRADING-ADAPTER", "projects/trading/mt5-mcp"),
    ]
    
    for service_id, service_path in service_configs:
        service_result = check_service_readiness(repo_root, service_id, service_path)
        services.append(service_result)
    
    return {
        "schema_version": SCHEMA_VERSION,
        "artifact_type": "ServiceReadiness",
        "part_id": PART_ID,
        "generated_at": utc_now(),
        "services": services,
        "summary": {
            "total_services": len(services),
            "ready": sum(1 for s in services if s["status"] == "ready"),
            "not_found": sum(1 for s in services if s["status"] == "not_found"),
            "documented_not_tested": sum(1 for s in services if s["status"] == "documented_not_tested"),
        },
    }


def write_service_readiness(
    repo_root: Path,
    output_dir: Path,
) -> Path:
    """Check services and write readiness report."""
    root = repo_root.resolve()
    destination = output_dir.resolve()

    readiness = check_all_services(root)
    output_path = destination / "service-readiness.json"

    output_path.parent.mkdir(parents=True, exist_ok=True)
    temporary = output_path.with_suffix(output_path.suffix + ".tmp")
    temporary.write_text(
        json.dumps(readiness, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    os.replace(temporary, output_path)

    return output_path


def build_argument_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Collect Phase 0 Book 2 Part 5 service readiness verification.",
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
        help="Directory for service readiness JSON artifact.",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_argument_parser().parse_args(list(argv) if argv is not None else None)
    root = args.root.resolve()
    output_dir = args.output_dir
    if not output_dir.is_absolute():
        output_dir = root / output_dir

    try:
        path = write_service_readiness(root, output_dir)
    except Exception as exc:
        print(f"service readiness check failed: {exc}", file=sys.stderr)
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
