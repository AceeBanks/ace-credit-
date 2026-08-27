"""G1 Wave 5 — client API (apps/api).

Chat-first API surface per Appendix B. FastAPI with the durable Store
(SQLite dev/CI; Postgres adapter swaps in). Every route is tenant-scoped;
every model selection goes through the governed registry contract from
Appendix A; submission remains structurally disabled.

Start:  uvicorn apps.api.main:app --reload
Test:   python -m pytest apps/api/tests -q
"""
