"""
GLX FORGE Gate Validation

This module defines the gate validation system for the GLX FORGE trading infrastructure.
Gates define the rules and requirements for phase transitions.

Version: 0.1.0
Phase: Phase 1 - Forge Constitution
"""

__version__ = "0.1.0"

from forge.gates.validation import (
    Gate,
    GateStatus,
    GateResult,
    GateCondition,
    validate_gate,
    check_phase_transition,
    DEFAULT_PHASE_GATES,
    get_gate,
    register_gate,
)

from forge.gates.conditions import (
    ConditionType,
    ArtifactCondition,
    TestCondition,
    PolicyCondition,
    ApprovalCondition,
    evaluate_condition,
)

__all__ = [
    # Validation
    "Gate",
    "GateStatus",
    "GateResult",
    "GateCondition",
    "validate_gate",
    "check_phase_transition",
    "DEFAULT_PHASE_GATES",
    "get_gate",
    "register_gate",
    # Conditions
    "ConditionType",
    "ArtifactCondition",
    "TestCondition",
    "PolicyCondition",
    "ApprovalCondition",
    "evaluate_condition",
]
