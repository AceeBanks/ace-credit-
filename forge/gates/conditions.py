"""
GLX FORGE Gate Conditions

This module defines the condition types for the GLX FORGE gate validation system.
Conditions define the specific checks that gates perform.

Version: 0.1.0
Phase: Phase 1 - Forge Constitution
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Optional, Dict, Any
from uuid import UUID, uuid4


class ConditionType(Enum):
    """Condition type enumeration."""
    ARTIFACT = "artifact"
    TEST = "test"
    POLICY = "policy"
    APPROVAL = "approval"
    CONFIGURATION = "configuration"
    DEPENDENCY = "dependency"


@dataclass
class ArtifactCondition:
    """Artifact condition contract."""
    condition_id: str
    artifact_path: str
    artifact_type: str
    description: str
    required: bool = True
    exists: bool = False
    
    def __post_init__(self):
        if not isinstance(self.condition_id, str) or not self.condition_id:
            self.condition_id = str(uuid4())
        if not isinstance(self.artifact_path, str) or not self.artifact_path:
            raise ValueError("Artifact path cannot be empty")
        if not isinstance(self.artifact_type, str) or not self.artifact_type:
            raise ValueError("Artifact type cannot be empty")
    
    def evaluate(self, repo_root: Path) -> bool:
        """Evaluate this artifact condition."""
        artifact_file = repo_root / self.artifact_path
        self.exists = artifact_file.exists()
        return self.exists


@dataclass
class TestCondition:
    """Test condition contract."""
    condition_id: str
    test_path: str
    test_pattern: str
    description: str
    required: bool = True
    min_pass_rate: float = 1.0
    
    def __post_init__(self):
        if not isinstance(self.condition_id, str) or not self.condition_id:
            self.condition_id = str(uuid4())
        if not isinstance(self.test_path, str) or not self.test_path:
            raise ValueError("Test path cannot be empty")
        if not isinstance(self.test_pattern, str) or not self.test_pattern:
            raise ValueError("Test pattern cannot be empty")
        if not isinstance(self.min_pass_rate, (int, float)):
            raise ValueError("Min pass rate must be numeric")
        if not 0.0 <= self.min_pass_rate <= 1.0:
            raise ValueError("Min pass rate must be between 0.0 and 1.0")
    
    def evaluate(self, repo_root: Path) -> bool:
        """Evaluate this test condition (simplified)."""
        # In real implementation, this would run tests and check pass rate
        # For now, return True if test directory exists
        test_dir = repo_root / self.test_path
        return test_dir.exists()


@dataclass
class PolicyCondition:
    """Policy condition contract."""
    condition_id: str
    policy_id: str
    policy_type: str
    description: str
    required: bool = True
    expected_effect: str = "allow"
    
    def __post_init__(self):
        if not isinstance(self.condition_id, str) or not self.condition_id:
            self.condition_id = str(uuid4())
        if not isinstance(self.policy_id, str) or not self.policy_id:
            raise ValueError("Policy ID cannot be empty")
        if not isinstance(self.policy_type, str) or not self.policy_type:
            raise ValueError("Policy type cannot be empty")
    
    def evaluate(self, context: Dict[str, Any]) -> bool:
        """Evaluate this policy condition."""
        # In real implementation, this would check policy evaluation
        # For now, return True if policy exists in context
        return self.policy_id in context.get("policies", {})


@dataclass
class ApprovalCondition:
    """Approval condition contract."""
    condition_id: str
    approval_type: str
    required_approver: str
    description: str
    required: bool = True
    
    def __post_init__(self):
        if not isinstance(self.condition_id, str) or not self.condition_id:
            self.condition_id = str(uuid4())
        if not isinstance(self.approval_type, str) or not self.approval_type:
            raise ValueError("Approval type cannot be empty")
        if not isinstance(self.required_approver, str) or not self.required_approver:
            raise ValueError("Required approver cannot be empty")
    
    def evaluate(self, context: Dict[str, Any]) -> bool:
        """Evaluate this approval condition."""
        # Check if approval exists in context
        approvals = context.get("approvals", {})
        approval = approvals.get(self.approval_type)
        
        if approval is None:
            return False
        
        # Check if approved by required approver
        return approval.get("approver") == self.required_approver and approval.get("status") == "approved"


def evaluate_condition(condition: Any, repo_root: Path, context: Optional[Dict[str, Any]] = None) -> bool:
    """Evaluate a condition based on its type."""
    context = context or {}
    
    if isinstance(condition, ArtifactCondition):
        return condition.evaluate(repo_root)
    elif isinstance(condition, TestCondition):
        return condition.evaluate(repo_root)
    elif isinstance(condition, PolicyCondition):
        return condition.evaluate(context)
    elif isinstance(condition, ApprovalCondition):
        return condition.evaluate(context)
    else:
        raise ValueError(f"Unknown condition type: {type(condition)}")


# Default conditions for common gate checks
DEFAULT_CONDITIONS = {
    # Artifact conditions
    "repository_fingerprint_exists": ArtifactCondition(
        condition_id="cond-repo-fingerprint",
        artifact_path="artifacts/forge/phase-00/repository-fingerprint.json",
        artifact_type="json",
        description="Repository fingerprint artifact exists",
        required=True,
    ),
    
    "environment_fingerprint_exists": ArtifactCondition(
        condition_id="cond-env-fingerprint",
        artifact_path="artifacts/forge/phase-00/environment-fingerprint.json",
        artifact_type="json",
        description="Environment fingerprint artifact exists",
        required=True,
    ),
    
    "baseline_report_exists": ArtifactCondition(
        condition_id="cond-baseline-report",
        artifact_path="artifacts/forge/phase-00/baseline-report.json",
        artifact_type="json",
        description="Baseline report artifact exists",
        required=True,
    ),
    
    "classification_exists": ArtifactCondition(
        condition_id="cond-classification",
        artifact_path="artifacts/forge/phase-00/component-classification.json",
        artifact_type="json",
        description="Component classification artifact exists",
        required=True,
    ),
    
    "reality_lock_exists": ArtifactCondition(
        condition_id="cond-reality-lock",
        artifact_path="artifacts/forge/phase-00/reality-lock-manifest.json",
        artifact_type="json",
        description="Reality lock manifest artifact exists",
        required=True,
    ),
    
    # Test conditions
    "phase_00_tests_pass": TestCondition(
        condition_id="cond-phase-00-tests",
        test_path="tests/forge",
        test_pattern="test_*.py",
        description="Phase 0 tests pass",
        required=True,
        min_pass_rate=1.0,
    ),
    
    # Approval conditions
    "reality_lock_approved": ApprovalCondition(
        condition_id="cond-reality-lock-approval",
        approval_type="reality_lock",
        required_approver="admin",
        description="Reality lock approved by administrator",
        required=True,
    ),
}
