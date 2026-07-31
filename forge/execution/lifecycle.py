"""
GLX FORGE Execution Lifecycle

This module defines the lifecycle management for the GLX FORGE trading infrastructure.
Lifecycle manages the state transitions of orders and executions.

Version: 0.1.0
Phase: Phase 9 - Execution Forge
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Optional, Dict, List, Callable
from uuid import UUID, uuid4

from forge.execution.contracts import ExecutionOrder, ExecutionStatus


class LifecycleState(Enum):
    """Lifecycle state enumeration."""
    CREATED = "created"
    VALIDATED = "validated"
    SUBMITTED = "submitted"
    ACKNOWLEDGED = "acknowledged"
    WORKING = "working"
    PARTIALLY_FILLED = "partially_filled"
    FILLED = "filled"
    CANCELLED = "cancelled"
    REJECTED = "rejected"
    EXPIRED = "expired"
    FAILED = "failed"
    CLOSED = "closed"


class LifecycleEventType(Enum):
    """Lifecycle event type enumeration."""
    CREATED = "created"
    VALIDATED = "validated"
    SUBMITTED = "submitted"
    ACKNOWLEDGED = "acknowledged"
    PARTIAL_FILL = "partial_fill"
    FILL = "fill"
    CANCEL_REQUESTED = "cancel_requested"
    CANCELLED = "cancelled"
    REJECTED = "rejected"
    EXPIRED = "expired"
    FAILED = "failed"


@dataclass
class LifecycleEvent:
    """Lifecycle event contract."""
    event_id: str
    order_id: str
    event_type: LifecycleEventType
    from_state: LifecycleState
    to_state: LifecycleState
    timestamp: datetime
    metadata: Dict = field(default_factory=dict)
    
    def __post_init__(self):
        if not isinstance(self.event_id, str) or not self.event_id:
            self.event_id = str(uuid4())
        if not isinstance(self.order_id, str) or not self.order_id:
            raise ValueError("Order ID cannot be empty")
        if not isinstance(self.event_type, LifecycleEventType):
            raise ValueError("Event type must be LifecycleEventType enum")
        if not isinstance(self.from_state, LifecycleState):
            raise ValueError("From state must be LifecycleState enum")
        if not isinstance(self.to_state, LifecycleState):
            raise ValueError("To state must be LifecycleState enum")


@dataclass
class ExecutionLifecycle:
    """Execution lifecycle contract."""
    lifecycle_id: str
    order_id: str
    current_state: LifecycleState
    events: List[LifecycleEvent] = field(default_factory=list)
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: Optional[datetime] = None
    
    def __post_init__(self):
        if not isinstance(self.lifecycle_id, str) or not self.lifecycle_id:
            self.lifecycle_id = str(uuid4())
        if not isinstance(self.order_id, str) or not self.order_id:
            raise ValueError("Order ID cannot be empty")
        if not isinstance(self.current_state, LifecycleState):
            raise ValueError("Current state must be LifecycleState enum")
    
    @property
    def is_terminal(self) -> bool:
        """Check if lifecycle is in terminal state."""
        return self.current_state in [
            LifecycleState.FILLED,
            LifecycleState.CANCELLED,
            LifecycleState.REJECTED,
            LifecycleState.EXPIRED,
            LifecycleState.FAILED,
            LifecycleState.CLOSED,
        ]
    
    @property
    def is_working(self) -> bool:
        """Check if lifecycle is in working state."""
        return self.current_state in [
            LifecycleState.SUBMITTED,
            LifecycleState.ACKNOWLEDGED,
            LifecycleState.WORKING,
            LifecycleState.PARTIALLY_FILLED,
        ]
    
    def transition_to(self, new_state: LifecycleState, event_type: LifecycleEventType, metadata: Optional[Dict] = None) -> None:
        """Transition to a new state."""
        event = LifecycleEvent(
            event_id=str(uuid4()),
            order_id=self.order_id,
            event_type=event_type,
            from_state=self.current_state,
            to_state=new_state,
            timestamp=datetime.now(timezone.utc),
            metadata=metadata or {},
        )
        
        self.events.append(event)
        self.current_state = new_state
        self.updated_at = datetime.now(timezone.utc)
    
    def get_events_by_type(self, event_type: LifecycleEventType) -> List[LifecycleEvent]:
        """Get events by type."""
        return [e for e in self.events if e.event_type == event_type]
    
    @property
    def event_count(self) -> int:
        """Get the number of events."""
        return len(self.events)
    
    @property
    def duration(self) -> Optional[float]:
        """Get lifecycle duration in seconds."""
        if self.updated_at is None:
            return None
        return (self.updated_at - self.created_at).total_seconds()


@dataclass
class LifecycleManager:
    """Lifecycle manager contract."""
    manager_id: str
    name: str
    lifecycles: Dict[str, ExecutionLifecycle] = field(default_factory=dict)
    state_transitions: Dict[LifecycleState, List[LifecycleState]] = field(default_factory=dict)
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    
    def __post_init__(self):
        if not isinstance(self.manager_id, str) or not self.manager_id:
            raise ValueError("Manager ID cannot be empty")
        if not isinstance(self.name, str) or not self.name:
            raise ValueError("Name cannot be empty")
        
        # Define valid state transitions
        self.state_transitions = {
            LifecycleState.CREATED: [LifecycleState.VALIDATED, LifecycleState.FAILED],
            LifecycleState.VALIDATED: [LifecycleState.SUBMITTED, LifecycleState.FAILED],
            LifecycleState.SUBMITTED: [LifecycleState.ACKNOWLEDGED, LifecycleState.REJECTED, LifecycleState.FAILED],
            LifecycleState.ACKNOWLEDGED: [LifecycleState.WORKING, LifecycleState.CANCELLED, LifecycleState.FAILED],
            LifecycleState.WORKING: [LifecycleState.PARTIALLY_FILLED, LifecycleState.FILLED, LifecycleState.CANCELLED, LifecycleState.EXPIRED, LifecycleState.FAILED],
            LifecycleState.PARTIALLY_FILLED: [LifecycleState.PARTIALLY_FILLED, LifecycleState.FILLED, LifecycleState.CANCELLED, LifecycleState.EXPIRED, LifecycleState.FAILED],
            LifecycleState.FILLED: [LifecycleState.CLOSED],
            LifecycleState.CANCELLED: [LifecycleState.CLOSED],
            LifecycleState.REJECTED: [LifecycleState.CLOSED],
            LifecycleState.EXPIRED: [LifecycleState.CLOSED],
            LifecycleState.FAILED: [LifecycleState.CLOSED],
            LifecycleState.CLOSED: [],
        }
    
    def create_lifecycle(self, order_id: str) -> ExecutionLifecycle:
        """Create a new lifecycle for an order."""
        lifecycle = ExecutionLifecycle(
            lifecycle_id=str(uuid4()),
            order_id=order_id,
            current_state=LifecycleState.CREATED,
        )
        
        # Add initial event
        lifecycle.transition_to(LifecycleState.CREATED, LifecycleEventType.CREATED)
        
        self.lifecycles[order_id] = lifecycle
        
        return lifecycle
    
    def get_lifecycle(self, order_id: str) -> Optional[ExecutionLifecycle]:
        """Get a lifecycle by order ID."""
        return self.lifecycles.get(order_id)
    
    def transition(self, order_id: str, new_state: LifecycleState, event_type: LifecycleEventType, metadata: Optional[Dict] = None) -> bool:
        """Transition a lifecycle to a new state."""
        lifecycle = self.get_lifecycle(order_id)
        if lifecycle is None:
            return False
        
        # Validate transition
        valid_transitions = self.state_transitions.get(lifecycle.current_state, [])
        if new_state not in valid_transitions:
            return False
        
        lifecycle.transition_to(new_state, event_type, metadata)
        return True
    
    def can_transition(self, order_id: str, new_state: LifecycleState) -> bool:
        """Check if a transition is valid."""
        lifecycle = self.get_lifecycle(order_id)
        if lifecycle is None:
            return False
        
        valid_transitions = self.state_transitions.get(lifecycle.current_state, [])
        return new_state in valid_transitions
    
    @property
    def lifecycle_count(self) -> int:
        """Get the number of lifecycles."""
        return len(self.lifecycles)
    
    def get_lifecycles_by_state(self, state: LifecycleState) -> List[ExecutionLifecycle]:
        """Get all lifecycles in a specific state."""
        return [l for l in self.lifecycles.values() if l.current_state == state]
    
    def get_terminal_lifecycles(self) -> List[ExecutionLifecycle]:
        """Get all terminal lifecycles."""
        return [l for l in self.lifecycles.values() if l.is_terminal]
    
    def get_working_lifecycles(self) -> List[ExecutionLifecycle]:
        """Get all working lifecycles."""
        return [l for l in self.lifecycles.values() if l.is_working]


def create_lifecycle_manager(name: str) -> LifecycleManager:
    """Create a new lifecycle manager."""
    return LifecycleManager(
        manager_id=str(uuid4()),
        name=name,
    )


def create_execution_lifecycle(order_id: str) -> ExecutionLifecycle:
    """Create a new execution lifecycle."""
    return ExecutionLifecycle(
        lifecycle_id=str(uuid4()),
        order_id=order_id,
        current_state=LifecycleState.CREATED,
    )
