"""
GLX FORGE Operations Incidents

This module defines the incident management for the GLX FORGE trading infrastructure.
Incident management handles operational incidents and responses.

Version: 0.1.0
Phase: Phase 11 - Sovereign Operations
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Optional, Dict, List
from uuid import UUID, uuid4


class IncidentSeverity(Enum):
    """Incident severity enumeration."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class IncidentStatus(Enum):
    """Incident status enumeration."""
    OPEN = "open"
    INVESTIGATING = "investigating"
    MITIGATED = "mitigated"
    RESOLVED = "resolved"
    CLOSED = "closed"


@dataclass
class IncidentAction:
    """Incident action contract."""
    action_id: str
    incident_id: str
    action_type: str  # "investigate", "mitigate", "resolve", "notify", etc.
    description: str
    performed_by: str
    performed_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    result: Optional[str] = None
    metadata: Dict = field(default_factory=dict)
    
    def __post_init__(self):
        if not isinstance(self.action_id, str) or not self.action_id:
            self.action_id = str(uuid4())
        if not isinstance(self.incident_id, str) or not self.incident_id:
            raise ValueError("Incident ID cannot be empty")
        if not isinstance(self.action_type, str) or not self.action_type:
            raise ValueError("Action type cannot be empty")
        if not isinstance(self.performed_by, str) or not self.performed_by:
            raise ValueError("Performed by cannot be empty")


@dataclass
class Incident:
    """Incident contract."""
    incident_id: str
    title: str
    description: str
    severity: IncidentSeverity
    status: IncidentStatus
    affected_components: List[str] = field(default_factory=list)
    actions: List[IncidentAction] = field(default_factory=list)
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: Optional[datetime] = None
    resolved_at: Optional[datetime] = None
    assigned_to: Optional[str] = None
    root_cause: Optional[str] = None
    metadata: Dict = field(default_factory=dict)
    
    def __post_init__(self):
        if not isinstance(self.incident_id, str) or not self.incident_id:
            self.incident_id = str(uuid4())
        if not isinstance(self.title, str) or not self.title:
            raise ValueError("Title cannot be empty")
        if not isinstance(self.description, str) or not self.description:
            raise ValueError("Description cannot be empty")
        if not isinstance(self.severity, IncidentSeverity):
            raise ValueError("Severity must be IncidentSeverity enum")
        if not isinstance(self.status, IncidentStatus):
            raise ValueError("Status must be IncidentStatus enum")
    
    @property
    def is_open(self) -> bool:
        """Check if incident is open."""
        return self.status in [IncidentStatus.OPEN, IncidentStatus.INVESTIGATING, IncidentStatus.MITIGATED]
    
    @property
    def is_resolved(self) -> bool:
        """Check if incident is resolved."""
        return self.status in [IncidentStatus.RESOLVED, IncidentStatus.CLOSED]
    
    @property
    def is_critical(self) -> bool:
        """Check if incident is critical."""
        return self.severity == IncidentSeverity.CRITICAL
    
    @property
    def duration(self) -> Optional[float]:
        """Get incident duration in seconds."""
        if self.resolved_at is None:
            return None
        return (self.resolved_at - self.created_at).total_seconds()
    
    @property
    def action_count(self) -> int:
        """Get the number of actions."""
        return len(self.actions)
    
    def assign(self, assignee: str) -> None:
        """Assign incident to a person."""
        self.assigned_to = assignee
        self.updated_at = datetime.now(timezone.utc)
    
    def investigate(self) -> None:
        """Mark incident as investigating."""
        self.status = IncidentStatus.INVESTIGATING
        self.updated_at = datetime.now(timezone.utc)
    
    def mitigate(self) -> None:
        """Mark incident as mitigated."""
        self.status = IncidentStatus.MITIGATED
        self.updated_at = datetime.now(timezone.utc)
    
    def resolve(self, root_cause: Optional[str] = None) -> None:
        """Resolve the incident."""
        self.status = IncidentStatus.RESOLVED
        self.resolved_at = datetime.now(timezone.utc)
        self.updated_at = datetime.now(timezone.utc)
        if root_cause:
            self.root_cause = root_cause
    
    def close(self) -> None:
        """Close the incident."""
        self.status = IncidentStatus.CLOSED
        self.updated_at = datetime.now(timezone.utc)
    
    def add_action(self, action: IncidentAction) -> None:
        """Add an action to the incident."""
        self.actions.append(action)
        self.updated_at = datetime.now(timezone.utc)


@dataclass
class IncidentReport:
    """Incident report contract."""
    report_id: str
    incident_id: str
    summary: str
    timeline: List[str] = field(default_factory=list)
    impact_assessment: str = ""
    lessons_learned: List[str] = field(default_factory=list)
    recommendations: List[str] = field(default_factory=list)
    generated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    
    def __post_init__(self):
        if not isinstance(self.report_id, str) or not self.report_id:
            self.report_id = str(uuid4())
        if not isinstance(self.incident_id, str) or not self.incident_id:
            raise ValueError("Incident ID cannot be empty")
    
    @property
    def has_recommendations(self) -> bool:
        """Check if report has recommendations."""
        return len(self.recommendations) > 0
    
    def add_timeline_event(self, event: str) -> None:
        """Add a timeline event."""
        self.timeline.append(event)
    
    def add_lesson_learned(self, lesson: str) -> None:
        """Add a lesson learned."""
        self.lessons_learned.append(lesson)
    
    def add_recommendation(self, recommendation: str) -> None:
        """Add a recommendation."""
        self.recommendations.append(recommendation)


@dataclass
class IncidentManager:
    """Incident manager contract."""
    manager_id: str
    name: str
    incidents: Dict[str, Incident] = field(default_factory=dict)
    reports: Dict[str, IncidentReport] = field(default_factory=dict)
    auto_escalation_enabled: bool = True
    escalation_rules: Dict[IncidentSeverity, int] = field(default_factory=dict)  # severity -> minutes
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    
    def __post_init__(self):
        if not isinstance(self.manager_id, str) or not self.manager_id:
            raise ValueError("Manager ID cannot be empty")
        if not isinstance(self.name, str) or not self.name:
            raise ValueError("Name cannot be empty")
        
        # Default escalation rules
        self.escalation_rules = {
            IncidentSeverity.LOW: 60 * 24,  # 24 hours
            IncidentSeverity.MEDIUM: 60 * 4,  # 4 hours
            IncidentSeverity.HIGH: 60,  # 1 hour
            IncidentSeverity.CRITICAL: 15,  # 15 minutes
        }
    
    def create_incident(
        self,
        title: str,
        description: str,
        severity: IncidentSeverity,
        affected_components: Optional[List[str]] = None,
    ) -> Incident:
        """Create a new incident."""
        incident = Incident(
            incident_id=str(uuid4()),
            title=title,
            description=description,
            severity=severity,
            status=IncidentStatus.OPEN,
            affected_components=affected_components or [],
        )
        
        self.incidents[incident.incident_id] = incident
        
        return incident
    
    def get_incident(self, incident_id: str) -> Optional[Incident]:
        """Get an incident by ID."""
        return self.incidents.get(incident_id)
    
    def get_incidents_by_severity(self, severity: IncidentSeverity) -> List[Incident]:
        """Get all incidents with a severity."""
        return [i for i in self.incidents.values() if i.severity == severity]
    
    def get_open_incidents(self) -> List[Incident]:
        """Get all open incidents."""
        return [i for i in self.incidents.values() if i.is_open]
    
    def get_critical_incidents(self) -> List[Incident]:
        """Get all critical incidents."""
        return [i for i in self.incidents.values() if i.is_critical]
    
    def generate_report(self, incident_id: str) -> Optional[IncidentReport]:
        """Generate an incident report."""
        incident = self.get_incident(incident_id)
        if incident is None:
            return None
        
        report = IncidentReport(
            report_id=str(uuid4()),
            incident_id=incident_id,
            summary=f"Incident: {incident.title} ({incident.severity.value})",
            impact_assessment=f"Affected components: {', '.join(incident.affected_components)}",
        )
        
        # Add timeline from actions
        for action in incident.actions:
            report.add_timeline_event(
                f"{action.performed_at.strftime('%Y-%m-%d %H:%M:%S')} - {action.action_type}: {action.description}"
            )
        
        self.reports[report.report_id] = report
        
        return report
    
    def check_escalation(self) -> List[Incident]:
        """Check for incidents that need escalation."""
        needs_escalation = []
        now = datetime.now(timezone.utc)
        
        for incident in self.incidents.values():
            if not incident.is_open:
                continue
            
            escalation_minutes = self.escalation_rules.get(incident.severity, 60)
            if (now - incident.created_at).total_seconds() > escalation_minutes * 60:
                needs_escalation.append(incident)
        
        return needs_escalation
    
    @property
    def incident_count(self) -> int:
        """Get the number of incidents."""
        return len(self.incidents)
    
    @property
    def open_incident_count(self) -> int:
        """Get the number of open incidents."""
        return len(self.get_open_incidents())
    
    @property
    def critical_incident_count(self) -> int:
        """Get the number of critical incidents."""
        return len(self.get_critical_incidents())


def create_incident_manager(name: str) -> IncidentManager:
    """Create a new incident manager."""
    return IncidentManager(
        manager_id=str(uuid4()),
        name=name,
    )


def create_incident(
    title: str,
    description: str,
    severity: IncidentSeverity,
) -> Incident:
    """Create a new incident."""
    return Incident(
        incident_id=str(uuid4()),
        title=title,
        description=description,
        severity=severity,
        status=IncidentStatus.OPEN,
    )


def create_incident_action(
    incident_id: str,
    action_type: str,
    description: str,
    performed_by: str,
) -> IncidentAction:
    """Create a new incident action."""
    return IncidentAction(
        action_id=str(uuid4()),
        incident_id=incident_id,
        action_type=action_type,
        description=description,
        performed_by=performed_by,
    )
