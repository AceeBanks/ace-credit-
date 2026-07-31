"""
GLX FORGE Portfolio Stress Controls

This module defines the stress controls for the GLX FORGE trading infrastructure.
Stress controls manage portfolio risk under extreme market conditions.

Version: 0.1.0
Phase: Phase 10 - Portfolio Forge
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Optional, Dict, List
from uuid import UUID, uuid4


class StressLevel(Enum):
    """Stress level enumeration."""
    NORMAL = "normal"
    ELEVATED = "elevated"
    HIGH = "high"
    SEVERE = "severe"
    CRITICAL = "critical"


@dataclass
class StressScenario:
    """Stress scenario contract."""
    scenario_id: str
    name: str
    description: str
    market_shock_pct: float
    volatility_multiplier: float
    liquidity_reduction_pct: float
    correlation_increase: float
    duration_hours: int
    metadata: Dict = field(default_factory=dict)
    
    def __post_init__(self):
        if not isinstance(self.scenario_id, str) or not self.scenario_id:
            self.scenario_id = str(uuid4())
        if not isinstance(self.name, str) or not self.name:
            raise ValueError("Name cannot be empty")
        if not isinstance(self.market_shock_pct, (int, float)):
            raise ValueError(f"Market shock must be numeric, got {type(self.market_shock_pct)}")


@dataclass
class StressResult:
    """Stress test result contract."""
    result_id: str
    scenario_id: str
    portfolio_id: str
    passed: bool
    portfolio_value_before: float
    portfolio_value_after: float
    loss_pct: float
    max_drawdown: float
    margin_requirement: float
    margin_available: float
    margin_call_risk: bool
    tested_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    
    def __post_init__(self):
        if not isinstance(self.result_id, str) or not self.result_id:
            self.result_id = str(uuid4())
        if not isinstance(self.scenario_id, str) or not self.scenario_id:
            raise ValueError("Scenario ID cannot be empty")
        if not isinstance(self.portfolio_id, str) or not self.portfolio_id:
            raise ValueError("Portfolio ID cannot be empty")
    
    @property
    def loss_amount(self) -> float:
        """Get loss amount."""
        return self.portfolio_value_before - self.portfolio_value_after
    
    @property
    def stress_level(self) -> StressLevel:
        """Determine stress level based on loss."""
        if self.loss_pct < 0.05:
            return StressLevel.NORMAL
        elif self.loss_pct < 0.10:
            return StressLevel.ELEVATED
        elif self.loss_pct < 0.20:
            return StressLevel.HIGH
        elif self.loss_pct < 0.30:
            return StressLevel.SEVERE
        return StressLevel.CRITICAL


@dataclass
class StressControl:
    """Stress control contract."""
    control_id: str
    name: str
    portfolio_id: str
    max_loss_pct: float = 0.10
    max_drawdown_pct: float = 0.15
    margin_requirement_pct: float = 0.50
    auto_reduce_on_stress: bool = True
    reduction_factor: float = 0.5
    enabled: bool = True
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    
    def __post_init__(self):
        if not isinstance(self.control_id, str) or not self.control_id:
            self.control_id = str(uuid4())
        if not isinstance(self.name, str) or not self.name:
            raise ValueError("Name cannot be empty")
        if not isinstance(self.portfolio_id, str) or not self.portfolio_id:
            raise ValueError("Portfolio ID cannot be empty")
        if not isinstance(self.max_loss_pct, (int, float)):
            raise ValueError(f"Max loss must be numeric, got {type(self.max_loss_pct)}")
        if not 0.0 <= self.max_loss_pct <= 1.0:
            raise ValueError(f"Max loss must be between 0.0 and 1.0, got {self.max_loss_pct}")
    
    @property
    def is_enabled(self) -> bool:
        """Check if control is enabled."""
        return self.enabled
    
    def should_reduce(self, loss_pct: float) -> bool:
        """Check if positions should be reduced."""
        if not self.auto_reduce_on_stress:
            return False
        return loss_pct >= self.max_loss_pct


@dataclass
class StressTest:
    """Stress test contract."""
    test_id: str
    name: str
    scenarios: List[StressScenario] = field(default_factory=list)
    results: List[StressResult] = field(default_factory=list)
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    
    def __post_init__(self):
        if not isinstance(self.test_id, str) or not self.test_id:
            self.test_id = str(uuid4())
        if not isinstance(self.name, str) or not self.name:
            raise ValueError("Name cannot be empty")
    
    def add_scenario(self, scenario: StressScenario) -> None:
        """Add a stress scenario."""
        self.scenarios.append(scenario)
    
    def add_result(self, result: StressResult) -> None:
        """Add a stress test result."""
        self.results.append(result)
    
    def run_scenario(
        self,
        scenario: StressScenario,
        portfolio_id: str,
        portfolio_value: float,
        portfolio_beta: float = 1.0,
    ) -> StressResult:
        """Run a stress scenario on a portfolio."""
        # Calculate portfolio value after shock
        loss_pct = abs(scenario.market_shock_pct) * portfolio_beta
        portfolio_value_after = portfolio_value * (1 - loss_pct)
        
        # Calculate margin requirements (simplified)
        margin_requirement = portfolio_value_after * 0.5
        margin_available = portfolio_value_after * 0.3
        margin_call_risk = margin_available < margin_requirement * 0.5
        
        result = StressResult(
            result_id=str(uuid4()),
            scenario_id=scenario.scenario_id,
            portfolio_id=portfolio_id,
            passed=loss_pct < 0.20,  # Pass if loss < 20%
            portfolio_value_before=portfolio_value,
            portfolio_value_after=portfolio_value_after,
            loss_pct=loss_pct,
            max_drawdown=loss_pct,
            margin_requirement=margin_requirement,
            margin_available=margin_available,
            margin_call_risk=margin_call_risk,
        )
        
        self.add_result(result)
        
        return result
    
    @property
    def scenario_count(self) -> int:
        """Get the number of scenarios."""
        return len(self.scenarios)
    
    @property
    def result_count(self) -> int:
        """Get the number of results."""
        return len(self.results)
    
    def get_worst_result(self) -> Optional[StressResult]:
        """Get the worst stress test result."""
        if not self.results:
            return None
        return max(self.results, key=lambda r: r.loss_pct)
    
    def get_pass_rate(self) -> float:
        """Get stress test pass rate."""
        if not self.results:
            return 0.0
        passed = sum(1 for r in self.results if r.passed)
        return passed / len(self.results)


def create_stress_scenario(
    name: str,
    market_shock_pct: float,
    volatility_multiplier: float = 2.0,
) -> StressScenario:
    """Create a new stress scenario."""
    return StressScenario(
        scenario_id=str(uuid4()),
        name=name,
        description=f"Market shock of {market_shock_pct:.1%}",
        market_shock_pct=market_shock_pct,
        volatility_multiplier=volatility_multiplier,
        liquidity_reduction_pct=0.5,
        correlation_increase=0.3,
        duration_hours=24,
    )


def create_stress_control(
    name: str,
    portfolio_id: str,
    max_loss_pct: float = 0.10,
) -> StressControl:
    """Create a new stress control."""
    return StressControl(
        control_id=str(uuid4()),
        name=name,
        portfolio_id=portfolio_id,
        max_loss_pct=max_loss_pct,
    )


def create_stress_test(name: str) -> StressTest:
    """Create a new stress test."""
    return StressTest(
        test_id=str(uuid4()),
        name=name,
    )
