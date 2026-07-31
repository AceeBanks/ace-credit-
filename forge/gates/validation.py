"""
GLX FORGE Gate Validation

This module defines the gate validation system for the GLX FORGE trading infrastructure.
Gates define the rules and requirements for phase transitions.

Version: 0.1.0
Phase: Phase 1 - Forge Constitution
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Optional, List, Dict
from uuid import UUID, uuid4


class GateStatus(Enum):
    """Gate status enumeration."""
    PENDING = "pending"
    PASSED = "passed"
    FAILED = "failed"
    SKIPPED = "skipped"


@dataclass
class GateCondition:
    """Gate condition contract."""
    condition_id: str
    condition_type: str
    description: str
    required: bool = True
    blocking: bool = True
    
    def __post_init__(self):
        if not isinstance(self.condition_id, str) or not self.condition_id:
            self.condition_id = str(uuid4())
        if not isinstance(self.condition_type, str) or not self.condition_type:
            raise ValueError("Condition type cannot be empty")
        if not isinstance(self.description, str) or not self.description:
            raise ValueError("Description cannot be empty")


@dataclass
class GateResult:
    """Gate validation result."""
    gate_id: str
    gate_name: str
    status: GateStatus
    validated_at: datetime
    conditions_results: Dict[str, bool] = field(default_factory=dict)
    failure_reason: Optional[str] = None
    metadata: Dict = field(default_factory=dict)
    
    def __post_init__(self):
        if not isinstance(self.gate_id, str) or not self.gate_id:
            raise ValueError("Gate ID cannot be empty")
        if not isinstance(self.gate_name, str) or not self.gate_name:
            raise ValueError("Gate name cannot be empty")
        if not isinstance(self.status, GateStatus):
            raise ValueError("Status must be GateStatus enum")
    
    @property
    def passed(self) -> bool:
        """Check if gate passed."""
        return self.status == GateStatus.PASSED
    
    @property
    def failed(self) -> bool:
        """Check if gate failed."""
        return self.status == GateStatus.FAILED
    
    @property
    def is_blocking(self) -> bool:
        """Check if gate failure is blocking."""
        return self.failed and self.metadata.get("blocking", True)


@dataclass
class Gate:
    """Gate contract."""
    gate_id: str
    gate_name: str
    phase: str
    description: str
    conditions: List[GateCondition] = field(default_factory=list)
    required: bool = True
    blocking: bool = True
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    
    def __post_init__(self):
        if not isinstance(self.gate_id, str) or not self.gate_id:
            self.gate_id = str(uuid4())
        if not isinstance(self.gate_name, str) or not self.gate_name:
            raise ValueError("Gate name cannot be empty")
        if not isinstance(self.phase, str) or not self.phase:
            raise ValueError("Phase cannot be empty")
        if not isinstance(self.description, str) or not self.description:
            raise ValueError("Description cannot be empty")
    
    def validate(self, context: Dict) -> GateResult:
        """Validate this gate against a context."""
        conditions_results = {}
        all_required_passed = True
        
        for condition in self.conditions:
            # Evaluate condition (simplified - in real implementation would delegate to condition evaluator)
            condition_passed = self._evaluate_condition(condition, context)
            conditions_results[condition.condition_id] = condition_passed
            
            if condition.required and not condition_passed:
                all_required_passed = False
        
        status = GateStatus.PASSED if all_required_passed else GateStatus.FAILED
        
        return GateResult(
            gate_id=self.gate_id,
            gate_name=self.gate_name,
            status=status,
            validated_at=datetime.now(timezone.utc),
            conditions_results=conditions_results,
            failure_reason=None if all_required_passed else "Required conditions not met",
            metadata={"blocking": self.blocking},
        )
    
    def _evaluate_condition(self, condition: GateCondition, context: Dict) -> bool:
        """Evaluate a single condition (simplified)."""
        # In real implementation, this would delegate to specific condition evaluators
        # For now, return True if condition is satisfied in context
        return context.get(condition.condition_id, False)


# Default phase gates for the GLX FORGE system
DEFAULT_PHASE_GATES = {
    # Phase 0 gates
    "phase-00-inventory": Gate(
        gate_id="gate-phase-00-inventory",
        gate_name="Phase 0 Inventory Gate",
        phase="phase-00",
        description="Verify workspace inventory is complete",
        conditions=[
            GateCondition(
                condition_id="inventory_complete",
                condition_type="artifact",
                description="Repository fingerprint exists",
                required=True,
                blocking=True,
            ),
            GateCondition(
                condition_id="component_inventory_exists",
                condition_type="artifact",
                description="Core component inventory exists",
                required=True,
                blocking=True,
            ),
        ],
        required=True,
        blocking=True,
    ),
    
    "phase-00-baseline": Gate(
        gate_id="gate-phase-00-baseline",
        gate_name="Phase 0 Baseline Gate",
        phase="phase-00",
        description="Verify reproducible baseline is complete",
        conditions=[
            GateCondition(
                condition_id="environment_fingerprint_exists",
                condition_type="artifact",
                description="Environment fingerprint exists",
                required=True,
                blocking=True,
            ),
            GateCondition(
                condition_id="test_execution_passed",
                condition_type="test",
                description="Test execution passed",
                required=True,
                blocking=True,
            ),
            GateCondition(
                condition_id="baseline_report_exists",
                condition_type="artifact",
                description="Baseline report exists",
                required=True,
                blocking=True,
            ),
        ],
        required=True,
        blocking=True,
    ),
    
    "phase-00-classification": Gate(
        gate_id="gate-phase-00-classification",
        gate_name="Phase 0 Classification Gate",
        phase="phase-00",
        description="Verify component classification is complete",
        conditions=[
            GateCondition(
                condition_id="classification_exists",
                condition_type="artifact",
                description="Component classification exists",
                required=True,
                blocking=True,
            ),
        ],
        required=True,
        blocking=True,
    ),
    
    "phase-00-reality-lock": Gate(
        gate_id="gate-phase-00-reality-lock",
        gate_name="Phase 0 Reality Lock Gate",
        phase="phase-00",
        description="Verify reality lock is complete",
        conditions=[
            GateCondition(
                condition_id="reality_lock_exists",
                condition_type="artifact",
                description="Reality lock manifest exists",
                required=True,
                blocking=True,
            ),
            GateCondition(
                condition_id="decisions_approved",
                condition_type="approval",
                description="Reality lock decisions approved",
                required=True,
                blocking=True,
            ),
        ],
        required=True,
        blocking=True,
    ),
    
    # Phase 1 gates
    "phase-01-domain-language": Gate(
        gate_id="gate-phase-01-domain-language",
        gate_name="Phase 1 Domain Language Gate",
        phase="phase-01",
        description="Verify domain language is defined",
        conditions=[
            GateCondition(
                condition_id="types_defined",
                condition_type="artifact",
                description="Domain types are defined",
                required=True,
                blocking=True,
            ),
            GateCondition(
                condition_id="contracts_defined",
                condition_type="artifact",
                description="Domain contracts are defined",
                required=True,
                blocking=True,
            ),
            GateCondition(
                condition_id="schemas_defined",
                condition_type="artifact",
                description="Domain schemas are defined",
                required=True,
                blocking=True,
            ),
        ],
        required=True,
        blocking=True,
    ),
    
    "phase-01-event-contracts": Gate(
        gate_id="gate-phase-01-event-contracts",
        gate_name="Phase 1 Event Contracts Gate",
        phase="phase-01",
        description="Verify event contracts are defined",
        conditions=[
            GateCondition(
                condition_id="trading_events_defined",
                condition_type="artifact",
                description="Trading events are defined",
                required=True,
                blocking=True,
            ),
            GateCondition(
                condition_id="research_events_defined",
                condition_type="artifact",
                description="Research events are defined",
                required=True,
                blocking=True,
            ),
            GateCondition(
                condition_id="system_events_defined",
                condition_type="artifact",
                description="System events are defined",
                required=True,
                blocking=True,
            ),
        ],
        required=True,
        blocking=True,
    ),
    
    "phase-01-governance": Gate(
        gate_id="gate-phase-01-governance",
        gate_name="Phase 1 Governance Gate",
        phase="phase-01",
        description="Verify governance authority is defined",
        conditions=[
            GateCondition(
                condition_id="authority_defined",
                condition_type="artifact",
                description="Authority system is defined",
                required=True,
                blocking=True,
            ),
            GateCondition(
                condition_id="roles_defined",
                condition_type="artifact",
                description="Roles are defined",
                required=True,
                blocking=True,
            ),
            GateCondition(
                condition_id="policies_defined",
                condition_type="artifact",
                description="Policies are defined",
                required=True,
                blocking=True,
            ),
        ],
        required=True,
        blocking=True,
    ),
    
    "phase-01-gate-validation": Gate(
        gate_id="gate-phase-01-gate-validation",
        gate_name="Phase 1 Gate Validation Gate",
        phase="phase-01",
        description="Verify gate validation is defined",
        conditions=[
            GateCondition(
                condition_id="gates_defined",
                condition_type="artifact",
                description="Gates are defined",
                required=True,
                blocking=True,
            ),
            GateCondition(
                condition_id="conditions_defined",
                condition_type="artifact",
                description="Gate conditions are defined",
                required=True,
                blocking=True,
            ),
        ],
        required=True,
        blocking=True,
    ),
}


def validate_gate(gate_id: str, context: Dict) -> GateResult:
    """Validate a gate against a context."""
    gate = DEFAULT_PHASE_GATES.get(gate_id)
    if gate is None:
        raise ValueError(f"Gate not found: {gate_id}")
    return gate.validate(context)


def check_phase_transition(from_phase: str, to_phase: str, context: Dict) -> Dict[str, GateResult]:
    """Check all gates for a phase transition."""
    # Get all gates for the source phase
    phase_gates = {
        gate_id: gate for gate_id, gate in DEFAULT_PHASE_GATES.items()
        if gate.phase == from_phase
    }
    
    results = {}
    for gate_id, gate in phase_gates.items():
        results[gate_id] = validate_gate(gate_id, context)
    
    return results


def get_gate(gate_id: str) -> Gate:
    """Get a gate by ID."""
    gate = DEFAULT_PHASE_GATES.get(gate_id)
    if gate is None:
        raise ValueError(f"Gate not found: {gate_id}")
    return gate


def register_gate(gate: Gate) -> None:
    """Register a new gate."""
    DEFAULT_PHASE_GATES[gate.gate_id] = gate
