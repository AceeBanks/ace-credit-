"""
GLX FORGE Validation Contracts

This module defines the validation contracts for the GLX FORGE trading infrastructure.
Validation contracts define the structure and criteria for validating strategies and systems.

Version: 0.1.0
Phase: Phase 7 - Validation Forge
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Optional, Dict, List, Any
from uuid import UUID, uuid4


class ValidationType(Enum):
    """Validation type enumeration."""
    STRATEGY = "strategy"
    DATA = "data"
    MODEL = "model"
    SYSTEM = "system"
    BACKTEST = "backtest"
    LIVE = "live"
    STRESS = "stress"
    REGRESSION = "regression"


class ValidationStatus(Enum):
    """Validation status enumeration."""
    PENDING = "pending"
    RUNNING = "running"
    PASSED = "passed"
    FAILED = "failed"
    WARNING = "warning"
    SKIPPED = "skipped"


@dataclass
class ValidationCriteria:
    """Validation criteria contract."""
    criteria_id: str
    name: str
    description: str
    threshold: float
    operator: str  # ">", "<", ">=", "<=", "==", "!="
    weight: float = 1.0  # 0.0 to 1.0
    required: bool = True
    metadata: Dict = field(default_factory=dict)
    
    def __post_init__(self):
        if not isinstance(self.criteria_id, str) or not self.criteria_id:
            self.criteria_id = str(uuid4())
        if not isinstance(self.name, str) or not self.name:
            raise ValueError("Name cannot be empty")
        if not isinstance(self.operator, str) or not self.operator:
            raise ValueError("Operator cannot be empty")
        if self.operator not in [">", "<", ">=", "<=", "==", "!="]:
            raise ValueError(f"Operator must be one of >, <, >=, <=, ==, !=, got {self.operator}")
        if not isinstance(self.weight, (int, float)):
            raise ValueError(f"Weight must be numeric, got {type(self.weight)}")
        if not 0.0 <= self.weight <= 1.0:
            raise ValueError(f"Weight must be between 0.0 and 1.0, got {self.weight}")
    
    def evaluate(self, value: float) -> bool:
        """Evaluate a value against this criterion."""
        if self.operator == ">":
            return value > self.threshold
        elif self.operator == "<":
            return value < self.threshold
        elif self.operator == ">=":
            return value >= self.threshold
        elif self.operator == "<=":
            return value <= self.threshold
        elif self.operator == "==":
            return value == self.threshold
        elif self.operator == "!=":
            return value != self.threshold
        return False


@dataclass
class ValidationResult:
    """Validation result contract."""
    result_id: str
    validation_type: ValidationType
    target_id: str  # strategy_id, model_id, etc.
    status: ValidationStatus
    criteria_results: Dict[str, bool] = field(default_factory=dict)
    score: float = 0.0  # 0.0 to 1.0
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    validated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    metadata: Dict = field(default_factory=dict)
    
    def __post_init__(self):
        if not isinstance(self.result_id, str) or not self.result_id:
            self.result_id = str(uuid4())
        if not isinstance(self.validation_type, ValidationType):
            raise ValueError("Validation type must be ValidationType enum")
        if not isinstance(self.target_id, str) or not self.target_id:
            raise ValueError("Target ID cannot be empty")
        if not isinstance(self.status, ValidationStatus):
            raise ValueError("Status must be ValidationStatus enum")
        if not isinstance(self.score, (int, float)):
            raise ValueError(f"Score must be numeric, got {type(self.score)}")
        if not 0.0 <= self.score <= 1.0:
            raise ValueError(f"Score must be between 0.0 and 1.0, got {self.score}")
    
    @property
    def is_passed(self) -> bool:
        """Check if validation passed."""
        return self.status == ValidationStatus.PASSED
    
    @property
    def is_failed(self) -> bool:
        """Check if validation failed."""
        return self.status == ValidationStatus.FAILED
    
    @property
    def has_errors(self) -> bool:
        """Check if validation has errors."""
        return len(self.errors) > 0
    
    @property
    def has_warnings(self) -> bool:
        """Check if validation has warnings."""
        return len(self.warnings) > 0
    
    @property
    def is_high_quality(self) -> bool:
        """Check if validation result is high quality."""
        return self.score >= 0.8
    
    def add_error(self, error: str) -> None:
        """Add an error to the result."""
        self.errors.append(error)
    
    def add_warning(self, warning: str) -> None:
        """Add a warning to the result."""
        self.warnings.append(warning)


@dataclass
class ValidationContract:
    """Validation contract contract."""
    contract_id: str
    contract_name: str
    validation_type: ValidationType
    criteria: List[ValidationCriteria] = field(default_factory=list)
    min_score: float = 0.7
    max_age_days: int = 30
    required: bool = True
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: Optional[datetime] = None
    
    def __post_init__(self):
        if not isinstance(self.contract_id, str) or not self.contract_id:
            self.contract_id = str(uuid4())
        if not isinstance(self.contract_name, str) or not self.contract_name:
            raise ValueError("Contract name cannot be empty")
        if not isinstance(self.validation_type, ValidationType):
            raise ValueError("Validation type must be ValidationType enum")
        if not isinstance(self.min_score, (int, float)):
            raise ValueError(f"Min score must be numeric, got {type(self.min_score)}")
        if not 0.0 <= self.min_score <= 1.0:
            raise ValueError(f"Min score must be between 0.0 and 1.0, got {self.min_score}")
    
    def add_criteria(self, criteria: ValidationCriteria) -> None:
        """Add a validation criterion."""
        self.criteria.append(criteria)
        self.updated_at = datetime.now(timezone.utc)
    
    def remove_criteria(self, criteria_id: str) -> None:
        """Remove a validation criterion."""
        self.criteria = [c for c in self.criteria if c.criteria_id != criteria_id]
        self.updated_at = datetime.now(timezone.utc)
    
    def get_criteria(self, criteria_id: str) -> Optional[ValidationCriteria]:
        """Get a criterion by ID."""
        for criteria in self.criteria:
            if criteria.criteria_id == criteria_id:
                return criteria
        return None
    
    def validate_result(self, result: ValidationResult) -> bool:
        """Validate a result against this contract."""
        if result.validation_type != self.validation_type:
            return False
        
        if result.score < self.min_score:
            return False
        
        # Check age
        age_days = (datetime.now(timezone.utc) - result.validated_at).days
        if age_days > self.max_age_days:
            return False
        
        return True


def create_validation_criteria(
    name: str,
    description: str,
    threshold: float,
    operator: str,
    weight: float = 1.0,
    required: bool = True,
) -> ValidationCriteria:
    """Create a new validation criterion."""
    return ValidationCriteria(
        criteria_id=str(uuid4()),
        name=name,
        description=description,
        threshold=threshold,
        operator=operator,
        weight=weight,
        required=required,
    )


def create_validation_result(
    validation_type: ValidationType,
    target_id: str,
) -> ValidationResult:
    """Create a new validation result."""
    return ValidationResult(
        result_id=str(uuid4()),
        validation_type=validation_type,
        target_id=target_id,
        status=ValidationStatus.PENDING,
    )


def create_validation_contract(
    contract_name: str,
    validation_type: ValidationType,
    min_score: float = 0.7,
) -> ValidationContract:
    """Create a new validation contract."""
    return ValidationContract(
        contract_id=str(uuid4()),
        contract_name=contract_name,
        validation_type=validation_type,
        min_score=min_score,
    )
