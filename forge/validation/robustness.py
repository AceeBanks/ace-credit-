"""
GLX FORGE Validation Robustness

This module defines the robustness qualification for the GLX FORGE trading infrastructure.
Robustness qualification evaluates system resilience under stress conditions.

Version: 0.1.0
Phase: Phase 7 - Validation Forge
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Optional, Dict, List
from uuid import UUID, uuid4


class QualificationLevel(Enum):
    """Qualification level enumeration."""
    UNQUALIFIED = "unqualified"
    BRONZE = "bronze"
    SILVER = "silver"
    GOLD = "gold"
    PLATINUM = "platinum"


@dataclass
class RobustnessMetrics:
    """Robustness metrics contract."""
    total_return: float = 0.0
    sharpe_ratio: float = 0.0
    max_drawdown: float = 0.0
    win_rate: float = 0.0
    profit_factor: float = 0.0
    avg_trade_duration: float = 0.0
    volatility: float = 0.0
    recovery_time: float = 0.0
    
    @property
    def is_healthy(self) -> bool:
        """Check if metrics indicate healthy performance."""
        return (
            self.max_drawdown < 0.20 and
            self.sharpe_ratio > 0.5 and
            self.win_rate > 0.4
        )


@dataclass
class StressTestResult:
    """Stress test result contract."""
    test_id: str
    test_name: str
    scenario: str
    passed: bool
    metrics: RobustnessMetrics
    duration_seconds: float
    error: Optional[str] = None
    tested_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    
    def __post_init__(self):
        if not isinstance(self.test_id, str) or not self.test_id:
            self.test_id = str(uuid4())
        if not isinstance(self.test_name, str) or not self.test_name:
            raise ValueError("Test name cannot be empty")
        if not isinstance(self.scenario, str) or not self.scenario:
            raise ValueError("Scenario cannot be empty")


@dataclass
class RobustnessQualification:
    """Robustness qualification contract."""
    qualification_id: str
    target_id: str  # strategy_id, model_id, etc.
    level: QualificationLevel
    metrics: RobustnessMetrics
    stress_test_results: List[StressTestResult] = field(default_factory=list)
    qualified_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    expires_at: Optional[datetime] = None
    metadata: Dict = field(default_factory=dict)
    
    def __post_init__(self):
        if not isinstance(self.qualification_id, str) or not self.qualification_id:
            self.qualification_id = str(uuid4())
        if not isinstance(self.target_id, str) or not self.target_id:
            raise ValueError("Target ID cannot be empty")
        if not isinstance(self.level, QualificationLevel):
            raise ValueError("Level must be QualificationLevel enum")
    
    @property
    def is_qualified(self) -> bool:
        """Check if target is qualified."""
        return self.level != QualificationLevel.UNQUALIFIED
    
    @property
    def is_expired(self) -> bool:
        """Check if qualification is expired."""
        if self.expires_at is None:
            return False
        return datetime.now(timezone.utc) > self.expires_at
    
    @property
    def stress_test_pass_rate(self) -> float:
        """Get stress test pass rate."""
        if not self.stress_test_results:
            return 0.0
        passed = sum(1 for r in self.stress_test_results if r.passed)
        return passed / len(self.stress_test_results)
    
    def add_stress_test_result(self, result: StressTestResult) -> None:
        """Add a stress test result."""
        self.stress_test_results.append(result)


@dataclass
class RobustnessReport:
    """Robustness report contract."""
    report_id: str
    target_id: str
    qualification: RobustnessQualification
    summary: str
    recommendations: List[str] = field(default_factory=list)
    generated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    
    def __post_init__(self):
        if not isinstance(self.report_id, str) or not self.report_id:
            self.report_id = str(uuid4())
        if not isinstance(self.target_id, str) or not self.target_id:
            raise ValueError("Target ID cannot be empty")
        if not isinstance(self.qualification, RobustnessQualification):
            raise ValueError("Qualification must be a RobustnessQualification instance")
    
    @property
    def has_recommendations(self) -> bool:
        """Check if report has recommendations."""
        return len(self.recommendations) > 0
    
    def add_recommendation(self, recommendation: str) -> None:
        """Add a recommendation to the report."""
        self.recommendations.append(recommendation)


def determine_qualification_level(metrics: RobustnessMetrics, pass_rate: float) -> QualificationLevel:
    """Determine qualification level based on metrics and pass rate."""
    if pass_rate < 0.5:
        return QualificationLevel.UNQUALIFIED
    
    if metrics.sharpe_ratio >= 2.0 and metrics.max_drawdown < 0.05 and pass_rate >= 0.9:
        return QualificationLevel.PLATINUM
    
    if metrics.sharpe_ratio >= 1.5 and metrics.max_drawdown < 0.10 and pass_rate >= 0.8:
        return QualificationLevel.GOLD
    
    if metrics.sharpe_ratio >= 1.0 and metrics.max_drawdown < 0.15 and pass_rate >= 0.7:
        return QualificationLevel.SILVER
    
    if metrics.sharpe_ratio >= 0.5 and metrics.max_drawdown < 0.20 and pass_rate >= 0.6:
        return QualificationLevel.BRONZE
    
    return QualificationLevel.UNQUALIFIED


def create_robustness_metrics(
    total_return: float = 0.0,
    sharpe_ratio: float = 0.0,
    max_drawdown: float = 0.0,
    win_rate: float = 0.0,
) -> RobustnessMetrics:
    """Create robustness metrics."""
    return RobustnessMetrics(
        total_return=total_return,
        sharpe_ratio=sharpe_ratio,
        max_drawdown=max_drawdown,
        win_rate=win_rate,
    )


def create_stress_test_result(
    test_name: str,
    scenario: str,
    metrics: RobustnessMetrics,
    passed: bool,
    duration_seconds: float = 0.0,
) -> StressTestResult:
    """Create a stress test result."""
    return StressTestResult(
        test_id=str(uuid4()),
        test_name=test_name,
        scenario=scenario,
        passed=passed,
        metrics=metrics,
        duration_seconds=duration_seconds,
    )


def create_robustness_qualification(
    target_id: str,
    metrics: RobustnessMetrics,
    level: QualificationLevel = QualificationLevel.UNQUALIFIED,
) -> RobustnessQualification:
    """Create a robustness qualification."""
    return RobustnessQualification(
        qualification_id=str(uuid4()),
        target_id=target_id,
        level=level,
        metrics=metrics,
    )


def create_robustness_report(
    target_id: str,
    qualification: RobustnessQualification,
    summary: str,
) -> RobustnessReport:
    """Create a robustness report."""
    return RobustnessReport(
        report_id=str(uuid4()),
        target_id=target_id,
        qualification=qualification,
        summary=summary,
    )
