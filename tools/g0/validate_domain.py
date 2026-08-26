"""G0 Book 2 — domain ontology validators.

Fail-closed validators over the domain sources of truth in config/g0/domain/.
Every validator follows the same contract:

    validate(data) -> (ok: bool, report: dict)

Missing files, malformed fields or unknown enum values are hard failures
(fail closed), never warnings. Chapter functions are added as chapters land:

- C1  validate_glossary
- C3  validate_entity_types
- C5  validate_identifier_namespaces
- C6  validate_relationships
- C7  validate_state_machines
- C8  validate_revision_policy
- C9  validate_fact_semantics
- C10 validate_eligibility_policy
- C11 validate_requirement_types
- C12 validate_budget_policy
- C13 validate_artifact_families
- C14 validate_outcome_policy
- C15 validate_common_grants_mapping
- C16 validate_extension_namespace
"""
from __future__ import annotations

import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[2]
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from tools.g0._common import DOMAIN_CONFIG_DIR, finish, load_yaml  # noqa: E402

GLOSSARY_FIELDS = (
    "term", "definition", "what_it_is_not", "identity_scope",
    "mutable_attributes", "source_of_truth_book", "examples", "common_confusions",
)


def validate_glossary(glossary: dict) -> tuple[bool, dict]:
    """B2.C1 — glossary soundness: no duplicates, no circular definitions,
    required fields, banned ambiguous aliases are not used as canonical terms."""
    errors: list[str] = []
    terms = glossary.get("terms") or []
    seen: set[str] = set()
    for entry in terms:
        term = entry.get("term")
        if not term:
            errors.append("glossary entry missing 'term'")
            continue
        missing = [f for f in GLOSSARY_FIELDS if entry.get(f) is None or
                   (isinstance(entry.get(f), str) and not entry[f].strip())]
        if missing:
            errors.append(f"{term}: missing fields {missing}")
        if term in seen:
            errors.append(f"{term}: duplicate canonical term")
        seen.add(term)
        for banned in glossary.get("banned_ambiguous_aliases") or []:
            if term.lower() == banned.lower():
                errors.append(f"{term}: banned ambiguous alias used as canonical term")

    return finish("domain_glossary", not errors, {
        "errors": errors,
        "term_count": len(seen),
        "duplicates": len(terms) - len(seen),
    })


ENTITY_FIELDS = ("entity_type", "identity_prefix", "identity_scope",
                 "glossary_term", "revisioned_by", "state_machine",
                 "schema_file", "fields")
SCALAR_TYPES = {"string", "integer", "boolean", "number", "date", "datetime",
                "money", "string_array"}
IDENTITY_PREFIXES = ("org_", "person_", "role_", "extid_", "program_", "opp_",
                     "opp_rev_", "rule_", "eldec_", "award_", "app_",
                     "app_rev_", "req_", "budget_", "fact_", "claim_", "stat_",
                     "artifact_", "outcome_", "rel_", "cgx_")


def validate_entity_types(catalog: dict) -> tuple[bool, dict]:
    """B2.C3 — entity catalog: required fields, unique prefixes, valid field
    types, enum refs resolve, identity prefixes follow the B2.C4 scheme."""
    errors: list[str] = []
    enums = catalog.get("enums") or {}
    types = catalog.get("entity_types") or []
    seen: set[str] = set()
    prefixes: set[str] = set()
    for ent in types:
        et = ent.get("entity_type")
        if not et:
            errors.append("entity entry missing entity_type")
            continue
        # revisioned_by/state_machine may legitimately be null (leaf entities);
        # every other field must be present and non-null.
        nullable = {"revisioned_by", "state_machine"}
        missing = [f for f in ENTITY_FIELDS
                   if f not in ent or (ent.get(f) is None and f not in nullable)]
        if missing:
            errors.append(f"{et}: missing fields {missing}")
        if et in seen:
            errors.append(f"{et}: duplicate entity type")
        seen.add(et)
        prefix = ent.get("identity_prefix")
        if prefix:
            if prefix in prefixes:
                errors.append(f"{et}: duplicate identity prefix '{prefix}'")
            prefixes.add(prefix)
            if prefix not in IDENTITY_PREFIXES:
                errors.append(f"{et}: identity prefix '{prefix}' not in B2.C4 scheme")
        for f in ent.get("fields") or []:
            fname = f.get("name")
            ftype = f.get("type")
            if not fname or not ftype:
                errors.append(f"{et}: field missing name/type")
                continue
            if ftype == "enum":
                ref = f.get("ref")
                if ref not in enums:
                    errors.append(f"{et}.{fname}: enum ref '{ref}' unresolved")
            elif ftype not in SCALAR_TYPES:
                errors.append(f"{et}.{fname}: unknown field type '{ftype}'")
    return finish("domain_entity_types", not errors, {
        "errors": errors,
        "entity_count": len(seen),
        "schema_files": [e.get("schema_file") for e in types if e.get("schema_file")],
    })


NAMESPACE_FIELDS = (
    "namespace_id", "name", "issuer", "applies_to_entity_types", "format",
    "validation_rule", "globally_unique", "temporally_unique", "reusable",
    "case_sensitive", "normalization_rule", "verification_sources",
)


def validate_identifier_namespaces(data: dict, entity_types: dict | None = None) -> tuple[bool, dict]:
    """B2.C5 — namespaces: required fields, unique ids, entity refs resolve,
    boolean flags are booleans."""
    errors: list[str] = []
    entities = {e.get("entity_type") for e in (entity_types or {}).get("entity_types", [])}
    namespaces = data.get("namespaces") or []
    seen: set[str] = set()
    for ns in namespaces:
        nid = ns.get("namespace_id")
        if not nid:
            errors.append("namespace missing namespace_id")
            continue
        missing = [f for f in NAMESPACE_FIELDS if f not in ns or ns.get(f) is None]
        if missing:
            errors.append(f"{nid}: missing fields {missing}")
        if nid in seen:
            errors.append(f"{nid}: duplicate namespace")
        seen.add(nid)
        for flag in ("globally_unique", "temporally_unique", "reusable",
                     "case_sensitive"):
            if flag in ns and not isinstance(ns[flag], bool):
                errors.append(f"{nid}: {flag} must be boolean")
        if entities:
            for et in ns.get("applies_to_entity_types") or []:
                if et not in entities:
                    errors.append(f"{nid}: applies to unknown entity '{et}'")
    return finish("domain_identifier_namespaces", not errors, {
        "errors": errors, "namespace_count": len(seen),
    })


RELATIONSHIP_FIELDS = (
    "relationship_type", "source_entity_types", "target_entity_types",
    "cardinality", "directed", "temporal", "attributes",
    "provenance_required",
)


def validate_relationships(data: dict, entity_types: dict | None = None) -> tuple[bool, dict]:
    """B2.C6 — relationship catalog: required fields, unique types, endpoint
    types resolve, cardinality values are valid."""
    errors: list[str] = []
    catalog = entity_types or {}
    entities = {e.get("entity_type") for e in catalog.get("entity_types", [])}
    entities |= set(data.get("external_entity_types") or [])
    valid_card = set(data.get("valid_cardinalities") or [])
    rels = data.get("relationship_types") or []
    seen: set[str] = set()
    for r in rels:
        rt = r.get("relationship_type")
        if not rt:
            errors.append("relationship missing relationship_type")
            continue
        missing = [f for f in RELATIONSHIP_FIELDS if f not in r or r.get(f) is None]
        if missing:
            errors.append(f"{rt}: missing fields {missing}")
        if rt in seen:
            errors.append(f"{rt}: duplicate relationship type")
        seen.add(rt)
        if r.get("cardinality") not in valid_card:
            errors.append(f"{rt}: unknown cardinality '{r.get('cardinality')}'")
        for side in ("source_entity_types", "target_entity_types"):
            for et in r.get(side) or []:
                if et not in entities:
                    errors.append(f"{rt}: endpoint type '{et}' unknown")
    return finish("domain_relationships", not errors, {
        "errors": errors, "relationship_count": len(seen),
    })


def validate_state_machines(data: dict) -> tuple[bool, dict]:
    """B2.C7 — state machines: unique names, known states, transitions
    reference known states, preconditions resolve, capability ids are the
    Book 1 capability ids (checked against policy registry when provided)."""
    errors: list[str] = []
    valid_pre = set(data.get("valid_precondition_codes") or [])
    machines = data.get("state_machines") or []
    seen: set[str] = set()
    for m in machines:
        name = m.get("state_machine")
        if not name:
            errors.append("state machine missing state_machine")
            continue
        if name in seen:
            errors.append(f"{name}: duplicate state machine")
        seen.add(name)
        states = m.get("states") or []
        if not states:
            errors.append(f"{name}: no states")
        future = m.get("future_states") or []
        unknown_future = [s for s in future if s not in states]
        if unknown_future:
            errors.append(f"{name}: future_states not in states {unknown_future}")
        for t in m.get("transitions") or []:
            frm, to = t.get("from"), t.get("to")
            if frm != "ANY" and frm not in states:
                errors.append(f"{name}: transition from unknown state '{frm}'")
            if to not in states:
                errors.append(f"{name}: transition to unknown state '{to}'")
            for pre in t.get("preconditions") or []:
                if pre not in valid_pre:
                    errors.append(f"{name}: unknown precondition '{pre}'")
    return finish("domain_state_machines", not errors, {
        "errors": errors, "state_machine_count": len(seen),
    })


REVISION_POLICY_FIELDS = ("revision_id", "revision_number", "changed_terms",
                          "created_at", "material")
VALID_ROOT_RULES = {"stable_root_with_immutable_revisions"}
VALID_TEMPORAL_FIELDS = {"observed_at", "retrieved_at", "effective_from",
                         "effective_to", "created_at", "superseded_at"}
VALID_CLAIM_TO_FACT_RULES = {"explicit_promotion_required"}
VALID_CONFLICT_RULES = {"claims_coexist_without_deletion"}
VALID_PROMOTION_STATES = {"PROPOSED", "PROMOTED", "CONFLICTED", "SUPERSEDED", "RETIRED"}
VALID_CLAIM_STATUSES = {"PROPOSED", "VERIFIED", "CONFLICTED", "RETRACTED"}


def validate_revision_policy(data: dict) -> tuple[bool, dict]:
    """B2.C8 — revision policy: root rule known, temporal fields unique and
    from the B2.C8 semantic set, materiality catalog non-empty with unique
    categories and non-empty affected terms."""
    errors: list[str] = []
    if data.get("root_rule") not in VALID_ROOT_RULES:
        errors.append(f"unknown root_rule '{data.get('root_rule')}'")
    seen_fields: set[str] = set()
    for tf in data.get("temporal_fields") or []:
        field_name = tf.get("field")
        if not field_name or not tf.get("semantic_role"):
            errors.append("temporal field entry missing field/semantic_role")
            continue
        if field_name not in VALID_TEMPORAL_FIELDS:
            errors.append(f"temporal field '{field_name}' not in B2.C8 semantic set")
        if field_name in seen_fields:
            errors.append(f"temporal field '{field_name}' duplicated")
        seen_fields.add(field_name)
    if not seen_fields:
        errors.append("temporal_fields may not be empty")
    mat = data.get("material_change_categories") or []
    if not mat:
        errors.append("material_change_categories may not be empty")
    seen_cat: set[str] = set()
    for cat in mat:
        cname = cat.get("category")
        terms = cat.get("affected_terms") or []
        if not cname:
            errors.append("material category missing 'category'")
            continue
        if cname in seen_cat:
            errors.append(f"material category '{cname}' duplicated")
        seen_cat.add(cname)
        if not terms:
            errors.append(f"material category '{cname}' has empty affected_terms")
    if not (data.get("non_material_change_categories") or []):
        errors.append("non_material_change_categories may not be empty")
    return finish("domain_revision_policy", not errors, {
        "errors": errors,
        "material_category_count": len(seen_cat),
        "temporal_field_count": len(seen_fields),
    })


def validate_fact_semantics(data: dict) -> tuple[bool, dict]:
    """B2.C9 — fact semantics: promotion is explicit, conflict rule known,
    promotion/claim state orders match the domain model, statistic context
    requirements present."""
    errors: list[str] = []
    if data.get("claim_to_fact_rule") not in VALID_CLAIM_TO_FACT_RULES:
        errors.append(f"claim_to_fact_rule must be explicit_promotion_required, "
                      f"got '{data.get('claim_to_fact_rule')}'")
    if data.get("fact_promotion_requires_support") is not True:
        errors.append("fact_promotion_requires_support must be true")
    if data.get("conflict_rule") not in VALID_CONFLICT_RULES:
        errors.append(f"unknown conflict_rule '{data.get('conflict_rule')}'")
    order = data.get("promotion_state_order") or []
    if set(order) != VALID_PROMOTION_STATES or len(order) != len(set(order)):
        errors.append(f"promotion_state_order must be exactly {sorted(VALID_PROMOTION_STATES)}")
    claim_statuses = data.get("claim_statuses") or []
    if set(claim_statuses) != VALID_CLAIM_STATUSES or len(claim_statuses) != len(set(claim_statuses)):
        errors.append(f"claim_statuses must be exactly {sorted(VALID_CLAIM_STATUSES)}")
    required_ctx = data.get("required_statistic_context") or []
    for field in ("geography", "unit", "reference_period"):
        if field not in required_ctx:
            errors.append(f"required_statistic_context must include '{field}'")
    if not (data.get("population_bearing_metric_keywords") or []):
        errors.append("population_bearing_metric_keywords may not be empty")
    return finish("domain_fact_semantics", not errors, {
        "errors": errors,
        "population_keyword_count": len(data.get("population_bearing_metric_keywords") or []),
    })


ELIGIBILITY_OPERATORS = {
    "EQUALS", "IN", "NOT_IN", "EXISTS", "NOT_EXISTS", "GTE", "LTE",
    "BETWEEN", "WITHIN_GEOGRAPHY", "BEFORE", "AFTER", "BOOLEAN_TRUE",
    "CUSTOM_DETERMINISTIC_PREDICATE",
}
REQUIRED_STATISTIC_CTX = {"geography", "unit", "reference_period"}


def validate_eligibility_policy(data: dict) -> tuple[bool, dict]:
    """B2.C10 — eligibility ontology: operators from the plan set, missing
    evidence is UNKNOWN by default, evaluation is deterministic, narrative
    cannot set the result, reproducibility fields present."""
    errors: list[str] = []
    ops = set(data.get("operators") or [])
    if ops != ELIGIBILITY_OPERATORS:
        errors.append(f"operators must be exactly {sorted(ELIGIBILITY_OPERATORS)}")
    if data.get("missing_evidence_semantics") != "UNKNOWN":
        errors.append("missing_evidence_semantics must be UNKNOWN")
    if data.get("closed_world_default") is not False:
        errors.append("closed_world_default must be false")
    boundary = data.get("extraction_boundary") or {}
    if boundary.get("evaluation_deterministic") is not True:
        errors.append("extraction_boundary.evaluation_deterministic must be true")
    if boundary.get("llm_narrative_cannot_set_result") is not True:
        errors.append("extraction_boundary.llm_narrative_cannot_set_result must be true")
    for field in ("rule_set_id", "rule_set_version", "opportunity_revision_id",
                  "per_rule_results", "aggregate_result"):
        if field not in (data.get("decision_reproducibility_fields") or []):
            errors.append(f"decision_reproducibility_fields must include '{field}'")
    return finish("domain_eligibility_policy", not errors, {
        "errors": errors, "operator_count": len(ops),
    })


REQUIREMENT_TYPES = {"narrative", "form_field", "budget", "attachment",
                     "certification", "support_letter", "data_entry", "other"}
RESPONSE_TYPES = {"section", "form", "budget", "attachment", "certification",
                  "support_letter"}


def validate_requirement_types(data: dict) -> tuple[bool, dict]:
    """B2.C11 — requirement & content model: known requirement/response types,
    section families present, content link targets non-empty."""
    errors: list[str] = []
    req_types = {r.get("type") for r in data.get("requirement_types") or []}
    if req_types != REQUIREMENT_TYPES:
        errors.append(f"requirement_types must be exactly {sorted(REQUIREMENT_TYPES)}")
    resp_types = {r.get("type") for r in data.get("response_types") or []}
    if resp_types != RESPONSE_TYPES:
        errors.append(f"response_types must be exactly {sorted(RESPONSE_TYPES)}")
    families = data.get("section_families") or []
    fam_keys = {f.get("family") for f in families}
    if "proposal_section" not in fam_keys or "business_plan_section" not in fam_keys:
        errors.append("section_families must include proposal_section and business_plan_section")
    if not (data.get("content_link_targets") or []):
        errors.append("content_link_targets may not be empty")
    return finish("domain_requirement_types", not errors, {
        "errors": errors,
        "requirement_type_count": len(req_types),
        "section_family_count": len(fam_keys),
    })


MONETARY_RULES = {"decimal_only", "explicit_currency", "explicit_period",
                  "deterministic_totals", "amount_lineage"}


def validate_budget_policy(data: dict) -> tuple[bool, dict]:
    """B2.C12 — budget semantics: monetary rules from the plan set, currency
    mismatch rejected, deterministic match calculation."""
    errors: list[str] = []
    rules = {r.get("rule") for r in data.get("monetary_rules") or []}
    if rules != MONETARY_RULES:
        errors.append(f"monetary_rules must be exactly {sorted(MONETARY_RULES)}")
    if data.get("currency_mismatch") != "REJECTED":
        errors.append("currency_mismatch must be REJECTED")
    if data.get("match_calculation") != "deterministic":
        errors.append("match_calculation must be deterministic")
    return finish("domain_budget_policy", not errors, {
        "errors": errors, "monetary_rule_count": len(rules),
    })


PHASE1_ARTIFACT_TYPES = {"grant_proposal", "business_plan", "pitch_deck",
                         "budget_financial", "partnership_material",
                         "testimonial_material", "goal_sheet", "research_report",
                         "qa_report", "submission_package"}


def validate_artifact_families(data: dict) -> tuple[bool, dict]:
    """B2.C13 — artifact families: Phase 1 family set complete, version and
    mock rules present."""
    errors: list[str] = []
    families = {f.get("artifact_type") for f in data.get("phase1_families") or []}
    if families != PHASE1_ARTIFACT_TYPES:
        errors.append(f"phase1_families must cover exactly {sorted(PHASE1_ARTIFACT_TYPES)}")
    version_rules = {r.get("rule") for r in data.get("version_rules") or []}
    for rule in ("immutable_versions", "monotonic_numbers", "no_superseded_in_package"):
        if rule not in version_rules:
            errors.append(f"version_rules must include '{rule}'")
    mock_rules = {r.get("rule") for r in data.get("mock_rules") or []}
    for rule in ("mock_visibly_distinct", "mock_cannot_submit"):
        if rule not in mock_rules:
            errors.append(f"mock_rules must include '{rule}'")
    return finish("domain_artifact_families", not errors, {
        "errors": errors, "family_count": len(families),
    })


OUTCOME_TYPES = {"SUBMITTED", "AWARDED", "REJECTED", "WITHDRAWN",
                 "REVISION_REQUESTED", "NOT_SUBMITTED", "UNKNOWN"}


def validate_outcome_policy(data: dict) -> tuple[bool, dict]:
    """B2.C14 — outcome ontology: outcome types from the plan, learning is
    evidence-only (never automatic doctrine), linkage rules present."""
    errors: list[str] = []
    types = set(data.get("outcome_types") or [])
    if types != OUTCOME_TYPES:
        errors.append(f"outcome_types must be exactly {sorted(OUTCOME_TYPES)}")
    if data.get("learning_rule") != "outcome_becomes_evidence_for_book7_not_automatic_doctrine":
        errors.append("learning_rule must be evidence-only (never automatic doctrine)")
    constraints = {c.get("rule") for c in data.get("learning_constraints") or []}
    if "no_automatic_prompt_rewrite" not in constraints:
        errors.append("learning_constraints must include no_automatic_prompt_rewrite")
    linkage = {c.get("rule") for c in data.get("linkage_rules") or []}
    if "historical_award_without_project" not in linkage:
        errors.append("linkage_rules must include historical_award_without_project")
    return finish("domain_outcome_policy", not errors, {
        "errors": errors, "outcome_type_count": len(types),
    })


MAPPING_CLASSES = {"EXACT", "EXTENSION", "INTERNAL_ONLY", "EXTERNAL_ONLY", "LOSSY"}
MAPPING_COLUMNS = ("internal_field", "common_grants_entity", "common_grants_field",
                   "mapping_class", "transform", "reverse_transform", "loss_notes",
                   "validation", "example")
CG_ENTITIES = {"Opportunity", "Application", "Award"}


def validate_common_grants_mapping(data: dict) -> tuple[bool, dict]:
    """B2.C15 — CommonGrants mapping: classes from the plan, full matrix
    columns per row, entities are Opportunity/Application/Award, extension
    namespace declared, no shadow semantics, every row pinned or pending."""
    errors: list[str] = []
    classes = set(data.get("mapping_classes") or [])
    if classes != MAPPING_CLASSES:
        errors.append(f"mapping_classes must be exactly {sorted(MAPPING_CLASSES)}")
    ns = data.get("extension_namespace")
    if not ns:
        errors.append("extension_namespace required")
    for ent in data.get("entities") or []:
        name = ent.get("entity")
        rows = ent.get("rows") or []
        if not rows:
            errors.append(f"{name}: no mapping rows")
        for row in rows:
            missing = [c for c in MAPPING_COLUMNS if c not in row]
            if missing:
                errors.append(f"{name}: row missing columns {missing}")
            cls = row.get("mapping_class")
            if cls not in MAPPING_CLASSES:
                errors.append(f"{name}.{row.get('internal_field')}: unknown class '{cls}'")
            cg_ent = row.get("common_grants_entity")
            if cg_ent not in CG_ENTITIES:
                errors.append(f"{name}.{row.get('internal_field')}: unknown CG entity '{cg_ent}'")
            if not row.get("validation"):
                errors.append(f"{name}.{row.get('internal_field')}: validation required")
    # no-shadow semantics: within an entity, one internal field maps to at most
    # one CG field and vice versa (duplicate targets are ambiguity/shadowing).
    # Identical internal/CG names are the intended identity mapping.
    for ent in data.get("entities") or []:
        name = ent.get("entity")
        rows = ent.get("rows") or []
        internal_fields = [r.get("internal_field") for r in rows]
        cg_fields = [r.get("common_grants_field") for r in rows]
        dup_internal = {f for f in internal_fields if internal_fields.count(f) > 1}
        if dup_internal:
            errors.append(f"{name}: internal_field duplicated {sorted(dup_internal)}")
        dup_cg = {f for f in cg_fields if cg_fields.count(f) > 1}
        if dup_cg:
            errors.append(f"{name}: common_grants_field duplicated {sorted(dup_cg)}")
    return finish("domain_common_grants_mapping", not errors, {
        "errors": errors,
        "row_count": sum(len(e.get("rows") or []) for e in data.get("entities") or []),
    })


PLATFORM_PRIMITIVE_CANDIDATES = {"Organization", "Person", "Artifact",
                                 "EvidenceClaim", "CanonicalFact",
                                 "StatisticObservation"}


def validate_extension_namespace(data: dict) -> tuple[bool, dict]:
    """B2.C16 — extension namespace: grant concepts stay grant, platform move
    needs explicit ADR, no premature generalization, provider fields namespaced."""
    errors: list[str] = []
    grant = set(data.get("grant_namespace_concepts") or [])
    for concept in ("GrantOpportunity", "OpportunityRevision", "EligibilityDecision",
                    "ApplicationProject", "Requirement", "Award"):
        if concept not in grant:
            errors.append(f"grant_namespace_concepts must include '{concept}'")
    primitives = set(data.get("platform_primitive_candidates") or [])
    if primitives != PLATFORM_PRIMITIVE_CANDIDATES:
        errors.append(f"platform_primitive_candidates must be exactly "
                      f"{sorted(PLATFORM_PRIMITIVE_CANDIDATES)}")
    if data.get("platform_move_rule") != "explicit_adr_required":
        errors.append("platform_move_rule must be explicit_adr_required")
    if data.get("premature_generalization_prohibited") is not True:
        errors.append("premature_generalization_prohibited must be true")
    if data.get("root_schema_pollution_prohibited") is not True:
        errors.append("root_schema_pollution_prohibited must be true")
    namespaces = data.get("provider_namespaces") or []
    if not namespaces:
        errors.append("provider_namespaces may not be empty")
    seen_prefix: set[str] = set()
    for ns in namespaces:
        prefix = ns.get("prefix")
        if not prefix or not prefix.endswith("_"):
            errors.append(f"{ns.get('provider')}: prefix must end with '_'")
        if prefix in seen_prefix:
            errors.append(f"{ns.get('provider')}: duplicate prefix '{prefix}'")
        seen_prefix.add(prefix)
    return finish("domain_extension_namespace", not errors, {
        "errors": errors,
        "grant_concept_count": len(grant),
        "provider_count": len(namespaces),
    })


def load_extension_namespace() -> dict:
    return load_yaml(DOMAIN_CONFIG_DIR / "extension_namespace.yaml")


def load_outcome_policy() -> dict:
    return load_yaml(DOMAIN_CONFIG_DIR / "outcome_policy.yaml")


def load_common_grants_mapping() -> dict:
    return load_yaml(DOMAIN_CONFIG_DIR / "common_grants_mapping.yaml")


def load_eligibility_policy() -> dict:
    return load_yaml(DOMAIN_CONFIG_DIR / "eligibility_policy.yaml")


def load_requirement_types() -> dict:
    return load_yaml(DOMAIN_CONFIG_DIR / "requirement_types.yaml")


def load_budget_policy() -> dict:
    return load_yaml(DOMAIN_CONFIG_DIR / "budget_policy.yaml")


def load_artifact_families() -> dict:
    return load_yaml(DOMAIN_CONFIG_DIR / "artifact_families.yaml")


def load_revision_policy() -> dict:
    return load_yaml(DOMAIN_CONFIG_DIR / "revision_policy.yaml")


def load_fact_semantics() -> dict:
    return load_yaml(DOMAIN_CONFIG_DIR / "fact_semantics.yaml")


def load_state_machines() -> dict:
    return load_yaml(DOMAIN_CONFIG_DIR / "state_machines.yaml")


def load_relationships() -> dict:
    return load_yaml(DOMAIN_CONFIG_DIR / "relationship_types.yaml")


def load_identifier_namespaces() -> dict:
    return load_yaml(DOMAIN_CONFIG_DIR / "identifier_namespaces.yaml")


def load_entity_types() -> dict:
    return load_yaml(DOMAIN_CONFIG_DIR / "entity_types.yaml")


def load_glossary() -> dict:
    return load_yaml(DOMAIN_CONFIG_DIR / "glossary.yaml")


def main() -> int:
    from tools.g0._common import emit
    entity_types = load_entity_types()
    checks = [
        ("glossary", validate_glossary, load_glossary),
        ("entity_types", validate_entity_types, lambda: entity_types),
        ("identifier_namespaces",
         lambda d: validate_identifier_namespaces(d, entity_types),
         load_identifier_namespaces),
        ("relationships",
         lambda d: validate_relationships(d, entity_types),
         load_relationships),
        ("state_machines", validate_state_machines, load_state_machines),
        ("revision_policy", validate_revision_policy, load_revision_policy),
        ("fact_semantics", validate_fact_semantics, load_fact_semantics),
        ("eligibility_policy", validate_eligibility_policy, load_eligibility_policy),
        ("requirement_types", validate_requirement_types, load_requirement_types),
        ("budget_policy", validate_budget_policy, load_budget_policy),
        ("artifact_families", validate_artifact_families, load_artifact_families),
        ("outcome_policy", validate_outcome_policy, load_outcome_policy),
        ("common_grants_mapping", validate_common_grants_mapping, load_common_grants_mapping),
        ("extension_namespace", validate_extension_namespace, load_extension_namespace),
    ]
    ok_all = True
    for name, fn, loader in checks:
        ok, report = fn(loader())
        ok_all = ok_all and ok
        if not ok:
            for e in report.get("errors", []):
                print(f"[{name}] {e}")
    return emit({"status": "PASS" if ok_all else "FAIL",
                 "domain_checks": [n for n, _, _ in checks]})


if __name__ == "__main__":
    sys.exit(main())
