"""B2.C17 tests — Georgia + Federal Fixture Architecture.

Every scenario (GA-1, FED-1, AWARD-1, COMMUNITY-1) validates against the
derived domain schemas and relationship/state invariants. Fixtures are
semantic examples, not live adapters.
"""
from __future__ import annotations

import json
from dataclasses import asdict, is_dataclass
from decimal import Decimal
from enum import Enum
from pathlib import Path

import jsonschema

from prototype.g0.domain.fixtures import SCENARIOS
from prototype.g0.domain.models import (
    ArtifactType,
    EligibilityStatus,
    FactPromotionState,
)

_ROOT = Path(__file__).resolve().parents[3]
SCHEMA_DIR = _ROOT / "schemas/g0/domain"


def _convert(value):
    """dataclass -> schema-safe dict: enums to .value, Decimal to str (money)
    or float (number), nested dataclasses/tuples recursively. Unset (None)
    optional fields are omitted — the schemas are non-nullable by design."""
    if isinstance(value, Enum):
        return value.value
    if isinstance(value, Decimal):
        return str(value)
    if isinstance(value, tuple):
        return [_convert(v) for v in value]
    if is_dataclass(value):
        return {k: _convert(v) for k, v in asdict(value).items()
                if v is not None}
    return value


def _entity_schema(entity: str) -> dict:
    path = SCHEMA_DIR / f"{entity}.schema.json"
    if not path.exists():
        # map model names to catalog schema filenames
        name = entity.replace("_", "")
        path = SCHEMA_DIR / f"{name}.schema.json"
    return json.loads(path.read_text(encoding="utf-8"))


def _validate_schema(obj) -> None:
    """Validate an object against its derived schema, keeping only fields the
    schema declares (catalog is authoritative; model extras are dropped)."""
    from tools.g0.generate_domain_schemas import generate_schemas
    from tools.g0.validate_domain import load_entity_types
    schemas = generate_schemas(load_entity_types())
    title = type(obj).__name__
    schema = next((s for s in schemas.values() if s["title"] == title), None)
    assert schema is not None, f"no derived schema for {title}"
    raw = _convert(obj)
    instance = {k: v for k, v in raw.items() if k in schema["properties"]}
    # money fields expect string pattern; number fields expect JSON number
    for k, prop in schema["properties"].items():
        if k in instance and prop.get("type") == "number" and isinstance(instance[k], str):
            instance[k] = float(instance[k])
    jsonschema.validate(instance, schema)


def test_all_scenarios_present():
    assert set(SCENARIOS) == {"GA-1", "FED-1", "AWARD-1", "COMMUNITY-1"}


# --- GA-1 ----------------------------------------------------------------------

def test_ga1_schemas_valid():
    s = SCENARIOS["GA-1"]
    for obj in (s["organization"], s["opportunity"], s["revision"],
                s["decision"], s["project"], s["fact"], s["claim"]):
        _validate_schema(obj)
    for ext in s["identifiers"]:
        _validate_schema(ext)
    for art in s["artifacts"]:
        _validate_schema(art)
    for req in s["requirements"]:
        _validate_schema(req)


def test_ga1_relationship_and_state_invariants():
    s = SCENARIOS["GA-1"]
    # project anchored to the EXACT revision used by the decision and rule set
    assert s["project"].opportunity_revision_id == s["revision"].revision_id
    assert s["decision"].opportunity_revision_id == s["revision"].revision_id
    assert s["rule_set"].opportunity_revision_id == s["revision"].revision_id
    assert s["project"].organization_id == s["organization"].organization_id
    # decision is ELIGIBLE and reproducible per-rule
    assert s["decision"].result is EligibilityStatus.ELIGIBLE
    assert len(s["decision"].per_rule_results) == 2
    # facts reference support; proposal and business plan are distinct families
    assert s["fact"].promotion_state is FactPromotionState.PROMOTED
    assert s["fact"].supporting_claim_ids == (s["claim"].claim_id,)
    families = {a.artifact_type for a in s["artifacts"]}
    assert families == {ArtifactType.GRANT_PROPOSAL, ArtifactType.BUSINESS_PLAN}
    # verified identifiers are claimed
    assert all(e.verification_state.value == "VERIFIED" for e in s["identifiers"])


# --- FED-1 ---------------------------------------------------------------------

def test_fed1_schemas_valid():
    s = SCENARIOS["FED-1"]
    for obj in (s["program"], s["opportunity"], s["revision"], s["project"]):
        _validate_schema(obj)


def test_fed1_program_opportunity_revision_chain():
    s = SCENARIOS["FED-1"]
    assert s["opportunity"].program_id == s["program"].program_id
    assert s["revision"].opportunity_id == s["opportunity"].opportunity_id
    assert s["program"].assistance_listing == "93.569"
    assert s["project"].opportunity_revision_id == s["revision"].revision_id


# --- AWARD-1 -------------------------------------------------------------------

def test_award1_schemas_valid():
    s = SCENARIOS["AWARD-1"]
    for obj in (s["funder"], s["recipient"], s["opportunity"], s["award"]):
        _validate_schema(obj)


def test_award1_winner_intelligence_invariants():
    s = SCENARIOS["AWARD-1"]
    award = s["award"]
    # recipient resolves to a canonical Organization
    assert award.recipient_id == s["recipient"].organization_id
    assert award.funder_id == s["funder"].organization_id
    # source ids carried without replacing internal identity
    assert award.external_award_ids[0].namespace == "USAspending"
    assert award.external_award_ids[0].entity_type == "Award"
    # amount is fixed-point
    assert isinstance(award.amount, Decimal)


# --- COMMUNITY-1 ---------------------------------------------------------------

def test_community1_schemas_valid():
    _validate_schema(SCENARIOS["COMMUNITY-1"]["statistic"])


def test_community1_context_preserved():
    stat = SCENARIOS["COMMUNITY-1"]["statistic"]
    # context is preserved, never flattened to a bare number
    assert stat.geography and stat.population and stat.reference_period
    assert stat.unit == "percent"
    assert stat.dataset_version == "ACS-5yr-2023"
    assert stat.methodology
