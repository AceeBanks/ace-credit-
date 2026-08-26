# G0 Book 0 — B0.C3 Contradiction & Drift Ledger

**Chapter:** B0.C3 — Contradiction & Drift Sweep
**Status:** IMPLEMENTED — ZERO UNRESOLVED P0
**Machine-readable source of truth:** `config/g0/ratification/contradiction_ledger.yaml`
**Validator:** `tools/g0/validate_contradictions.py`

## WHAT

Deliberate contradiction scan across all pinned R0/G0 artifacts, covering the ten
mandated probes from the Book 0 plan plus one standing drift doctrine. Each entry
records both claims, both sources, severity, resolution, resolution authority, and
affected decision IDs.

## WHY

The authority order requires contradictions to be resolved explicitly (supersession
or decision), never silently. This ledger is the durable proof that the sweep
happened and how each conflict closed.

## AUTHORITY

Book 0 master prompt §B0.C3. Historical documents are not edited to remove
conflicts (implementation requirement 6.4); resolutions supersede via this ledger.

## LEDGER SUMMARY

| ID | Title | Severity | Status | Closed by |
|---|---|---|---|---|
| CD-001 | California-first vs Georgia-first | P1 | RESOLVED | Amendment 001 supersedes |
| CD-002 | Drafting at Book 8 vs early D0/D1 milestones | P1 | RESOLVED | Amendment 001 |
| CD-003 | Submission exclusion vs reachable external channels | **P0** | RESOLVED | Structural: capability layer dominates tools; Book 1 lock proves disabled |
| CD-004 | Semantica "foundational" vs bake-off mandate | P1 | RESOLVED | PROTOTYPE_REQUIRED downgrade |
| CD-005 | Treg pattern value vs license restriction | P1 | RESOLVED | Pattern/independent impl + code REJECTED split |
| CD-006 | Graph projection vs canonical DB sovereignty | P1 | RESOLVED | Sovereignty invariant absolute |
| CD-007 | Redis transport vs accepted-job durability | P1 | RESOLVED | Postgres stores intent first |
| CD-008 | Shared memory vs Personal/CEO isolation | **P0** | RESOLVED | Separate namespaces binding |
| CD-009 | Transcripts in parent context vs sidechain isolation | P1 | RESOLVED | Sidechain binding |
| CD-010 | Framework convenience vs bounded-component sovereignty | **P0** | RESOLVED | Policy layer dominates framework config |
| CD-011 | Historical test counts vs current-proof standard | P2 | RESOLVED | Re-run doctrine (drift) |

## INVARIANTS (validator-enforced, fail-closed)

- unique contradiction IDs, known severity/status enums;
- both claims cite artifact IDs that resolve to the pinned manifest;
- every affected decision exists in the decision register;
- **gate:** any OPEN P0 fails validation outright.

## FAILURE MODE

Validator exits non-zero on an unresolved P0 or any lineage defect. The Book 0
Reality Lock consumes `open_p0` from this validator — it cannot be asserted PASS
while the ledger holds an open critical contradiction.

## TEST

`tests/g0/book0/test_contradictions.py` — live-ledger pass plus adversarial
fixtures: injected OPEN P0 must fail the gate, phantom sources must fail,
unknown enums and phantom decision links must fail.

## HANDOFF

Book 1 inherits three structural obligations from the P0 closures:
CD-003 (submission disabled provable from registry/policy), CD-008 (memory
namespaces keyed by actor identity), CD-010 (no framework config may authorize).
