# G0-B5-C15 — Client Explanation Packet

## Purpose

Convert evidence/decision lineage into useful transparency for the client
without exposing internal chain-of-thought. The explanation cites structured
decision evidence — never hidden reasoning traces.

## Contract

`EvidenceExplanationPacket` (`schemas/g0/evidence/explanation_packet.schema.json`)
is derived from a `DecisionRecord` by `prototype/g0/evidence/explanation.py`
and validated by `tools/g0/validate_explanation_packet.py` against
`config/g0/evidence/explanation_policy.yaml`.

The packet carries:

- `decision_record_ref` — audit linkage back to the decision;
- `summary` — derived from the decision result;
- `cited_evidence_refs` — exactly the decision's inputs/outputs;
- `reason_codes`;
- `stale_indicators` — TOMBSTONED/INVALIDATED/SUPERSEDED/EXPIRED;
- `conflict_disclosures` — CONTRADICTS edges among cited refs;
- `assumptions` — rationale not traceable to decision inputs must be
  explicitly flagged or it is rejected.

## Rules (EXPL-001..005)

1. Every cited ref must be a decision input or output.
2. Unsupported rationale is rejected (or explicitly flagged ASSUMPTION).
3. Chain-of-thought never enters the packet.
4. Stale/invalidated inputs surface stale indicators; they are never cited
   as current.
5. Conflicts among cited refs are disclosed, never hidden.

Book 4's `ClientExplanationPacket` (B4.C10) remains the client-facing
adaptation layer; B5 packets feed it. Style/personalization may change
language, never the underlying factual anchors.
