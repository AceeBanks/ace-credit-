"""B2.C22 — Book 2 Reality Lock builder.

Readiness is COMPUTED from repository evidence — never asserted:

    ready_for_book3 =
        glossary_complete
        AND entity_boundaries_ratified
        AND root_entities_with_stable_identity == 1.0
        AND external_ids_namespaced
        AND relationship_catalog_complete
        AND state_machine_tests_pass
        AND revision_replay_tests_pass
        AND fact_claim_evidence_tests_pass
        AND eligibility_determinism_contract_pass
        AND application_document_model_pass
        AND common_grants_exact_roundtrip_pass
        AND common_grants_loss_reporting_pass
        AND client_phase1_domain_coverage == 1.0
        AND georgia_federal_fixture_tests_pass
        AND d0_draft_context_ready
        AND adversarial_p0_pass
        AND p0_open == 0

Usage:
    python tools/g0/build_book2_reality_lock.py [--no-tests] [--out PATH]

`--no-tests` skips the pytest run (used by unit tests that inject fixtures);
the emitted lock then reports adversarial_p0_pass as null rather than a claim.
"""
from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
from decimal import Decimal
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[2]
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from tools.g0._common import DOMAIN_CONFIG_DIR, RATIFICATION_CONFIG_DIR, load_yaml  # noqa: E402
from tools.g0.validate_domain import (  # noqa: E402
    validate_artifact_families,
    validate_budget_policy,
    validate_client_vision_matrix,
    validate_common_grants_mapping,
    validate_draft_context_policy,
    validate_eligibility_policy,
    validate_entity_types,
    validate_extension_namespace,
    validate_fact_semantics,
    validate_glossary,
    validate_identifier_namespaces,
    validate_outcome_policy,
    validate_relationships,
    validate_requirement_types,
    validate_revision_policy,
    validate_state_machines,
)

COMMITTED_LOCK_PATH = (
    _ROOT / "docs" / "grant-sector" / "g0" / "00-ratification"
    / "G0_B2_REALITY_LOCK.json"
)

CONFIG_NAMES = (
    "glossary.yaml", "entity_types.yaml", "identifier_namespaces.yaml",
    "relationship_types.yaml", "state_machines.yaml", "revision_policy.yaml",
    "fact_semantics.yaml", "eligibility_policy.yaml", "requirement_types.yaml",
    "budget_policy.yaml", "artifact_families.yaml", "extension_namespace.yaml",
    "client_vision_matrix.yaml", "draft_context_policy.yaml",
    "common_grants_mapping.yaml", "outcome_policy.yaml",
)

VALIDATORS = {
    "glossary": validate_glossary,
    "entity_types": validate_entity_types,
    "identifier_namespaces": validate_identifier_namespaces,
    "relationships": validate_relationships,
    "state_machines": validate_state_machines,
    "revision_policy": validate_revision_policy,
    "fact_semantics": validate_fact_semantics,
    "eligibility_policy": validate_eligibility_policy,
    "requirement_types": validate_requirement_types,
    "budget_policy": validate_budget_policy,
    "artifact_families": validate_artifact_families,
    "extension_namespace": validate_extension_namespace,
    "client_vision": validate_client_vision_matrix,
    "draft_context": validate_draft_context_policy,
    "common_grants": validate_common_grants_mapping,
    "outcome": validate_outcome_policy,
}


def _run_book2_tests() -> dict:
    # Recursion guard: the lock-freshness test itself invokes this builder; the
    # inner pytest run must skip it or we recurse forever.
    env = {**os.environ, "G0_SKIP_LOCK_FRESHNESS": "1"}
    proc = subprocess.run(
        [sys.executable, "-m", "pytest", "tests/g0/book2", "-q", "--tb=no"],
        cwd=_ROOT, capture_output=True, text=True, timeout=600, env=env,
    )
    tail = (proc.stdout or "").strip().splitlines()[-1:] or [""]
    match = re.search(r"(\d+) passed", tail[0])
    failed = re.search(r"(\d+) failed", tail[0])
    return {
        "exit_code": proc.returncode,
        "passed": int(match.group(1)) if match else 0,
        "failed": int(failed.group(1)) if failed else (1 if proc.returncode else 0),
        "summary": tail[0],
        "scope": "tests/g0/book2 excluding G0_B2_REALITY_LOCK.json freshness self-test",
    }


def _exact_roundtrips_pass(mapping: dict) -> bool:
    """EXACT CommonGrants rows round-trip with semantic equality (B2.C15)."""
    from prototype.g0.domain.common_grants import round_trip
    for ent in mapping.get("entities", []):
        internal: dict = {}
        for row in ent.get("rows", []):
            if row.get("mapping_class") != "EXACT":
                continue
            value = row.get("example")
            if row.get("transform") == "decimal_to_string":
                value = Decimal(str(value))
            internal[row["internal_field"]] = value
        if not internal:
            continue
        ok, _ = round_trip(internal, mapping, ent["entity"])
        if not ok:
            return False
    return True


def _loss_reporting_pass(mapping: dict) -> bool:
    """Every LOSSY row documents its loss explicitly (B2.C15)."""
    for ent in mapping.get("entities", []):
        for row in ent.get("rows", []):
            if row.get("mapping_class") == "LOSSY" and not (row.get("loss_notes") or ""):
                return False
    return True


def _fixtures_pass() -> bool:
    """Georgia/federal fixtures validate against the same core ontology (C17)."""
    from prototype.g0.domain.draft_context import validate_draft_context
    from prototype.g0.domain.fixtures import SCENARIOS
    from prototype.g0.domain.fixtures.draft_context import GA_DRAFT_BUNDLE
    if set(SCENARIOS) != {"GA-1", "FED-1", "AWARD-1", "COMMUNITY-1"}:
        return False
    return validate_draft_context(GA_DRAFT_BUNDLE) == []


def _draft_context_ready(policy_data: dict) -> bool:
    ok, _ = validate_draft_context_policy(policy_data)
    if not ok:
        return False
    from prototype.g0.domain.draft_context import validate_draft_context
    from prototype.g0.domain.fixtures.draft_context import GA_DRAFT_BUNDLE
    return validate_draft_context(GA_DRAFT_BUNDLE) == []


def compute_lock(configs: dict, test_results: dict | None = None) -> dict:
    """Compute the Reality Lock from loaded configs (+ optional pytest results).

    `configs` maps config-stem -> parsed document. `test_results` None means
    tests were not executed (reported as null and readiness is blocked).
    """
    def check(stem: str) -> bool:
        ok, _ = VALIDATORS[stem](configs[stem])
        return ok

    entity_types = configs["entity_types"]
    # relationship/namespace checks resolve endpoint types against the catalog
    from tools.g0.validate_domain import validate_identifier_namespaces as _vin
    from tools.g0.validate_domain import validate_relationships as _vr
    predicates_extra = {
        "external_ids_namespaced": _vin(configs["identifier_namespaces"],
                                         entity_types)[0],
        "relationship_catalog_complete": _vr(configs["relationships"],
                                              entity_types)[0],
    }
    # root entities with stable identity: every catalog entity carries a valid
    # identity prefix from the B2.C4 scheme
    from prototype.g0.domain.identity import validate_internal_id
    from prototype.g0.domain.extensions import core_identity_scheme
    scheme = core_identity_scheme(entity_types.get("entity_types", []))
    all_entities = entity_types.get("entity_types", [])
    with_prefix = [e for e in all_entities if e.get("identity_prefix")]
    root_identity = 0.0
    if with_prefix:
        ok_ids = sum(
            1 for e in with_prefix
            if validate_internal_id(e["entity_type"], e["identity_prefix"] + "sample1")
        )
        root_identity = ok_ids / len(with_prefix)

    matrix = configs["client_vision"]
    rows = matrix.get("coverage", [])
    covered = sum(1 for r in rows if r.get("covered") is True)
    client_coverage = (covered / len(rows)) if rows else 0.0

    cg_mapping = configs["common_grants"]
    exact_rt = _exact_roundtrips_pass(cg_mapping) and check("common_grants")
    loss_rep = _loss_reporting_pass(cg_mapping)

    # p0_open from the contradiction ledger (shared with Books 0/1); injectable
    # via configs["ledger"] so defect tests can flip it without touching files.
    ledger = configs.get("ledger")
    if not isinstance(ledger, dict):
        ledger = load_yaml(RATIFICATION_CONFIG_DIR / "contradiction_ledger.yaml")
    p0_open = len([c for c in ledger.get("contradictions", [])
                   if c.get("severity") == "P0" and c.get("status") != "RESOLVED"])

    predicates = {
        "glossary_complete": check("glossary"),
        "entity_boundaries_ratified": check("entity_types"),
        "root_entities_with_stable_identity": round(root_identity, 6),
        **predicates_extra,
        "state_machine_tests_pass": check("state_machines"),
        "revision_replay_tests_pass": check("revision_policy"),
        "fact_claim_evidence_tests_pass": check("fact_semantics"),
        "eligibility_determinism_contract_pass": check("eligibility_policy"),
        "application_document_model_pass": (
            check("requirement_types") and check("budget_policy")
            and check("artifact_families") and check("outcome")
        ),
        "common_grants_exact_roundtrip_pass": exact_rt,
        "common_grants_loss_reporting_pass": loss_rep,
        "client_phase1_domain_coverage": round(client_coverage, 6),
        "georgia_federal_fixture_tests_pass": _fixtures_pass(),
        "d0_draft_context_ready": _draft_context_ready(configs["draft_context"]),
        "extension_namespace_sound": check("extension_namespace"),
    }
    if test_results is None:
        predicates["adversarial_p0_pass"] = None
    else:
        predicates["adversarial_p0_pass"] = (
            test_results["exit_code"] == 0 and test_results["failed"] == 0
        )

    ready = (
        all(v is True for k, v in predicates.items()
            if k != "client_phase1_domain_coverage"
            and k != "root_entities_with_stable_identity")
        and predicates["client_phase1_domain_coverage"] >= 1.0
        and predicates["root_entities_with_stable_identity"] >= 1.0
        and predicates["adversarial_p0_pass"] is True
        and p0_open == 0
    )

    return {
        "book": "G0-B2",
        "status": "PASS" if ready else "FAIL",
        **predicates,
        "p0_open": p0_open,
        "ready_for_book3": ready,
        "evidence": {
            "test_results": test_results,
            "config_count": len(CONFIG_NAMES),
            "entity_count": len(all_entities),
            "coverage_row_count": len(rows),
        },
    }


_STEM_MAP = {
    "glossary.yaml": "glossary",
    "entity_types.yaml": "entity_types",
    "identifier_namespaces.yaml": "identifier_namespaces",
    "relationship_types.yaml": "relationships",
    "state_machines.yaml": "state_machines",
    "revision_policy.yaml": "revision_policy",
    "fact_semantics.yaml": "fact_semantics",
    "eligibility_policy.yaml": "eligibility_policy",
    "requirement_types.yaml": "requirement_types",
    "budget_policy.yaml": "budget_policy",
    "artifact_families.yaml": "artifact_families",
    "extension_namespace.yaml": "extension_namespace",
    "client_vision_matrix.yaml": "client_vision",
    "draft_context_policy.yaml": "draft_context",
    "common_grants_mapping.yaml": "common_grants",
    "outcome_policy.yaml": "outcome",
}


def build_live_lock(run_tests: bool = True) -> dict:
    configs = {_STEM_MAP[stem]: load_yaml(DOMAIN_CONFIG_DIR / stem)
               for stem in CONFIG_NAMES}
    test_results = _run_book2_tests() if run_tests else None
    return compute_lock(configs, test_results=test_results)


def main() -> int:
    ap = argparse.ArgumentParser(description="Build G0 Book 2 Reality Lock")
    ap.add_argument("--no-tests", action="store_true",
                    help="skip the pytest run (predicates reported as null)")
    ap.add_argument("--out", type=str, default=None)
    args = ap.parse_args()

    lock = build_live_lock(run_tests=not args.no_tests)
    out = Path(args.out) if args.out else COMMITTED_LOCK_PATH
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(lock, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(lock, indent=2))
    return 0 if lock["status"] == "PASS" else 1


if __name__ == "__main__":
    sys.exit(main())
