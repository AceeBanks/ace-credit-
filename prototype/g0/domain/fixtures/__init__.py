"""G0 Book 2 — B2.C17 Georgia + Federal fixture architecture.

Fixtures are SEMANTIC EXAMPLES, not live adapters: Book 3 governs
SourceRegistry/Snapshot and G1 builds ingestion. Each scenario validates
against the derived domain schemas and relationship/state invariants
(see tests/g0/book2/test_fixtures.py).
"""
from __future__ import annotations

from prototype.g0.domain.fixtures.community import COMMUNITY_1
from prototype.g0.domain.fixtures.federal import AWARD_1, FED_1
from prototype.g0.domain.fixtures.georgia import GA_1

SCENARIOS = {
    "GA-1": GA_1,
    "FED-1": FED_1,
    "AWARD-1": AWARD_1,
    "COMMUNITY-1": COMMUNITY_1,
}
