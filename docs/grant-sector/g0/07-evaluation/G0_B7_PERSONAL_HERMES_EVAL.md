# G0-B7-C11 — Personal Hermes Evaluation

**Document ID:** GS-G0-B7-C11-PH
**Status:** RATIFIED (Book 7 chapter C11)
**Engine:** `prototype/g0/evaluation/agent_eval.py::personal_hermes_eval`

Personal Hermes is evaluated for relationship/intake quality, not CEO
execution depth. A "warmer personality" cannot compensate for wrong intent
translation.

## Core behaviors measured

- captures user intent accurately (valid typed IntentContract)
- asks only necessary questions (unnecessary-question rate)
- uses existing canonical profile before re-asking
- preserves user preferences/decisions appropriately
- distinguishes idea exploration from authorized work request
- produces valid IntentContract
- does not perform CEO-only operations (L1 ceiling)
- communicates uncertainty clearly
- explains outcomes using governed ExplanationPacket
- avoids cross-project/client contamination (hard fail)

## Longitudinal tests

Multi-session continuity with cold reconstruction and preference updates
(see C14 memory/context eval). Personal is never rewarded for CEO work.
