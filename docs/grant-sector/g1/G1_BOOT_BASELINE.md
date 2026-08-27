# G1 Production Implementation Baseline (G1-BOOT)

**Date:** 2026-08-27
**Branch:** `grant-sector-g1-production`
**Parent:** `grant-sector-r0-salvage`

## Baseline references

| Item | Reference |
|---|---|
| G0 source SHA | `84ebd8b9ac6aa6f377ab4ea02d08caa33d8f2ef9` (G0 final head) |
| G0 final Reality Lock | `docs/grant-sector/g0/00-ratification/G0_FINAL_REALITY_LOCK.json` (PASS, ready_for_g1=true, submission_enabled=false, p0_open=0) |
| G0 final external review | `docs/grant-sector/g0/00-ratification/G0_FINAL_EXTERNAL_REVIEW.md` (READY_FOR_EXTERNAL_RATIFICATION) |
| Appendix A | `docs/grant-sector/g1/G1_APPENDIX_A_MODEL_CAPABILITY_AND_SELECTION_CONTRACT_v1.0.md` |
| Appendix B | `docs/grant-sector/g1/G1_APPENDIX_B_CLIENT_INTERACTION_AND_FRONTEND_CONTRACT_v1.0.md` |
| G1 backlog | `docs/grant-sector/g0/09-production-seed/G0_B9_G1_IMPLEMENTATION_BACKLOG.md` |
| Runtime ADR | `docs/grant-sector/g0/09-production-seed/G0_B9_RUNTIME_SUBSTRATE_ADR.md` (OCE_NATIVE) |
| Clean seed | `production-seed/` (migrations, bootstrap, grant_platform package) |

## Prohibited actions (G1)

- Force push / rewrite historical G0 commits.
- Squash whole G1 waves into one commit.
- Mix unrelated waves in one commit.
- Work directly on `main`.
- Hide repairs.
- Enable automatic Grant submission (structurally disabled, all waves).
- Introduce a generic super-agent architecture.
- Redesign the product or rebuild proven G0 code unnecessarily.

## Planned milestone sequence

1. G1-W1 — durable platform kernel + persistence (G1.1+G1.2)
2. G1-W2 — real source connectivity + evidence (G1.3+G1.5)
3. G1-W3 — production Personal/CEO Hermes runtime (G1.6)
4. G1-W4 — full long-form Grant factory (G1.7+G1.8)
5. G1-W5 — client chat application (G1.9)
6. Pilot checkpoint — first end-to-end client-pilot simulation; STOP

## Promotion law

Per component, classify `PROMOTE_FROM_G0 | HARDEN_FROM_G0 |
REIMPLEMENT_PRODUCTION | NEW` against the authoritative G1 backlog. If
working G0 logic is reimplemented without need, document why.

## Commit: `G1-BOOT`
