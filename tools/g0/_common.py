"""Shared fail-closed helpers for G0 ratification/policy validators.

Every validator follows the same contract:
  validate(...) -> (ok: bool, report: dict)
and its CLI prints the JSON report and exits non-zero when not ok.
Missing files, malformed fields, or unknown enum values are hard failures
(fail closed), never warnings.
"""
from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

import yaml

REPO_ROOT = Path(__file__).resolve().parents[2]

RATIFICATION_CONFIG_DIR = Path("config/g0/ratification")
POLICY_CONFIG_DIR = Path("config/g0/policy")
DOMAIN_CONFIG_DIR = Path("config/g0/domain")


class ValidationFailure(Exception):
    """Raised when a fail-closed validation rule is violated."""


def load_yaml(rel_or_abs_path) -> dict:
    path = Path(rel_or_abs_path)
    if not path.is_absolute():
        path = REPO_ROOT / path
    if not path.exists():
        raise ValidationFailure(f"required file missing: {path}")
    try:
        data = yaml.safe_load(path.read_text(encoding="utf-8"))
    except yaml.YAMLError as exc:
        raise ValidationFailure(f"malformed YAML in {path}: {exc}") from exc
    if not isinstance(data, (dict, list)):
        raise ValidationFailure(f"{path} does not parse to a structured document")
    return data


def blob_sha(path) -> str:
    """Git-style blob SHA-1 of a file's content, normalized for line endings.

    CRLF/LF must not create phantom authority drift across checkouts with
    different autocrlf settings, so newlines are canonicalized before hashing.
    """
    p = Path(path)
    if not p.is_absolute():
        p = REPO_ROOT / p
    data = p.read_bytes().replace(b"\r\n", b"\n")
    return hashlib.sha1(b"blob %d\x00" % len(data) + data).hexdigest()


def require(cond: bool, errors: list, message: str) -> None:
    """Record a failure when cond does not hold. Never raises by itself."""
    if not cond:
        errors.append(message)


def require_field(obj: dict, field: str, errors: list, context: str) -> None:
    value = obj.get(field)
    if value is None or (isinstance(value, str) and not value.strip()):
        errors.append(f"{context}: missing or empty required field '{field}'")


def finish(name: str, ok: bool, checks: dict) -> tuple[bool, dict]:
    report = {"validator": name, "status": "PASS" if ok else "FAIL", **checks}
    return ok, report


def emit(report: dict) -> int:
    print(json.dumps(report, indent=2))
    return 0 if report.get("status") == "PASS" else 1


def cli_main(validate_fn, default_config: Path) -> int:
    config = Path(sys.argv[1]) if len(sys.argv) > 1 else default_config
    try:
        ok, report = validate_fn(config)
    except ValidationFailure as exc:
        ok, report = False, {"validator": default_config.stem, "status": "FAIL",
                             "errors": [str(exc)]}
    return emit(report)
