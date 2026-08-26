"""B2.C17 Scenario COMMUNITY-1 — Georgia community statistic.

Geography/population/reference-period semantics preserved — never flattened
to a generic number.
"""
from __future__ import annotations

from decimal import Decimal

from prototype.g0.domain.models import StatisticObservation

COMMUNITY_1 = {
    "name": "COMMUNITY-1 Georgia community statistic",
    "statistic": StatisticObservation(
        stat_id="stat_ga_42",
        metric="county poverty rate",
        value=Decimal("18.2"),
        unit="percent",
        geography="county-121 (Dade County, GA)",
        reference_period="2023",
        population="all residents of Dade County, GA",
        dataset_version="ACS-5yr-2023",
        methodology="ACS 5-year estimates; MOE +/- 1.4",
    ),
}
