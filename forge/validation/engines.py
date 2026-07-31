"""
GLX FORGE Validation Engines

This module defines the validation engines for the GLX FORGE trading infrastructure.
Engines execute validation tests against strategies, models, and systems.

Version: 0.1.0
Phase: Phase 7 - Validation Forge
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Optional, Dict, List, Callable, Any
from uuid import UUID, uuid4

from forge.validation.contracts import ValidationCriteria, ValidationResult, ValidationType


class EngineType(Enum):
    """Engine type enumeration."""
    BACKTEST = "backtest"
    LIVE = "live"
    STRESS = "stress"
    REGRESSION = "regression"
    DATA_QUALITY = "data_quality"
    MODEL_VALIDATION = "model_validation"
    SYSTEM_HEALTH = "system_health"
    CUSTOM = "custom"


@dataclass
class EngineConfig:
    """Engine configuration contract."""
    engine_id: str
    engine_type: EngineType
    timeout_seconds: int = 300
    max_retries: int = 3
    parallel: bool = False
    log_level: str = "INFO"
    metadata: Dict = field(default_factory=dict)
    
    def __post_init__(self):
        if not isinstance(self.engine_id, str) or not self.engine_id:
            raise ValueError("Engine ID cannot be empty")
        if not isinstance(self.engine_type, EngineType):
            raise ValueError("Engine type must be EngineType enum")
        if not isinstance(self.timeout_seconds, int) or self.timeout_seconds < 1:
            raise ValueError(f"Timeout must be >= 1, got {self.timeout_seconds}")


@dataclass
class ValidationTest:
    """Validation test contract."""
    test_id: str
    name: str
    description: str
    criteria: List[ValidationCriteria] = field(default_factory=list)
    test_function: Optional[Callable] = None
    enabled: bool = True
    metadata: Dict = field(default_factory=dict)
    
    def __post_init__(self):
        if not isinstance(self.test_id, str) or not self.test_id:
            self.test_id = str(uuid4())
        if not isinstance(self.name, str) or not self.name:
            raise ValueError("Name cannot be empty")
    
    def add_criteria(self, criteria: ValidationCriteria) -> None:
        """Add a criterion to the test."""
        self.criteria.append(criteria)
    
    def execute(self, context: Dict) -> Dict[str, bool]:
        """Execute the test and return criteria results."""
        results = {}
        
        if self.test_function is not None:
            try:
                test_result = self.test_function(context)
                for criteria in self.criteria:
                    results[criteria.criteria_id] = criteria.evaluate(test_result)
            except Exception as e:
                for criteria in self.criteria:
                    results[criteria.criteria_id] = False
        else:
            # Default: all criteria pass if no test function
            for criteria in self.criteria:
                results[criteria.criteria_id] = True
        
        return results


@dataclass
class TestResult:
    """Test result contract."""
    result_id: str
    test_id: str
    passed: bool
    score: float
    duration_seconds: float
    criteria_results: Dict[str, bool] = field(default_factory=dict)
    error: Optional[str] = None
    executed_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    
    def __post_init__(self):
        if not isinstance(self.result_id, str) or not self.result_id:
            self.result_id = str(uuid4())
        if not isinstance(self.test_id, str) or not self.test_id:
            raise ValueError("Test ID cannot be empty")
        if not isinstance(self.score, (int, float)):
            raise ValueError(f"Score must be numeric, got {type(self.score)}")
        if not 0.0 <= self.score <= 1.0:
            raise ValueError(f"Score must be between 0.0 and 1.0, got {self.score}")


@dataclass
class ValidationEngine:
    """Validation engine contract."""
    engine_id: str
    name: str
    engine_type: EngineType
    config: EngineConfig
    tests: Dict[str, ValidationTest] = field(default_factory=dict)
    results: List[TestResult] = field(default_factory=list)
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    
    def __post_init__(self):
        if not isinstance(self.engine_id, str) or not self.engine_id:
            raise ValueError("Engine ID cannot be empty")
        if not isinstance(self.name, str) or not self.name:
            raise ValueError("Name cannot be empty")
        if not isinstance(self.engine_type, EngineType):
            raise ValueError("Engine type must be EngineType enum")
        if not isinstance(self.config, EngineConfig):
            raise ValueError("Config must be an EngineConfig instance")
    
    def add_test(self, test: ValidationTest) -> None:
        """Add a test to the engine."""
        self.tests[test.test_id] = test
    
    def remove_test(self, test_id: str) -> None:
        """Remove a test from the engine."""
        if test_id in self.tests:
            del self.tests[test_id]
    
    def get_test(self, test_id: str) -> Optional[ValidationTest]:
        """Get a test by ID."""
        return self.tests.get(test_id)
    
    def execute_test(self, test_id: str, context: Dict) -> TestResult:
        """Execute a single test."""
        test = self.get_test(test_id)
        if test is None:
            raise ValueError(f"Test not found: {test_id}")
        
        if not test.enabled:
            return TestResult(
                result_id=str(uuid4()),
                test_id=test_id,
                passed=True,
                score=1.0,
                duration_seconds=0.0,
            )
        
        start_time = datetime.now(timezone.utc)
        
        try:
            criteria_results = test.execute(context)
            
            # Calculate score based on criteria results
            total_weight = sum(c.weight for c in test.criteria)
            if total_weight == 0:
                score = 1.0
            else:
                passed_weight = sum(
                    c.weight for c in test.criteria
                    if criteria_results.get(c.criteria_id, False)
                )
                score = passed_weight / total_weight
            
            passed = score >= 0.7  # Default threshold
            
            duration = (datetime.now(timezone.utc) - start_time).total_seconds()
            
            result = TestResult(
                result_id=str(uuid4()),
                test_id=test_id,
                passed=passed,
                score=score,
                duration_seconds=duration,
                criteria_results=criteria_results,
            )
            
            self.results.append(result)
            
            return result
        except Exception as e:
            duration = (datetime.now(timezone.utc) - start_time).total_seconds()
            
            result = TestResult(
                result_id=str(uuid4()),
                test_id=test_id,
                passed=False,
                score=0.0,
                duration_seconds=duration,
                error=str(e),
            )
            
            self.results.append(result)
            
            return result
    
    def execute_all_tests(self, context: Dict) -> List[TestResult]:
        """Execute all tests in the engine."""
        results = []
        for test_id in self.tests:
            result = self.execute_test(test_id, context)
            results.append(result)
        return results
    
    @property
    def test_count(self) -> int:
        """Get the number of tests."""
        return len(self.tests)
    
    @property
    def result_count(self) -> int:
        """Get the number of results."""
        return len(self.results)
    
    def get_pass_rate(self) -> float:
        """Get the pass rate of all executed tests."""
        if not self.results:
            return 0.0
        passed = sum(1 for r in self.results if r.passed)
        return passed / len(self.results)


# Default validation engines for common validation types
DEFAULT_ENGINES = {
    "backtest": ValidationEngine(
        engine_id="engine-backtest",
        name="Backtest Validation Engine",
        engine_type=EngineType.BACKTEST,
        config=EngineConfig(
            engine_id="engine-backtest",
            engine_type=EngineType.BACKTEST,
            timeout_seconds=600,
        ),
    ),
    
    "stress": ValidationEngine(
        engine_id="engine-stress",
        name="Stress Testing Engine",
        engine_type=EngineType.STRESS,
        config=EngineConfig(
            engine_id="engine-stress",
            engine_type=EngineType.STRESS,
            timeout_seconds=1200,
        ),
    ),
    
    "data_quality": ValidationEngine(
        engine_id="engine-data-quality",
        name="Data Quality Validation Engine",
        engine_type=EngineType.DATA_QUALITY,
        config=EngineConfig(
            engine_id="engine-data-quality",
            engine_type=EngineType.DATA_QUALITY,
            timeout_seconds=300,
        ),
    ),
    
    "model_validation": ValidationEngine(
        engine_id="engine-model-validation",
        name="Model Validation Engine",
        engine_type=EngineType.MODEL_VALIDATION,
        config=EngineConfig(
            engine_id="engine-model-validation",
            engine_type=EngineType.MODEL_VALIDATION,
            timeout_seconds=600,
        ),
    ),
}


def create_validation_engine(
    name: str,
    engine_type: EngineType,
    config: Optional[EngineConfig] = None,
) -> ValidationEngine:
    """Create a new validation engine."""
    if config is None:
        config = EngineConfig(
            engine_id=str(uuid4()),
            engine_type=engine_type,
        )
    
    return ValidationEngine(
        engine_id=config.engine_id,
        name=name,
        engine_type=engine_type,
        config=config,
    )


def create_validation_test(
    name: str,
    description: str,
    test_function: Optional[Callable] = None,
) -> ValidationTest:
    """Create a new validation test."""
    return ValidationTest(
        test_id=str(uuid4()),
        name=name,
        description=description,
        test_function=test_function,
    )
