# G0 Plan Amendment Register

**Document ID:** GS-G0-AMD-REG-001  
**Version:** 1.0  
**Status:** ACTIVE  
**Date:** 2026-08-25

This register lists planning amendments that modify implementation priorities or candidate bake-offs without silently rewriting previously authored master plans.

| Amendment | Status | Scope | Effect |
|---|---|---|---|
| `G0_BLUEPRINT_AMENDMENT_001_GEORGIA_FIRST_EARLY_DRAFTING.md` | ACTIVE | Books 1–4, 8 | Georgia-first state proof; D0/D1 early drafting milestones |
| `G0_AMENDMENT_002_RUNTIME_AND_COMPONENT_BAKEOFF_DISCIPLINE_v1.0.md` | ACTIVE | Books 3,4,6,7,8,9 | Adds only bounded external component bake-offs; freezes anti-pollution/runtime-selection rules |

## Amendment precedence

Amendments may refine implementation candidates, sequencing, fixtures, or explicit extension points. They may not silently weaken Book 1 constitutional laws or Book 0 ratified decisions.

If an amendment conflicts with a ratified constitutional invariant, the constitutional invariant prevails until a formal constitutional amendment is approved.

## Execution-agent rule

When executing a Book, the agent must read:

1. the Book master implementation plan;
2. all ACTIVE amendments whose scope includes that Book;
3. prior ratified Books and ADRs.

The agent must treat the active amendment as a narrow overlay, not permission to expand scope beyond the Book mission.
