# G0-B3 — Source Precedence & Freshness Constitution (C8-C9)

## Scope

Defines **which source governs which fact class** when sources disagree (B3.C8) and **when data is current enough for its intended use** (B3.C9). Together they make fact resolution deterministic and freshness policy explicit and fail-closed.

## C8 — Source Precedence Matrix

Config of truth: `config/g0/source/precedence_matrix.yaml` · Prototype: `prototype/g0/source/precedence.py`

Each fact class maps to an **ordered precedence chain** of source-class stages (lower index = more authoritative). Identity is resolved per fact class × source class — a higher generic source tier never outranks a specialized authoritative source for the fact it governs.

Representative chains (most authoritative first):

- **Opportunity deadline:** `OFFICIAL_ISSUER → OFFICIAL_AGGREGATOR → (GOVERNED_WEB|OFFICIAL_TRANSACTIONAL) → TRUSTED_CURATED → (GOVERNED_WEB|USER_PROVIDED) → USER_PROVIDED`
- **Tax-exempt status:** `OFFICIAL_TRANSACTIONAL → TRUSTED_CURATED → GOVERNED_WEB → USER_PROVIDED`
- **Historical award amount:** `OFFICIAL_TRANSACTIONAL → TRUSTED_CURATED → GOVERNED_WEB`
- **Client program intent:** `USER_PROVIDED (client-approved) → USER_PROVIDED (conversation) → (TRUSTED_CURATED|GOVERNED_WEB)`

### Client control

`client_program_intent`, `user_preferences_intention`, and `internal_project_goals` are client-controlled. Client intent may outrank government data **only** for the facts the client controls — never for legal/issuer facts like `tax_exempt_status` or `opportunity_deadline`.

### Equal-authority conflict

**No automatic last-write-wins.** When two claims at the same resolved authority disagree, the fact state becomes `CONFLICTED` / `REVIEW_REQUIRED` unless a temporal (`source_effective_at`) rule resolves it.

## C9 — Freshness Constitution

Config of truth: `config/g0/source/freshness_policy.yaml` · Prototype: `prototype/g0/source/freshness.py`

### Freshness states

`FRESH`, `SOFT_STALE`, `HARD_STALE`, `UNKNOWN_FRESHNESS`, `HISTORICAL_FIXED`.

### Per-fact-class policy

Each policy carries `fact_class`, `source_class`, `soft_stale_after`, `hard_stale_after`, `refresh_on_access`, `refresh_on_deadline_window`, `latest_vintage_rule`, and `critical_use_block_on_hard_stale`. The same data age can be **HARD_STALE** for an active-opportunity deadline yet **FRESH** for a funder-identity record.

### Vintage-based facts

- **Historical award** → `HISTORICAL_FIXED` once verified, absent correction/revision discovery.
- **IRS annual filings** → vintage-based, not stale merely because old, while the latest official filing remains that vintage.
- **ACS/SAIPE community statistics** → dataset-vintage based; distinguishes reference period from retrieval time.

### Deadline proximity

Five tiers (>30d, 14–30d, 7–14d, <7d, <24h); closer deadlines impose stronger refresh/health requirements.

**Critical use-once facts** (`opportunity_deadline`, `opportunity_eligibility`) must block submission-ready state on hard-stale.

## Tests

`tests/g0/book3/test_precedence_freshness.py` — 12 tests covering:
- fact-specific precedence works; official issuer outranks user recollection;
- higher generic tier does NOT outrank specialized authority;
- equal-authority disagreement → CONFLICTED (no last-write-wins);
- equal-authority disagreement with a newer effective date resolves via temporal rule;
- client-intent outranks government only for the facts the client controls;
- same age → different freshness for different fact classes;
- annual-statistic latest-vintage remains valid; superseded vintage → HARD_STALE;
- hard-stale deadline blocks submission readiness;
- historical-fixed award remains valid absent correction; unknown age → UNKNOWN_FRESHNESS.

## Validation

- Validator CLI: `python tools/g0/validate_precedence_freshness.py` → **PASS** (precedence + freshness)
- Book 3 suite: 62 passed (50 prior + 12 new)

## Commits

- `G0-B3-C8-C9` chapter band.

## Status

PASS — source precedence and freshness are deterministic, fail-closed, and under test.