# G0 Book 5 — Graph Projection Contract

**Chapter:** B5.C12 · **Schema:** `graph_projection_event.schema.json`

## Rules

- PROJ-001 — graph node ids derive from internal canonical ids;
- PROJ-002 — projection is rebuildable;
- PROJ-003 — graph-only mutation cannot create canonical facts;
- PROJ-004 — canonical changes propagate through projection events;
- PROJ-005 — projection lag is measurable;
- PROJ-006 — graph deletion cannot erase canonical history;
- PROJ-007 — schema/version mapping is explicit.

## Exit test (EXIT-001)

Delete the graph projection and rebuild it from canonical state/evidence
without semantic loss. If impossible, the graph has become sovereign and
Book 5 fails. Proven in `tests/g0/book5/test_graph_projection.py`.
