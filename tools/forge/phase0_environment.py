#!/usr/bin/env python3
"""Phase 0 Book 2 Part 1: Environment fingerprint collection."""

import argparse
import json
import os
import platform
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


SCHEMA_VERSION = "0.1.0"
PART_ID = "PHASE-00-BOOK-02-PART-01"
DEFAULT_OUTPUT = Path("artifacts/forge/phase-00")


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _run_command(args: list[str]) -> tuple[int, str, str]:
    """Run a command and return exit code, stdout, stderr."""
    try:
        result = subprocess.run(
            args,
            capture_output=True,
            text=True,
            timeout=10,
        )
        return result.returncode, result.stdout.strip(), result.stderr.strip()
    except (subprocess.TimeoutExpired, FileNotFoundError):
        return -1, "", ""


def _get_version(command: str, version_flag: str = "--version") -> str | None:
    """Get version string from a command."""
    code, stdout, _ = _run_command([command, version_flag])
    if code == 0 and stdout:
        return stdout.splitlines()[0]
    return None


def collect_environment_fingerprint() -> dict[str, Any]:
    """Collect comprehensive environment fingerprint."""
    fingerprint = {
        "schema_version": SCHEMA_VERSION,
        "artifact_type": "EnvironmentFingerprint",
        "part_id": PART_ID,
        "generated_at": utc_now(),
        "environment": {
            "operating_system": platform.system(),
            "operating_system_release": platform.release(),
            "operating_system_version": platform.version(),
            "architecture": platform.machine(),
            "processor": platform.processor(),
            "hostname": platform.node(),
            "python": {
                "version": platform.python_version(),
                "version_info": list(platform.python_version_tuple()),
                "executable": sys.executable,
                "implementation": platform.python_implementation(),
            },
        },
        "tools": {},
        "platform_dependencies": {},
    }

    # Git
    git_version = _get_version("git", "--version")
    fingerprint["tools"]["git"] = {
        "available": git_version is not None,
        "version": git_version,
    }

    # Docker
    docker_version = _get_version("docker", "--version")
    fingerprint["tools"]["docker"] = {
        "available": docker_version is not None,
        "version": docker_version,
    }

    # Podman
    podman_version = _get_version("podman", "--version")
    fingerprint["tools"]["podman"] = {
        "available": podman_version is not None,
        "version": podman_version,
    }

    # pip
    pip_version = _get_version("pip", "--version")
    fingerprint["tools"]["pip"] = {
        "available": pip_version is not None,
        "version": pip_version,
    }

    # uv (if available)
    uv_version = _get_version("uv", "--version")
    fingerprint["tools"]["uv"] = {
        "available": uv_version is not None,
        "version": uv_version,
    }

    # Node/npm (if available)
    node_version = _get_version("node", "--version")
    npm_version = _get_version("npm", "--version")
    fingerprint["tools"]["node"] = {
        "available": node_version is not None,
        "version": node_version,
    }
    fingerprint["tools"]["npm"] = {
        "available": npm_version is not None,
        "version": npm_version,
    }

    # Rust (if available)
    rustc_version = _get_version("rustc", "--version")
    cargo_version = _get_version("cargo", "--version")
    fingerprint["tools"]["rustc"] = {
        "available": rustc_version is not None,
        "version": rustc_version,
    }
    fingerprint["tools"]["cargo"] = {
        "available": cargo_version is not None,
        "version": cargo_version,
    }

    # Platform-specific dependencies
    if platform.system() == "Windows":
        fingerprint["platform_dependencies"]["windows"] = {
            "mt5_available": False,  # Would need to check registry or path
            "ib_gateway_available": False,  # Would need to check for TWS
        }
    elif platform.system() == "Darwin":
        fingerprint["platform_dependencies"]["macos"] = {}
    elif platform.system() == "Linux":
        fingerprint["platform_dependencies"]["linux"] = {}

    # Disk space
    try:
        stat = os.statvfs(".")
        fingerprint["environment"]["disk"] = {
            "total_bytes": stat.f_frsize * stat.f_blocks,
            "available_bytes": stat.f_frsize * stat.f_bavail,
        }
    except (AttributeError, OSError):
        # Windows doesn't have statvfs
        try:
            import ctypes
            free_bytes = ctypes.c_ulonglong(0)
            total_bytes = ctypes.c_ulonglong(0)
            ctypes.windll.kernel32.GetDiskFreeSpaceExW(
                ctypes.c_wchar_p("."),
                ctypes.byref(free_bytes),
                ctypes.byref(total_bytes),
                None,
            )
            fingerprint["environment"]["disk"] = {
                "total_bytes": total_bytes.value,
                "available_bytes": free_bytes.value,
            }
        except (AttributeError, OSError):
            fingerprint["environment"]["disk"] = {"error": "unavailable"}

    # Memory
    try:
        import psutil
        mem = psutil.virtual_memory()
        fingerprint["environment"]["memory"] = {
            "total_bytes": mem.total,
            "available_bytes": mem.available,
        }
    except ImportError:
        fingerprint["environment"]["memory"] = {"error": "psutil not available"}

    # Environment variable names (never values)
    env_names = [
        "PATH",
        "PYTHONPATH",
        "VIRTUAL_ENV",
        "CONDA_PREFIX",
        "DOCKER_HOST",
        "OPENAI_API_KEY",
        "ANTHROPIC_API_KEY",
    ]
    fingerprint["environment"]["env_variables"] = [
        name for name in env_names if name in os.environ
    ]

    return fingerprint


def write_environment_fingerprint(
    repo_root: Path,
    output_dir: Path,
) -> Path:
    """Collect and write environment fingerprint."""
    root = repo_root.resolve()
    destination = output_dir.resolve()

    fingerprint = collect_environment_fingerprint()
    output_path = destination / "environment-fingerprint.json"

    output_path.parent.mkdir(parents=True, exist_ok=True)
    temporary = output_path.with_suffix(output_path.suffix + ".tmp")
    temporary.write_text(
        json.dumps(fingerprint, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    os.replace(temporary, output_path)

    return output_path


def build_argument_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Collect Phase 0 Book 2 Part 1 environment evidence.",
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
        help="Directory for environment fingerprint JSON artifact.",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_argument_parser().parse_args(list(argv) if argv is not None else None)
    root = args.root.resolve()
    output_dir = args.output_dir
    if not output_dir.is_absolute():
        output_dir = root / output_dir

    try:
        path = write_environment_fingerprint(root, output_dir)
    except Exception as exc:
        print(f"environment fingerprint failed: {exc}", file=sys.stderr)
        return 1

    result = {
        "part_id": PART_ID,
        "status": "implemented_unverified",
        "artifact": str(path.relative_to(root) if path.is_relative_to(root) else str(path)),
    }
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
