"""G1-INTEGRITY — claim-level factual integrity engine.

Mission §2-§17, §28-§31: every material assertion in the FINAL rendered
narrative must be locatable (sentence span), classified, resolved to a
governing authority (OrganizationFactPack | ResearchPack | Solicitation |
BudgetEngine | explicit client answer), temporally valid as-of the
application date, and numerically consistent with the canonical budget
and cross-section usage. Unsupported material claims never silently
become facts; unresolved CRITICAL missing facts block READY_FOR_REVIEW.
"""
from __future__ import annotations

import re
from dataclasses import dataclass, field
from datetime import date, datetime, timezone


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


# --- Canonical vocabularies ---------------------------------------------------

CLAIM_CLASSES = (
    "CANONICAL_FACT", "CLIENT_ASSERTION", "EXTERNAL_STATISTIC",
    "HISTORICAL_OUTCOME", "FUTURE_TARGET", "BUDGET_DERIVED",
    "SOLICITATION_FACT", "MODEL_INFERENCE", "ASSUMPTION", "UNKNOWN",
    "QUESTION")

FUTURE_MARKERS = (
    "will ", "will be", "plans to", "target of", "expects", "expects to",
    "will have", "will leverage", "will deliver", "will receive",
    "will serve", "anticipates", "goal is", "aims to")

PAST_MARKERS = (
    "has ", "have ", "serves", "currently", "operates", "delivered",
    "achieved", "produced", "maintains", "holds", "committed",
    "documented", "built", "founded", "brings", "supervises")


@dataclass(frozen=True)
class ApplicantStatus:
    """Canonical applicant status for one solicitation (mission §11).
    Requirement applicability derives from this single value."""
    status: str  # NEW | RECOMPETE | CONTINUATION | FORMULA_NEW | FORMULA_CONTINUATION | UNKNOWN
    basis: str   # authority that fixed it (client answer / fact pack)
    determined_at: str = ""

    @property
    def is_new(self) -> bool:
        return self.status in ("NEW", "FORMULA_NEW")


@dataclass(frozen=True)
class ClientAnswer:
    """Governed client answer resolving a missing fact (mission §10)."""
    fact_id: str
    value: object
    source: str = "CLIENT_ASSERTION"
    answered_at: str = ""
    principal: str = "client-1"
    project_id: str = "proj-g1q"
    revision_id: str = ""
    label: str = "CLIENT_ASSERTION"   # e.g. MOCK_CLIENT_ASSERTION


@dataclass(frozen=True)
class ResearchSource:
    """Normalized research provenance (mission §18-§20). Malformed
    free-text strings are never final provenance."""
    source_id: str
    publisher: str
    dataset: str
    official_url: str
    retrieval_date: str
    observation_period: str
    geography: str
    locator: str
    authority_tier: str      # OFFICIAL_PRIMARY | OFFICIAL_SECONDARY | AGGREGATOR
    content_hash: str = ""


RESEARCH_SOURCES = (
    ResearchSource(
        source_id="census_quickfacts_dade",
        publisher="U.S. Census Bureau",
        dataset="QuickFacts ACS 5-year 2020-2024",
        official_url="https://www.census.gov/quickfacts/dadecountygeorgia",
        retrieval_date="2026-08-28", observation_period="2020-2024",
        geography="Dade County, GA", locator="INC910224 / PEPTADR",
        authority_tier="OFFICIAL_PRIMARY"),
    ResearchSource(
        source_id="census_acs5_child_poverty_walker",
        publisher="U.S. Census Bureau (ACS 5-year)",
        dataset="Child poverty rate, under 18",
        official_url="https://www.census.gov/programs-surveys/acs",
        retrieval_date="2026-08-28", observation_period="2020-2024",
        geography="Walker County, GA", locator="table S1701",
        authority_tier="OFFICIAL_PRIMARY"),
    ResearchSource(
        source_id="gadoe_grad_rates",
        publisher="Georgia Department of Education",
        dataset="Cohort graduation rates (district comparison baseline)",
        official_url="https://www.gadoe.org",
        retrieval_date="2026-08-28", observation_period="2024-25",
        geography="Walker / Dade / Catoosa counties, GA",
        locator="CCRPI graduation data",
        authority_tier="OFFICIAL_PRIMARY"),
)

# Values licensed by the research pack: value -> (source_id, metric)
RESEARCH_STATS: dict[float, tuple[str, str]] = {
    19.5: ("census_acs5_child_poverty_walker",
           "child poverty rate, Walker County"),
    16.4: ("census_quickfacts_dade", "child poverty rate, Dade County"),
    41_629: ("census_quickfacts_dade", "median household income, Dade County"),
    88.6: ("census_quickfacts_dade", "HS graduate or higher, Dade County"),
    89.8: ("gadoe_grad_rates", "state HS graduation reference"),
}


# --- Canonical quantities + budget authority (mission §6-§7, §12-§13) ---------

# Numeric authority classes (mission §7): MODEL_INFERENCE is never a
# numeric license.
NumericAuthority = (
    "SOLICITATION_VALUE", "ORG_FACT_VALUE", "CLIENT_ASSERTION_VALUE",
    "RESEARCH_STATISTIC", "BUDGET_VALUE", "CALCULATED_VALUE",
    "FUTURE_TARGET",
)


@dataclass(frozen=True)
class CanonicalQuantity:
    """One canonical material quantity with a single governed source
    (mission §16-§17). Cross-section deviation fails QA."""
    quantity_id: str
    subject: str
    metric: str
    value: object
    unit: str
    period: str
    geography: str
    source_type: str            # NumericAuthority
    source_ref: str
    allowed_usage: str = "sectional"
    derivation: str = ""

    @property
    def numeric(self) -> float | None:
        try:
            return float(self.value)
        except (TypeError, ValueError):
            return None


class CanonicalQuantityRegistry:
    """Governed registry of every material quantity that must not drift.
    Fill from OrganizationFactPack, ClientAnswerPack, BudgetEngine
    (mission §6, §30)."""

    def __init__(self, quantities: list[CanonicalQuantity] | None = None):
        self.quantities: dict[str, CanonicalQuantity] = {
            q.quantity_id: q for q in (quantities or [])}

    def add(self, q: CanonicalQuantity) -> None:
        self.quantities[q.quantity_id] = q

    def find(self, *, subject: str | None = None,
             metric: str | None = None) -> list[CanonicalQuantity]:
        out = list(self.quantities.values())
        if subject:
            out = [q for q in out if q.subject == subject]
        if metric:
            out = [q for q in out if q.metric == metric]
        return out

    def dollar_values(self) -> set[float]:
        return {q.numeric for q in self.quantities.values()
                if q.source_type in ("BUDGET_VALUE", "SOLICITATION_VALUE")
                and q.numeric is not None}

    def all_values(self) -> set[float]:
        return {q.numeric for q in self.quantities.values()
                if q.numeric is not None}

    def to_dict(self) -> list[dict]:
        return [
            {"quantity_id": q.quantity_id, "subject": q.subject,
             "metric": q.metric, "value": str(q.value), "unit": q.unit,
             "period": q.period, "geography": q.geography,
             "source_type": q.source_type, "source_ref": q.source_ref,
             "allowed_usage": q.allowed_usage, "derivation": q.derivation}
            for q in self.quantities.values()]


def build_budget_fact_pack(budget) -> list[dict]:
    """Flatten a canonical BudgetReport into ordered monetary facts the
    drafting lane may reference verbatim (mission §13-§14). All values
    are read-only authority — the model may reference them, never alter
    them or introduce substitutes."""
    facts: list[dict] = []
    if budget is None:
        return facts
    try:
        total = float(str(budget.total).replace(",", ""))
        ceiling = float(str(budget.ceiling).replace(",", ""))
    except (ValueError, TypeError):
        total = ceiling = None
    if total is not None:
        facts.append({"budget_id": "total", "label": "total project cost",
                      "amount": f"${total:,.2f}", "source_ref": "BudgetEngine"})
    if ceiling is not None:
        facts.append({"budget_id": "ceiling", "label": "funding ceiling",
                      "amount": f"${ceiling:,.2f}",
                      "source_ref": "BudgetEngine"})
    for line in getattr(budget, "lines", []):
        try:
            amt = float(str(line.amount).replace(",", ""))
        except (ValueError, TypeError):
            continue
        facts.append({"budget_id": getattr(line, "line_id", ""),
                      "label": getattr(line, "description", ""),
                      "amount": f"${amt:,.2f}",
                      "category": getattr(line, "category", ""),
                      "source_ref": "BudgetEngine"})
    return facts


# --- Claim records --------------------------------------------------------------

@dataclass
class ClaimRecord:
    claim_id: str
    section_id: str
    locator: str                  # "p3.s2" paragraph.sentence locator
    claim_text: str
    subject: str
    predicate: str
    value: str
    claim_class: str
    materiality: str = "MATERIAL"  # MATERIAL | LOW
    source_refs: tuple[str, ...] = ()
    fact_refs: tuple[str, ...] = ()
    resolution_state: str = "SUPPORTED"  # SUPPORTED | TARGET_ALLOWED | UNSUPPORTED | UNKNOWN | NA
    allowed_by: str = ""
    model_run_ref: str | None = None

    def to_dict(self) -> dict:
        return {
            "claim_id": self.claim_id, "section_id": self.section_id,
            "locator": self.locator, "claim_text": self.claim_text[:200],
            "subject": self.subject, "predicate": self.predicate,
            "value": self.value, "claim_class": self.claim_class,
            "materiality": self.materiality,
            "source_refs": list(self.source_refs),
            "fact_refs": list(self.fact_refs),
            "resolution_state": self.resolution_state,
            "allowed_by": self.allowed_by,
            "model_run_ref": self.model_run_ref}


@dataclass
class ClaimLedger:
    claims: list[ClaimRecord] = field(default_factory=list)

    def add(self, c: ClaimRecord) -> None:
        self.claims.append(c)

    def by_class(self, cls: str) -> list[ClaimRecord]:
        return [c for c in self.claims if c.claim_class == cls]

    def unsupported_material(self) -> list[ClaimRecord]:
        return [c for c in self.claims
                if c.materiality == "MATERIAL"
                and c.resolution_state in ("UNSUPPORTED", "UNKNOWN")]

    def summary(self) -> dict:
        counts: dict[str, int] = {}
        for c in self.claims:
            counts[c.claim_class] = counts.get(c.claim_class, 0) + 1
        states: dict[str, int] = {}
        for c in self.claims:
            states[c.resolution_state] = states.get(c.resolution_state, 0) + 1
        material = [c for c in self.claims if c.materiality == "MATERIAL"]
        supported = [c for c in material
                     if c.resolution_state in ("SUPPORTED", "TARGET_ALLOWED")]
        return {
            "total": len(self.claims),
            "material": len(material),
            "supported": len(supported),
            "unsupported": len(material) - len(supported),
            "by_class": counts,
            "by_resolution": states,
        }


# --- Extraction ---------------------------------------------------------------

_NUM = re.compile(
    r"\$\s?[\d,]+(?:\.\d+)?"
    r"|\b\d[\d,]*(?:\.\d+)?\s?(?:percent|%)"
    r"|\b[-+]?\d+(?:\.\d+)?\b")
_YEAR = re.compile(r"\b(19|20)\d{2}\b")
_ORG_HINTS = ("coalition", "inc.", "organization", "EIN")


def _sentences(text: str) -> list[str]:
    parts = re.split(r"(?<=[.!?])\s+", text)
    return [p.strip().replace("\n", " ") for p in parts if len(p.strip()) > 30]


def _is_future(s: str) -> bool:
    low = s.lower()
    return any(m in low for m in FUTURE_MARKERS)


def _extract_number(s: str) -> str:
    m = _NUM.search(s)
    if not m:
        return ""
    val = m.group(0).replace("$", "").replace(",", "").replace("%", "").strip()
    try:
        return str(float(val))
    except ValueError:
        return val


def _match_fact_value(value: str, fact_pack, answers) -> tuple[str, str]:
    """value (normalized str) -> (fact_id, source) if any governed source
    licenses that exact quantity (mission §6)."""
    v = value.rstrip(".")
    try:
        fv = float(v)
    except ValueError:
        for a in answers:
            if str(a.value).lower() in value.lower():
                return a.fact_id, f"client_answer:{a.fact_id}"
        for f in fact_pack.facts.values():
            sv = str(f.value)
            if len(sv) > 8 and sv.lower() in value.lower():
                return f.fact_id, f.source
        return "", ""
    for a in answers:
        try:
            if float(str(a.value).replace(",", "")) == fv:
                return a.fact_id, f"client_answer:{a.fact_id}"
        except (ValueError, TypeError):
            continue
    for f in fact_pack.facts.values():
        try:
            if float(str(f.value).replace(",", "")) == fv:
                return f.fact_id, f.source
        except (ValueError, TypeError):
            if str(f.value) == value:
                return f.fact_id, f.source
    return "", ""


def _classify(sentence: str, value: str, fact_pack, answers,
              budget, profile) -> ClaimRecord:
    """Classify one material sentence against governed authorities."""
    low = sentence.lower()
    future = _is_future(sentence)
    src_refs: list[str] = []
    fact_refs: list[str] = []
    allowed_by = ""

    # 1. UNKNOWN / QUESTION markers from the writer
    if re.search(r"\bUNKNOWN:?", sentence):
        return ClaimRecord("", "", "", sentence, "", "", value, "UNKNOWN",
                           resolution_state="UNKNOWN")
    if sentence.rstrip().endswith("?"):
        return ClaimRecord("", "", "", sentence, "", "", value, "QUESTION",
                           resolution_state="UNKNOWN")

    # 2. Dollar amounts -> budget reconciliation
    if sentence.startswith("$") or "$" in sentence:
        if budget is not None:
            for line in budget.lines:
                try:
                    if float(str(line.amount).replace(",", "")) == float(
                            value.replace(",", "")):
                        fact_refs.append(f"budget:{line.line_id}")
                        src_refs.append("BudgetEngine")
                except (ValueError, TypeError):
                    continue
            try:
                if float(str(budget.total).replace(",", "")) == float(
                        value.replace(",", "")):
                    fact_refs.append("budget:total")
                    src_refs.append("BudgetEngine")
            except (ValueError, TypeError):
                pass
        fid, src = _match_fact_value(value, fact_pack, answers)
        if fid:
            fact_refs.append(fid)
            src_refs.append(src)
            allowed_by = src
        if fact_refs:
            cls = "BUDGET_DERIVED" if any(r.startswith("budget:")
                                          for r in fact_refs) \
                else ("CLIENT_ASSERTION" if "client_answer" in allowed_by
                      else "CANONICAL_FACT")
            return ClaimRecord("", "", "", sentence, "", "", value, cls,
                               source_refs=tuple(src_refs),
                               fact_refs=tuple(fact_refs),
                               allowed_by=allowed_by or "BudgetEngine")
        if future:
            # Clearly-labeled future planning numbers are legitimate
            # targets without historical evidence (mission §29); the
            # FACT_CRITIC and tense checks police misuse.
            return ClaimRecord("", "", "", sentence, "", "", value,
                               "FUTURE_TARGET",
                               resolution_state="TARGET_ALLOWED",
                               allowed_by="program_design_target")
        return ClaimRecord("", "", "", sentence, "", "", value,
                           "MODEL_INFERENCE", resolution_state="UNSUPPORTED")

    # 3. Percentages / statistics -> research pack lineage
    try:
        fv = float(value)
        if fv in RESEARCH_STATS:
            sid, metric = RESEARCH_STATS[fv]
            return ClaimRecord("", "", "", sentence, metric, "reports",
                               value, "EXTERNAL_STATISTIC",
                               source_refs=(sid, "ResearchPack"),
                               allowed_by=f"ResearchPack:{sid}")
    except ValueError:
        pass

    # 4. Solicitation facts
    if profile is not None:
        sol_terms = ("americorps", "georgia serves", "1700", "1,700",
                     "24%", "24 percent", "match")
        if any(t in low for t in sol_terms) and re.search(
                r"\b\d{3,}\b|24", low):
            return ClaimRecord("", "", "", sentence, "solicitation", "requires",
                               value, "SOLICITATION_FACT",
                               source_refs=(profile.snapshot.source_id,),
                               allowed_by="Solicitation")

    # 5. Exact fact-pack match (identity, counts, outcomes)
    fid, src = _match_fact_value(value, fact_pack, answers)
    if fid:
        fact = fact_pack.get(fid)
        cls = "CLIENT_ASSERTION" if (fact and fact.allowed_claim_type
                                     == "CLIENT_ASSERTION") else "CANONICAL_FACT"
        if fact and fact.allowed_claim_type == "FUTURE_TARGET" and future:
            cls = "FUTURE_TARGET"
        if "client_answer" in src:
            cls = "CLIENT_ASSERTION"
        if (fact and fact.allowed_claim_type == "STATISTIC") and not future:
            cls = "HISTORICAL_OUTCOME"
        return ClaimRecord("", "", "", sentence, fid, "states", value, cls,
                           fact_refs=(fid,), source_refs=(src,),
                           allowed_by=src)

    # 6. Future-tense numbers without lineage: legitimate planning targets
    # when clearly future-tense (mission §29); tense misuse is caught by
    # the FACT_CRITIC and the deterministic temporal gate.
    if future:
        return ClaimRecord("", "", "", sentence, "", "", value,
                           "FUTURE_TARGET", resolution_state="TARGET_ALLOWED",
                           allowed_by="program_design_target")
    return ClaimRecord("", "", "", sentence, "", "", value,
                       "MODEL_INFERENCE", resolution_state="UNSUPPORTED")


def extract_claims(sections: dict, fact_pack, answers=(),
                   budget=None, profile=None) -> ClaimLedger:
    """Extract the material Claim Ledger over the COMPLETE final narrative
    (mission §2-§4). Sentence-level spans: locator p{par}.s{i}."""
    ledger = ClaimLedger()
    n = 0
    for sid, sec in sections.items():
        paras = [p for p in sec.text.split("\n") if p.strip()]
        for pi, para in enumerate(paras, start=1):
            for si, sent in enumerate(_sentences(para), start=1):
                if not _NUM.search(sent) and not any(
                        h in sent for h in _ORG_HINTS):
                    continue
                value = _extract_number(sent)
                rec = _classify(sent, value, fact_pack, answers,
                                budget, profile)
                n += 1
                rec.claim_id = f"cl-int-{n:04d}"
                rec.section_id = sid
                rec.locator = f"p{pi}.s{si}"
                rec.model_run_ref = sec.model_ref
                ledger.add(rec)
    return ledger


# --- Gates ----------------------------------------------------------------------


def _parse_date(tok: str) -> date | None:
    m = re.match(r"(19|20)\d{2}-(\d{1,2})-(\d{1,2})", tok)
    if m:
        try:
            return date(int(m.group(1)), int(m.group(2)), int(m.group(3)))
        except ValueError:
            return None
    m = re.match(r"(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\w*\s+(\d{1,2}),?\s+((19|20)\d{2})",
                 tok)
    if m:
        # Regex captures the 3-letter prefix ("Mar"); key the map by
        # prefix so prose dates like "March 12, 2026" actually parse.
        months = {name[:3]: i for i, name in enumerate(
            calendar_month_names(), start=1)}
        try:
            return date(int(m.group(3)), months[m.group(1)], int(m.group(2)))
        except (KeyError, ValueError):
            return None
    return None


def calendar_month_names() -> list[str]:
    return ["January", "February", "March", "April", "May", "June", "July",
            "August", "September", "October", "November", "December"]


@dataclass
class TemporalConflict:
    claim_id: str
    section_id: str
    claim_text: str
    conflict_date: str
    as_of: str
    kind: str   # POST_DEADLINE_AS_CURRENT | FUTURE_AS_PAST


def check_temporal(ledger: ClaimLedger, as_of: date) -> list[TemporalConflict]:
    """Temporal validation as-of the application date (mission §13-§15).
    Dates after the as-of date presented as current/committed facts are
    contradictions. Scans BOTH the claim text and the provenance strings
    of its governing sources (a 'current' commitment sourced to a
    post-deadline resolution is temporally impossible)."""
    conflicts: list[TemporalConflict] = []
    # Only CURRENT-fact classes are temporally scanned. SOLICITATION_FACT
    # carries program-year labels (FY2026) that outlive the deadline by
    # design; FUTURE_TARGET is future by definition; EXTERNAL_STATISTIC
    # vintage is owned by the ResearchPack.
    temporal_classes = ("CANONICAL_FACT", "CLIENT_ASSERTION",
                        "HISTORICAL_OUTCOME", "BUDGET_DERIVED")
    for c in ledger.claims:
        if c.claim_class not in temporal_classes:
            continue
        scan_texts = [c.claim_text] + [
            f"source: {ref}" for ref in c.source_refs]
        found = False
        for scan in scan_texts:
            if found:
                break
            tokens = re.findall(
                r"(?:(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\w*\s+\d{1,2},?\s+((?:19|20)\d{2}))"
                r"|((?:19|20)\d{2}-\d{1,2}-\d{1,2})"
                r"|\b((?:19|20)\d{2})\b", scan)
            for tok in tokens:
                month_name, prose_year, iso, bare = tok
                if iso:
                    d = _parse_date(iso)
                    raw = iso
                elif month_name:
                    raw = f"{month_name} 1, {prose_year}"
                    d = _parse_date(raw)
                else:
                    raw = bare
                    d = None
                    if re.match(r"^(19|20)\d{2}$", bare):
                        d = date(int(bare), 12, 31)
                if d is None:
                    continue
                if d > as_of and not _is_future(c.claim_text):
                    kind = ("FUTURE_AS_PAST"
                            if c.claim_class in ("CANONICAL_FACT",
                                                 "CLIENT_ASSERTION",
                                                 "HISTORICAL_OUTCOME")
                            else "POST_DEADLINE_AS_CURRENT")
                    conflicts.append(TemporalConflict(
                        c.claim_id, c.section_id, c.claim_text[:160],
                        raw, as_of.isoformat(), kind))
                    found = True
                    break
    return conflicts


@dataclass
class NumericConflict:
    kind: str          # DERIVED_ARITHMETIC | CROSS_SECTION_DRIFT | BUDGET_DRIFT
    detail: str
    section_a: str = ""
    section_b: str = ""


def check_numerics(ledger: ClaimLedger, budget=None) -> list[NumericConflict]:
    """Numeric consistency against the canonical budget authority (mission
    §16-§17). Every dollar amount in prose that is >= 1000 must reconcile
    to a canonical budget value (total / ceiling / a governed line item).
    Any non-canonical dollar figure in prose is an UNAUTHORIZED_NUMERIC_CLAIM
    and blocks readiness — the model may never design a second budget.
    """
    conflicts: list[NumericConflict] = []
    canon: set[float] = set()
    if budget is not None:
        for line in budget.lines:
            try:
                canon.add(float(str(line.amount).replace(",", "")))
            except (ValueError, TypeError):
                continue
        for key in ("total", "ceiling"):
            try:
                canon.add(float(str(getattr(budget, key)).replace(",", "")))
            except (ValueError, TypeError, AttributeError):
                pass
    for c in ledger.claims:
        if "$" not in c.claim_text:
            continue
        seen: set[float] = set()
        for m in _NUM.finditer(c.claim_text):
            raw = m.group(0).replace("$", "").replace(",", "").strip()
            if "%" in m.group(0) or "percent" in raw:
                continue
            try:
                v = float(raw)
            except ValueError:
                continue
            if v < 1000 or v in seen or v in canon:
                seen.add(v)
                continue
            # A dollar figure that matches a RESEARCH_STAT (e.g. $41,629
            # median income) is an external statistic, not budget drift.
            if v in RESEARCH_STATS:
                continue
            conflicts.append(NumericConflict(
                kind="BUDGET_DRIFT", detail=(
                    f"dollar figure {m.group(0)} in prose is not a canonical "
                    f"budget amount (unauthorized numeric claim)"),
                section_a=c.section_id))
            break
    return conflicts


def check_derived_arithmetic(ledger: ClaimLedger) -> list[NumericConflict]:
    """Derived numbers (mission §17, §41): when prose states a product
    like 'N members x X sessions x Y weeks = Z', verify the arithmetic and
    ensure the claim is flagged BUDGET_DERIVED / derived — never silently
    invented. Detects impossible multiplicative claims."""
    conflicts: list[NumericConflict] = []
    for c in ledger.claims:
        low = c.claim_text.lower()
        if not any(t in low for t in ("yields", "totals", "a total of",
                                      "amounts to", "equals", "= ",
                                      "collective total", "x")):
            continue
        nums = [float(x) for x in _NUM.findall(c.claim_text)
                if all(ch.isdigit() or ch in ",." for ch in x)]
        # 3+ explicit factors plus a claimed sum means we can cross-check.
        ints = [int(n) for n in nums if n == int(n)]
        if len(ints) >= 3:
            # heuristic: largest claimed value should be the product of the
            # two leading multiplicands when they recur across the sentence
            factors = sorted(ints)
            if len(factors) >= 3:
                big = factors[-1]
                a, b = factors[0], factors[1]
                if a > 1 and b > 1 and abs(a * b - big) <= max(2, 0.02 * big):
                    conflicts.append(NumericConflict(
                        kind="DERIVED_ARITHMETIC",
                        detail=(f"derived total detected in prose: "
                                f"{a} x {b} = {big} — must be a governed "
                                f"CALCULATED_VALUE with lineage, not "
                                f"free-form arithmetic ({c.claim_text[:120]})"),
                        section_a=c.section_id))
    return conflicts


def check_cross_section_drift(ledger: ClaimLedger) -> list[NumericConflict]:
    """Cross-section quantity drift (mission §16): a canonical quantity
    (members, sites, weeks, etc.) must not appear with different values in
    different sections. Identical canonical values are synthesis language;
    deviations are contradictions."""
    usage: dict[str, dict[str, set]] = {}  # (subject,metric) -> section->values
    for c in ledger.claims:
        if c.claim_class in ("FUTURE_TARGET", "EXTERNAL_STATISTIC",
                             "BUDGET_DERIVED", "SOLICITATION_FACT"):
            continue
        key = (c.subject or "org", c.predicate or "quantity")
        bucket = usage.setdefault(key, {})
        bucket.setdefault(c.section_id, set()).add(c.value)
    conflicts: list[NumericConflict] = []
    for (subj, pred), bysec in usage.items():
        all_vals = [v for vals in bysec.values() for v in vals]
        if len(all_vals) < 2:
            continue
        numeric = set()
        for v in all_vals:
            try:
                numeric.add(float(v))
            except ValueError:
                pass
        if len(numeric) > 1 and 0 not in numeric:
            conflict_sections = [s for s, vals in bysec.items()
                                 if vals]
            conflicts.append(NumericConflict(
                kind="CROSS_SECTION_DRIFT",
                detail=(f"quantity ({subj}|{pred}) differs across sections: "
                        f"{sorted(numeric)} in "
                        f"{', '.join(sorted(conflict_sections))}"),
                section_a=next(iter(bysec))))
    return conflicts


@dataclass
class StatusConflict:
    detail: str
    claim_id: str = ""


def check_applicant_status(ledger: ClaimLedger,
                           status: ApplicantStatus) -> list[StatusConflict]:
    """Requirement consistency vs the canonical applicant status
    (mission §11-§12). NEW applicants must not reference prior AmeriCorps
    three-year grant cycles as their own history."""
    conflicts: list[StatusConflict] = []
    if status.is_new:
        for c in ledger.claims:
            low = c.claim_text.lower()
            prior_cycle = (("three-year" in low or "3-year" in low)
                           and ("grant cycle" in low or "prior" in low
                                or "last" in low or "recompete" in low))
            held = ("our" in low or "we " in low or "the coalition has"
                    in low or "organization has" in low)
            if prior_cycle and held:
                conflicts.append(StatusConflict(
                    detail=(f"NEW applicant references its own prior "
                            f"AmeriCorps cycle: {c.claim_text[:120]}"),
                    claim_id=c.claim_id))
    return conflicts


@dataclass
class MissingFactBreach:
    fact_id: str
    section_id: str
    claim_id: str
    claim_text: str
    detail: str


DOSAGE_PATTERNS = re.compile(
    r"(\d+\s*(?:sessions|tutoring sessions)\s*(?:per|/)\s*week"
    r"|\d+\s*hours?\s*(?:per|/)\s*session"
    r"|\d+(?:-\d+)?\s*(?:program\s+)?weeks?"
    r"|\b\d{2,}\s*service hours"
    r"|\d+\s*hours?\s*per\s*week)", re.IGNORECASE)


def enforce_missing_facts(matrix, answers, ledger: ClaimLedger
                          ) -> tuple[list[MissingFact], list[MissingFactBreach]]:
    """Unresolved CRITICAL facts (mission §8) + prose guard (mission §9):
    unresolved dosage facts may not appear as exact dosage numbers in
    prose."""
    answered = {a.fact_id for a in answers}
    unresolved = [m for m in matrix.missing
                  if m.severity == "CRITICAL_BLOCKER"
                  and m.fact_id not in answered]
    breaches: list[MissingFactBreach] = []
    if any(m.fact_id == "member_dosage" for m in unresolved):
        for c in ledger.claims:
            if DOSAGE_PATTERNS.search(c.claim_text):
                breaches.append(MissingFactBreach(
                    "member_dosage", c.section_id, c.claim_id,
                    c.claim_text[:160],
                    "dosage asserted in prose while member_dosage is "
                    "unresolved (prohibited claim)"))
    return unresolved, breaches


# --- Global pass -----------------------------------------------------------------


@dataclass
class GlobalIntegrityReport:
    run_at: str = ""
    as_of: str = ""
    ledger_summary: dict = field(default_factory=dict)
    unresolved_critical: list = field(default_factory=list)
    client_questions: list = field(default_factory=list)
    dosage_breaches: list = field(default_factory=list)
    temporal_conflicts: list = field(default_factory=list)
    numeric_conflicts: list = field(default_factory=list)
    derived_conflicts: list = field(default_factory=list)
    drift_conflicts: list = field(default_factory=list)
    status_conflicts: list = field(default_factory=list)
    quantities: list = field(default_factory=list)
    unsupported_claims: list = field(default_factory=list)
    readiness_state: str = "QA_BLOCKED"
    blockers: list = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "run_at": self.run_at, "as_of": self.as_of,
            "claims": self.ledger_summary,
            "unresolved_critical_facts": [m.fact_id for m
                                          in self.unresolved_critical],
            "client_questions": self.client_questions,
            "dosage_breaches": [b.__dict__ for b in self.dosage_breaches],
            "temporal_conflicts": [t.__dict__ for t
                                   in self.temporal_conflicts],
            "numeric_conflicts": [n.__dict__ for n
                                  in self.numeric_conflicts],
            "derived_conflicts": [n.__dict__ for n
                                  in self.derived_conflicts],
            "drift_conflicts": [n.__dict__ for n
                                in self.drift_conflicts],
            "canonical_quantities": self.quantities,
            "status_conflicts": [s.__dict__ for s
                                 in self.status_conflicts],
            "unsupported_claims": self.unsupported_claims,
            "readiness_state": self.readiness_state,
            "blockers": self.blockers}


def run_integrity_pass(*, sections: dict, fact_pack, matrix, answers=(),
                       budget=None, profile=None,
                       applicant_status: ApplicantStatus | None = None,
                       as_of: date | None = None,
                       quantities: CanonicalQuantityRegistry | None = None
                       ) -> GlobalIntegrityReport:
    """Global integrity pass after synthesis (mission §31)."""
    rep = GlobalIntegrityReport(run_at=_now())
    rep.as_of = (as_of or date.today()).isoformat()
    ledger = extract_claims(sections, fact_pack, answers, budget, profile)
    rep.ledger_summary = ledger.summary()

    if quantities is not None:
        rep.quantities = quantities.to_dict()

    unresolved, breaches = enforce_missing_facts(matrix, answers, ledger)
    rep.unresolved_critical = unresolved
    rep.client_questions = [m.client_question for m in unresolved]
    rep.dosage_breaches = breaches

    rep.temporal_conflicts = check_temporal(ledger, as_of or date.today())
    rep.numeric_conflicts = check_numerics(ledger, budget)
    rep.derived_conflicts = check_derived_arithmetic(ledger)
    rep.drift_conflicts = check_cross_section_drift(ledger)
    if applicant_status is not None:
        rep.status_conflicts = check_applicant_status(ledger,
                                                      applicant_status)

    blockers: list[str] = []
    if unresolved:
        blockers.append(
            f"{len(unresolved)} unresolved CRITICAL missing fact(s): "
            f"{[m.fact_id for m in unresolved]} -> client input required")
    if breaches:
        blockers.append(f"{len(breaches)} prohibited-claim breach(es): "
                        "unresolved facts asserted in prose")
    if rep.temporal_conflicts:
        blockers.append(f"{len(rep.temporal_conflicts)} temporal "
                        "contradiction(s)")
    if rep.numeric_conflicts:
        blockers.append(f"{len(rep.numeric_conflicts)} numeric "
                        "contradiction(s)")
    if rep.derived_conflicts:
        blockers.append(f"{len(rep.derived_conflicts)} derived-arithmetic "
                        "contradiction(s) with no governed lineage")
    if rep.drift_conflicts:
        blockers.append(f"{len(rep.drift_conflicts)} cross-section "
                        "quantity-drift contradiction(s)")
    if rep.status_conflicts:
        blockers.append(f"{len(rep.status_conflicts)} applicant-status "
                        "contradiction(s)")
    rep.unsupported_claims = [
        c.to_dict() for c in ledger.claims
        if c.materiality == "MATERIAL"
        and c.resolution_state in ("UNSUPPORTED", "UNKNOWN")][:20]
    if rep.unsupported_claims:
        blockers.append(
            f"{len(rep.unsupported_claims)} unsupported/unresolved material "
            "claim(s) with no governed authority")

    rep.blockers = blockers
    if unresolved:
        rep.readiness_state = "NEEDS_CLIENT_INPUT"
    elif blockers:
        rep.readiness_state = "QA_BLOCKED"
    else:
        rep.readiness_state = "READY_FOR_REVIEW"
    return rep
