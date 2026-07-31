"""
GLX FORGE Validation Forge

This module defines the validation infrastructure for the GLX FORGE trading infrastructure.
Validation includes contracts, engines, and robustness qualification.

Version: 0.1.0
Phase: Phase 7 - Validation Forge
"""

__version__ = "0.1.0"

from forge.validation.contracts import (
    ValidationContract,
    ValidationType,
    ValidationStatus,
    ValidationCriteria,
    ValidationResult,
)

from forge.validation.engines import (
    ValidationEngine,
    EngineType,
    EngineConfig,
    ValidationTest,
    TestResult,
    DEFAULT_ENGINES,
)

from forge.validation.robustness import (
    RobustnessQualification,
    RobustnessMetrics,
    StressTestResult,
    QualificationLevel,
    RobustnessReport,
)

__all__ = [
    # Contracts
    "ValidationContract",
    "ValidationType",
    "ValidationStatus",
    "ValidationCriteria",
    "ValidationResult",
    # Engines
    "ValidationEngine",
    "EngineType",
    "EngineConfig",
    "ValidationTest",
    "TestResult",
    "DEFAULT_ENGINES",
    # Robustness
    "RobustnessQualification",
    "RobustnessMetrics",
    "StressTestResult",
    "QualificationLevel",
    "RobustnessReport",
]
