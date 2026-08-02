# QUANT LAB INFRA UPGRADE — Build Status

> **Recorded:** 2026-07-31
> **Updated:** 2026-08-02 (P0-REPAIR-01 truth-repair pass)
> **Canonical branch:** `main`
> **Program planning:** complete for Phases 0–11
> **Program implementation:** Phase 0 Book 1 Parts 1-4 implemented_unverified; Books 2-4 partial scaffolding
> **Live or capital authority:** none
> **P0-REPAIR-01:** Test counts reconciled, tools marked legacy/untrusted, fail-closed gates implemented

## Truth Snapshot

| Plane | Current state | Evidence |
|---|---|---|
| Design | Complete Phase 0–11 planning corpus | Master blueprint, final build guide, 12 phase READMEs, 58 books |
| Build | Phase 0 Book 1 Parts 1-4 implemented_unverified; Books 2-4 partial scaffolding (untrusted) | `tools/forge/phase0_inventory.py`, `phase0_trading_census.py`, `phase0_claims_secrets.py`, `phase0_book_gate.py` |
| Verification | Builder checks pass; independent review pending | 48 Phase 0 tests passing (actual test collection: Part 1: 10, Part 2: 10, Part 3: 9, Part 4: 8, environment: 9, extension: 2) |
| Operations | No FORGE production runtime has been certified | No Phase Lock or production authority artifact exists |

## Phase 0 Book 1 Status

| Part | Status | Tests | Evidence |
|---|---|---|---|
| Part 1 - Repository Fingerprint | implemented_unverified | 10/10 passing | repository-fingerprint.json, core-component-inventory.json |
| Part 2 - Trading Census | implemented_unverified | 10/10 passing | trading-file-census.json, dependency-inventory.json, data-inventory.json |
| Part 3 - Claims/Secrets/Contradictions | implemented_unverified | 9/9 passing | claims-secrets-inventory.json, contradictions-register.json |
| Part 4 - Canonical Merge & Book Gate | implemented_unverified | 8/8 passing | workspace-inventory.json, book-gate-record.json |
| Environment Fingerprint | implemented_unverified | 9/9 passing | environment-fingerprint.json |
| Extension Documentation | implemented_unverified | 2/2 passing | extension validation |

**Total Phase 0 Tests:** 48/48 passing (actual test collection)  
**Independent Review:** Pending for all parts

## Phase 0 Books 2-4 Status

| Book | Status | Progress |
|---|---|---|
| Book 2 - Reproducible Baseline | partial_scaffolding_untrusted | Environment fingerprinting complete (9/9 tests); test discovery, bounded execution, service readiness, backtest reproduction have partial scaffolding; tools marked legacy/untrusted per P0-REPAIR-01 |
| Book 3 - Component Classification | partial_scaffolding_untrusted | Classification tool exists but violates strict rules (name-based classification); marked legacy/untrusted per P0-REPAIR-01; requires evidence-based reimplementation |
| Book 4 - Reality Lock | partial_scaffolding_untrusted | Reality Lock tool exists but hardcodes completion as true; repaired to fail-closed per P0-REPAIR-01; requires evidence validation before use |

**P0-REPAIR-01 Tool Status:**
- `phase0_baseline_report.py`: LEGACY/UNTRUSTED - test counts need reconciliation
- `phase0_classification.py`: LEGACY/UNTRUSTED - name-based classification violates rules
- `phase0_reality_lock.py`: REPAIRED - now fails closed with evidence validation
- `phase0_bounded_execution.py`: REPAIRED - shell=True replaced with allowlist + shell=False

**Safe Defaults Applied:**
- Canonical branch: main (master is legacy/reference)
- NautilusTrader: pinned upstream dependency (vendored source quarantined)
- MT5 MCP: experimental/quarantined
- Agent authority: deny by default
- Classification: strict (supporting/quarantined until verified)
- Quarantine: targeted and enforceable
- Canonical path map: one canonical per function
- Service readiness: verify only canonical/current services

**Contradiction Analysis Status:**
- 1,345 heuristic triage candidates (NOT MAD decisions)
- Requires evidence-backed cluster analysis before MAD review
- Heuristic pattern matching only, not validated contradictions
- See `material-contradictions-mad-review.md` for details

Do not describe Phase 0, Book 2, Book 3, or Book 4 as complete or locked.

## Implemented Slice

Phase 0, Book 1, Part 1 currently provides:

- a sanitized Git repository fingerprint;
- bounded identities for dirty and untracked worktree files;
- explicit generated-output exclusion to prevent recursive fingerprint drift;
- mid-scan repository mutation detection;
- required component presence or absence records;
- deterministic core-component and entrypoint discovery;
- machine-readable Part 1 evidence manifests.

Current builder evidence from this checkout:

- 48 Phase 0 tests passing (actual test collection: Part 1: 10, Part 2: 10, Part 3: 9, Part 4: 8, environment: 9, extension: 2);
- 15 of 15 required component paths present;
- 376 entrypoints mapped to one component each;
- zero truncated component scans;
- consecutive repository and component fingerprints reproduce;
- zero credential-shaped matches in generated Part 1 artifacts;
- zero final validation errors.

Generated artifacts are checkout-bound evidence under `artifacts/forge/phase-00/book-01-part-01/`. Regenerate them after any commit or worktree change; do not treat an older artifact as current merely because it exists.

## Exact Verification Commands

```bash
python3 -m compileall -q tools/forge tests/forge

python3 -m tools.forge.validate_extension_docs --root .

python3 -m pytest tests/forge/phase_00/ -v

python3 -m tools.forge.phase0_inventory \
  --root . \
  --output-dir artifacts/forge/phase-00/book-01-part-01
```

The collector intentionally reports `implemented_unverified`; it cannot approve its own independent-review gate.

## P0-REPAIR-01 Status (2026-08-02)

**Completed Repairs:**
1. ✅ Test count reconciliation: 48/48 actual tests (not 49/49)
2. ✅ Legacy tool marking: phase0_baseline_report.py, phase0_classification.py marked untrusted
3. ✅ Fail-closed Reality Lock: phase0_reality_lock.py now validates evidence before allowing phase transition
4. ✅ MT5 inventory correction: Cerebus_Symmetry_OptionB.mq5 documented as external MQL5 candidate (not Pine)
5. ✅ Contradiction reclassification: 1,345 heuristic candidates (not MAD decisions)
6. ✅ Bounded execution safety: shell=True replaced with allowlist + shell=False

**Remaining Work:**
- Evidence-based classification implementation (Book 3)
- Actual Nautilus fixture reproduction (Book 2)
- Evidence-backed contradiction cluster analysis
- Independent review of all Phase 0 artifacts

## Next Planned Slice

Phase 0, Book 1, Part 2 is [Trading Census, Dependencies, and Data Metadata](implementation/phase-00/book-1/part-02-trading-dependencies-data.md).

Its bounded deliverables are:

- `trading-file-census.json`;
- `dependency-inventory.json`;
- `data-inventory.json`;
- tests for bounded metadata collection, stable ownership references, and explicit unknowns.

Part 2 must not classify operational fitness, install dependencies, execute a broker path, load entire large datasets, or change legacy trading files.

## Gate State

| Scope | State | Blocking condition |
|---|---|---|
| Phase 0 Book 1 Part 1 | `implemented_unverified` | Independent review not yet recorded |
| Phase 0 Book 1 Parts 2–4 | `implemented_unverified` | Independent review not yet recorded |
| Phase 0 Book 2 | `partial_scaffolding_untrusted` | Legacy tools marked; requires evidence-based implementation |
| Phase 0 Book 3 | `partial_scaffolding_untrusted` | Classification violates rules; requires evidence-based reimplementation |
| Phase 0 Book 4 | `partial_scaffolding_untrusted` | Reality Lock repaired to fail-closed; requires evidence validation |
| Phase 0 Reality Lock | `blocked` | Books 2-4 incomplete; untrusted tools; no evidence validation |
| Phases 1–11 | `planned` | Approved Phase 0 Reality Lock absent |

## Environment Notes

- The inventory implementation uses the Python standard library.
- Static Python compilation passed for `tools/forge`, `tests/forge`, `srrs_opc`, and the OCE backend/test trees.
- The 48 Phase 0 tests executed and passed in the local environment (pytest collection).
- No missing dependency was installed merely to change a blocked result into a pass.
- Docker and Podman were not available in the current hosted test environment.
- No live, paper, sandbox, MT5, exchange, or broker action was run.
- A later local machine run is still required for machine-specific engines and dependencies that are unavailable here.
