#!/usr/bin/env python3
"""G0-B6-C6-C8 — validate_authn_credentials.

Validates the authn/session, service identity and credential vault policy
configs. Exit 0 when valid.
"""
from __future__ import annotations

import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[2]
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from tools.g0._common import load_yaml  # noqa: E402

AUTH_RULES = ("AUTH-001", "AUTH-002", "AUTH-003", "AUTH-004", "AUTH-005")
SVC_RULES = ("SVC-001", "SVC-002", "SVC-003", "SVC-004", "SVC-005", "SVC-006")
VAULT_RULES = ("VAULT-001", "VAULT-002", "VAULT-003", "VAULT-004",
               "VAULT-005", "VAULT-006", "VAULT-007")


def validate(errors: list[str] | None = None,
            authn: dict | None = None, svc: dict | None = None,
            vault: dict | None = None) -> tuple[bool, dict]:
    errors = [] if errors is None else errors
    ok = True
    authn = authn if authn is not None else load_yaml(
        _ROOT / "config/g0/security/authn_session_policy.yaml")
    svc = svc if svc is not None else load_yaml(
        _ROOT / "config/g0/security/service_identity_policy.yaml")
    vault = vault if vault is not None else load_yaml(
        _ROOT / "config/g0/security/credential_vault_policy.yaml")

    for rules, label in ((AUTH_RULES, "authn"), (SVC_RULES, "svc"),
                         (VAULT_RULES, "vault")):
        cfg_rules = {r.get("id") for r in (authn if label == "authn"
                     else svc if label == "svc" else vault).get("rules", [])}
        for rid in rules:
            if rid not in cfg_rules:
                errors.append(f"{label} policy missing rule {rid}")
                ok = False

    if len(svc.get("service_identities", [])) < 6:
        errors.append("service identity policy must define at least 6 services")
        ok = False
    if not svc.get("no_shared_omnipotent_secret"):
        errors.append("no-shared-omnipotent-secret must be true (SVC-001)")
        ok = False
    if len(vault.get("secret_classes", [])) != 8:
        errors.append("credential vault must define 8 secret classes")
        ok = False
    return ok, {"authn_rules": len(authn.get("rules", [])),
                "services": len(svc.get("service_identities", [])),
                "secret_classes": len(vault.get("secret_classes", []))}


def main() -> int:
    errs: list[str] = []
    ok, details = validate(errs)
    if not ok:
        print("AUTHN/CREDENTIAL POLICY INVALID")
        for e in errs:
            print(f"  - {e}")
        return 1
    print(f"authn/credential policy OK: {details}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
