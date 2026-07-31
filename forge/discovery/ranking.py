"""
GLX FORGE Discovery Ranking

This module defines the ranking system for the GLX FORGE trading infrastructure.
Ranking evaluates and ranks discoveries, strategies, and opportunities.

Version: 0.1.0
Phase: Phase 5 - Discovery Forge
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Optional, Dict, List, Callable, Any
from uuid import UUID, uuid4

from forge.discovery.contracts import DiscoveryResult


class RankingMethod(Enum):
    """Ranking method enumeration."""
    SCORE = "score"
    CONFIDENCE = "confidence"
    PROFIT_POTENTIAL = "profit_potential"
    RISK_REWARD = "risk_reward"
    SHARPE_RATIO = "sharpe_ratio"
    CUSTOM = "custom"


@dataclass
class RankingCriteria:
    """Ranking criteria contract."""
    criteria_id: str
    name: str
    weight: float  # 0.0 to 1.0
    ascending: bool = False  # False = higher is better
    min_value: Optional[float] = None
    max_value: Optional[float] = None
    metadata: Dict = field(default_factory=dict)
    
    def __post_init__(self):
        if not isinstance(self.criteria_id, str) or not self.criteria_id:
            self.criteria_id = str(uuid4())
        if not isinstance(self.name, str) or not self.name:
            raise ValueError("Name cannot be empty")
        if not isinstance(self.weight, (int, float)):
            raise ValueError(f"Weight must be numeric, got {type(self.weight)}")
        if not 0.0 <= self.weight <= 1.0:
            raise ValueError(f"Weight must be between 0.0 and 1.0, got {self.weight}")
    
    def normalize(self, value: float) -> float:
        """Normalize a value to 0-1 range."""
        if self.min_value is not None and self.max_value is not None:
            normalized = (value - self.min_value) / (self.max_value - self.min_value)
            return max(0.0, min(1.0, normalized))
        return value
    
    def score(self, value: float) -> float:
        """Calculate score for a value."""
        normalized = self.normalize(value)
        if not self.ascending:
            return normalized * self.weight
        return (1.0 - normalized) * self.weight


@dataclass
class RankedItem:
    """Ranked item contract."""
    item_id: str
    item_type: str  # "discovery", "strategy", "opportunity", etc.
    item_data: Dict
    score: float
    rank: int
    criteria_scores: Dict[str, float] = field(default_factory=dict)
    metadata: Dict = field(default_factory=dict)
    ranked_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    
    def __post_init__(self):
        if not isinstance(self.item_id, str) or not self.item_id:
            self.item_id = str(uuid4())
        if not isinstance(self.item_type, str) or not self.item_type:
            raise ValueError("Item type cannot be empty")
        if not isinstance(self.score, (int, float)):
            raise ValueError(f"Score must be numeric, got {type(self.score)}")
        if not isinstance(self.rank, int) or self.rank < 1:
            raise ValueError(f"Rank must be >= 1, got {self.rank}")
    
    @property
    def is_top_ranked(self) -> bool:
        """Check if item is top ranked (rank 1)."""
        return self.rank == 1
    
    @property
    def is_top_tier(self) -> bool:
        """Check if item is in top tier (rank 1-10)."""
        return self.rank <= 10


@dataclass
class RankingResult:
    """Ranking result contract."""
    result_id: str
    ranking_method: RankingMethod
    items: List[RankedItem] = field(default_factory=list)
    total_items: int = 0
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    metadata: Dict = field(default_factory=dict)
    
    def __post_init__(self):
        if not isinstance(self.result_id, str) or not self.result_id:
            self.result_id = str(uuid4())
        if not isinstance(self.ranking_method, RankingMethod):
            raise ValueError("Ranking method must be RankingMethod enum")
        self.total_items = len(self.items)
    
    @property
    def top_item(self) -> Optional[RankedItem]:
        """Get the top ranked item."""
        if not self.items:
            return None
        return self.items[0]
    
    @property
    def top_items(self, limit: int = 10) -> List[RankedItem]:
        """Get the top N ranked items."""
        return self.items[:limit]
    
    def get_item_by_rank(self, rank: int) -> Optional[RankedItem]:
        """Get an item by rank."""
        for item in self.items:
            if item.rank == rank:
                return item
        return None
    
    def get_items_by_score_range(self, min_score: float, max_score: float) -> List[RankedItem]:
        """Get items within a score range."""
        return [
            item for item in self.items
            if min_score <= item.score <= max_score
        ]


@dataclass
class RankingEngine:
    """Ranking engine contract."""
    engine_id: str
    name: str
    criteria: List[RankingCriteria] = field(default_factory=list)
    ranking_method: RankingMethod = RankingMethod.SCORE
    results: List[RankingResult] = field(default_factory=list)
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: Optional[datetime] = None
    
    def __post_init__(self):
        if not isinstance(self.engine_id, str) or not self.engine_id:
            self.engine_id = str(uuid4())
        if not isinstance(self.name, str) or not self.name:
            raise ValueError("Name cannot be empty")
        if not isinstance(self.ranking_method, RankingMethod):
            raise ValueError("Ranking method must be RankingMethod enum")
    
    def add_criteria(self, criteria: RankingCriteria) -> None:
        """Add a ranking criterion."""
        self.criteria.append(criteria)
        self.updated_at = datetime.now(timezone.utc)
    
    def remove_criteria(self, criteria_id: str) -> None:
        """Remove a ranking criterion."""
        self.criteria = [c for c in self.criteria if c.criteria_id != criteria_id]
        self.updated_at = datetime.now(timezone.utc)
    
    def get_criteria(self, criteria_id: str) -> Optional[RankingCriteria]:
        """Get a criterion by ID."""
        for criteria in self.criteria:
            if criteria.criteria_id == criteria_id:
                return criteria
        return None
    
    def rank_discoveries(self, discoveries: List[DiscoveryResult]) -> RankingResult:
        """Rank a list of discoveries."""
        ranked_items = []
        
        for i, discovery in enumerate(discoveries):
            # Calculate score based on criteria
            total_score = 0.0
            criteria_scores = {}
            
            for criterion in self.criteria:
                # Extract value from discovery metadata
                value = discovery.metadata.get(criterion.name, discovery.confidence)
                score = criterion.score(value)
                criteria_scores[criterion.name] = score
                total_score += score
            
            ranked_item = RankedItem(
                item_id=discovery.result_id,
                item_type="discovery",
                item_data={
                    "discovery_type": discovery.discovery_type.value,
                    "instrument_id": discovery.instrument_id,
                    "confidence": discovery.confidence,
                    "value": discovery.value,
                },
                score=total_score,
                rank=0,  # Will be set after sorting
                criteria_scores=criteria_scores,
            )
            ranked_items.append(ranked_item)
        
        # Sort by score (descending)
        ranked_items.sort(key=lambda x: x.score, reverse=True)
        
        # Assign ranks
        for i, item in enumerate(ranked_items):
            item.rank = i + 1
        
        result = RankingResult(
            result_id=str(uuid4()),
            ranking_method=self.ranking_method,
            items=ranked_items,
        )
        
        self.results.append(result)
        self.updated_at = datetime.now(timezone.utc)
        
        return result
    
    def rank_items(self, items: List[Dict], value_extractor: Callable[[Dict], float]) -> RankingResult:
        """Rank a list of items using a value extractor function."""
        ranked_items = []
        
        for i, item in enumerate(items):
            # Calculate score based on criteria
            total_score = 0.0
            criteria_scores = {}
            
            for criterion in self.criteria:
                value = value_extractor(item)
                score = criterion.score(value)
                criteria_scores[criterion.name] = score
                total_score += score
            
            ranked_item = RankedItem(
                item_id=str(uuid4()),
                item_type="custom",
                item_data=item,
                score=total_score,
                rank=0,  # Will be set after sorting
                criteria_scores=criteria_scores,
            )
            ranked_items.append(ranked_item)
        
        # Sort by score (descending)
        ranked_items.sort(key=lambda x: x.score, reverse=True)
        
        # Assign ranks
        for i, item in enumerate(ranked_items):
            item.rank = i + 1
        
        result = RankingResult(
            result_id=str(uuid4()),
            ranking_method=self.ranking_method,
            items=ranked_items,
        )
        
        self.results.append(result)
        self.updated_at = datetime.now(timezone.utc)
        
        return result
    
    @property
    def criteria_count(self) -> int:
        """Get the number of criteria."""
        return len(self.criteria)
    
    @property
    def result_count(self) -> int:
        """Get the number of ranking results."""
        return len(self.results)


def create_ranking_criteria(
    name: str,
    weight: float,
    ascending: bool = False,
    min_value: Optional[float] = None,
    max_value: Optional[float] = None,
) -> RankingCriteria:
    """Create a new ranking criterion."""
    return RankingCriteria(
        criteria_id=str(uuid4()),
        name=name,
        weight=weight,
        ascending=ascending,
        min_value=min_value,
        max_value=max_value,
    )


def create_ranking_engine(
    name: str,
    ranking_method: RankingMethod = RankingMethod.SCORE,
) -> RankingEngine:
    """Create a new ranking engine."""
    return RankingEngine(
        engine_id=str(uuid4()),
        name=name,
        ranking_method=ranking_method,
    )
