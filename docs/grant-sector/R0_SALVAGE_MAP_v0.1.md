# R0 Salvage Map

**Document ID:** GS-R0-MAP-001  
**Version:** 0.1  
**Status:** IN PROGRESS  
**Branch:** `grant-sector-r0-salvage`  
**Date:** 2026-08-24  

This file is the live component-level salvage ledger for the Grant Sector product. It will be expanded as branch archaeology proceeds.

## Disposition vocabulary

- ADOPT
- FORK
- WRAP
- PORT
- REWRITE
- REJECT
- DEFER

## Current priority candidates

| Capability | Source | Initial posture | Final disposition | Notes |
|---|---|---:|---:|---|
| Hermes context compaction | archived Hermes | high | TBD | Five-stage compaction pattern |
| Hermes sidechain/subagent manager | archived Hermes | very high | TBD | Parent summary + full sidechain audit |
| Hermes workflows | archived Hermes | medium-high | TBD | Useful scheduler/operator patterns |
| OCE-Hermes MCP facade | `hermes-set-up` | very high | TBD | Strong boundary/security foundation |
| OCE constitutional governance | OCE docs/main | very high | TBD | Control-plane doctrine |
| OCE Block 1 runtime/infrastructure patterns | OCE docs/main | very high | TBD | Postgres/Redis/workers/recovery |
| Generic agent/workflow tools | `main/tools` | high | TBD | Requires full inventory |

> This document is intentionally incomplete until the R0 deep dive finishes.
