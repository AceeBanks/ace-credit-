"""
GLX FORGE System Events

This module defines system-related events for the GLX FORGE trading infrastructure.
System events represent service lifecycle, phase transitions, and gate validations.

Version: 0.1.0
Phase: Phase 1 - Forge Constitution
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Optional

from forge.domain.types import (
    Timestamp,
    validate_timestamp,
    ValidationError,
)


@dataclass(frozen=True)
class ServiceStarted:
    """Event emitted when a service starts."""
    event_id: str
    service_id: str
    service_type: str
    timestamp: Timestamp
    host: str
    port: Optional[int] = None
    version: Optional[str] = None
    
    def __post_init__(self):
        if not isinstance(self.event_id, str) or not self.event_id:
            raise ValidationError("Event ID cannot be empty")
        if not isinstance(self.service_id, str) or not self.service_id:
            raise ValidationError("Service ID cannot be empty")
        if not isinstance(self.service_type, str) or not self.service_type:
            raise ValidationError("Service type cannot be empty")
        if not isinstance(self.host, str) or not self.host:
            raise ValidationError("Host cannot be empty")
        self.timestamp = validate_timestamp(self.timestamp)


@dataclass(frozen=True)
class ServiceStopped:
    """Event emitted when a service stops."""
    event_id: str
    service_id: str
    service_type: str
    timestamp: Timestamp
    reason: Optional[str] = None
    exit_code: Optional[int] = None
    
    def __post_init__(self):
        if not isinstance(self.event_id, str) or not self.event_id:
            raise ValidationError("Event ID cannot be empty")
        if not isinstance(self.service_id, str) or not self.service_id:
            raise ValidationError("Service ID cannot be empty")
        if not isinstance(self.service_type, str) or not self.service_type:
            raise ValidationError("Service type cannot be empty")
        self.timestamp = validate_timestamp(self.timestamp)


@dataclass(frozen=True)
class ServiceError:
    """Event emitted when a service encounters an error."""
    event_id: str
    service_id: str
    service_type: str
    timestamp: Timestamp
    error: str
    error_type: Optional[str] = None
    error_code: Optional[str] = None
    severity: str = "error"  # "warning", "error", "critical"
    
    def __post_init__(self):
        if not isinstance(self.event_id, str) or not self.event_id:
            raise ValidationError("Event ID cannot be empty")
        if not isinstance(self.service_id, str) or not self.service_id:
            raise ValidationError("Service ID cannot be empty")
        if not isinstance(self.service_type, str) or not self.service_type:
            raise ValidationError("Service type cannot be empty")
        if not isinstance(self.error, str) or not self.error:
            raise ValidationError("Error message cannot be empty")
        if self.severity not in ["warning", "error", "critical"]:
            raise ValidationError(f"Severity must be 'warning', 'error', or 'critical', got {self.severity}")
        self.timestamp = validate_timestamp(self.timestamp)


@dataclass(frozen=True)
class PhaseTransitioned:
    """Event emitted when a phase transition occurs."""
    event_id: str
    from_phase: str
    to_phase: str
    timestamp: Timestamp
    transition_type: str  # "advance", "rollback", "skip"
    reason: Optional[str] = None
    approved_by: Optional[str] = None
    
    def __post_init__(self):
        if not isinstance(self.event_id, str) or not self.event_id:
            raise ValidationError("Event ID cannot be empty")
        if not isinstance(self.from_phase, str) or not self.from_phase:
            raise ValidationError("From phase cannot be empty")
        if not isinstance(self.to_phase, str) or not self.to_phase:
            raise ValidationError("To phase cannot be empty")
        if not isinstance(self.transition_type, str) or not self.transition_type:
            raise ValidationError("Transition type cannot be empty")
        if self.transition_type not in ["advance", "rollback", "skip"]:
            raise ValidationError(f"Transition type must be 'advance', 'rollback', or 'skip', got {self.transition_type}")
        self.timestamp = validate_timestamp(self.timestamp)


@dataclass(frozen=True)
class GateValidationPassed:
    """Event emitted when a gate validation passes."""
    event_id: str
    gate_id: str
    gate_name: str
    phase: str
    timestamp: Timestamp
    validation_results: dict = field(default_factory=dict)
    validated_by: Optional[str] = None
    
    def __post_init__(self):
        if not isinstance(self.event_id, str) or not self.event_id:
            raise ValidationError("Event ID cannot be empty")
        if not isinstance(self.gate_id, str) or not self.gate_id:
            raise ValidationError("Gate ID cannot be empty")
        if not isinstance(self.gate_name, str) or not self.gate_name:
            raise ValidationError("Gate name cannot be empty")
        if not isinstance(self.phase, str) or not self.phase:
            raise ValidationError("Phase cannot be empty")
        self.timestamp = validate_timestamp(self.timestamp)


@dataclass(frozen=True)
class GateValidationFailed:
    """Event emitted when a gate validation fails."""
    event_id: str
    gate_id: str
    gate_name: str
    phase: str
    timestamp: Timestamp
    failure_reason: str
    validation_results: dict = field(default_factory=dict)
    blocking: bool = True
    validated_by: Optional[str] = None
    
    def __post_init__(self):
        if not isinstance(self.event_id, str) or not self.event_id:
            raise ValidationError("Event ID cannot be empty")
        if not isinstance(self.gate_id, str) or not self.gate_id:
            raise ValidationError("Gate ID cannot be empty")
        if not isinstance(self.gate_name, str) or not self.gate_name:
            raise ValidationError("Gate name cannot be empty")
        if not isinstance(self.phase, str) or not self.phase:
            raise ValidationError("Phase cannot be empty")
        if not isinstance(self.failure_reason, str) or not self.failure_reason:
            raise ValidationError("Failure reason cannot be empty")
        self.timestamp = validate_timestamp(self.timestamp)
