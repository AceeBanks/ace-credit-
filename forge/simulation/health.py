"""
GLX FORGE Simulation Health

This module defines the health monitoring for the GLX FORGE trading infrastructure.
Health monitor tracks system health metrics and alerts.

Version: 0.1.0
Phase: Phase 8 - Simulation Forge
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Optional, Dict, List
from uuid import UUID, uuid4


class HealthStatus(Enum):
    """Health status enumeration."""
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"
    CRITICAL = "critical"
    UNKNOWN = "unknown"


@dataclass
class HealthMetric:
    """Health metric contract."""
    metric_id: str
    name: str
    value: float
    unit: str
    threshold_warning: Optional[float] = None
    threshold_critical: Optional[float] = None
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    metadata: Dict = field(default_factory=dict)
    
    def __post_init__(self):
        if not isinstance(self.metric_id, str) or not self.metric_id:
            self.metric_id = str(uuid4())
        if not isinstance(self.name, str) or not self.name:
            raise ValueError("Name cannot be empty")
    
    @property
    def status(self) -> HealthStatus:
        """Get health status based on thresholds."""
        if self.threshold_critical is not None and self.value >= self.threshold_critical:
            return HealthStatus.CRITICAL
        if self.threshold_warning is not None and self.value >= self.threshold_warning:
            return HealthStatus.DEGRADED
        return HealthStatus.HEALTHY


@dataclass
class HealthAlert:
    """Health alert contract."""
    alert_id: str
    metric_id: str
    severity: str  # "warning", "critical"
    message: str
    value: float
    threshold: float
    triggered_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    resolved_at: Optional[datetime] = None
    
    def __post_init__(self):
        if not isinstance(self.alert_id, str) or not self.alert_id:
            self.alert_id = str(uuid4())
        if not isinstance(self.metric_id, str) or not self.metric_id:
            raise ValueError("Metric ID cannot be empty")
        if not isinstance(self.severity, str) or not self.severity:
            raise ValueError("Severity cannot be empty")
        if self.severity not in ["warning", "critical"]:
            raise ValueError(f"Severity must be 'warning' or 'critical', got {self.severity}")
    
    @property
    def is_resolved(self) -> bool:
        """Check if alert is resolved."""
        return self.resolved_at is not None
    
    def resolve(self) -> None:
        """Resolve the alert."""
        self.resolved_at = datetime.now(timezone.utc)


@dataclass
class HealthMonitor:
    """Health monitor contract."""
    monitor_id: str
    name: str
    metrics: Dict[str, HealthMetric] = field(default_factory=dict)
    alerts: List[HealthAlert] = field(default_factory=list)
    check_interval: int = 30
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    
    def __post_init__(self):
        if not isinstance(self.monitor_id, str) or not self.monitor_id:
            raise ValueError("Monitor ID cannot be empty")
        if not isinstance(self.name, str) or not self.name:
            raise ValueError("Name cannot be empty")
    
    def add_metric(self, metric: HealthMetric) -> None:
        """Add a health metric."""
        self.metrics[metric.metric_id] = metric
    
    def remove_metric(self, metric_id: str) -> None:
        """Remove a health metric."""
        if metric_id in self.metrics:
            del self.metrics[metric_id]
    
    def get_metric(self, metric_id: str) -> Optional[HealthMetric]:
        """Get a metric by ID."""
        return self.metrics.get(metric_id)
    
    def update_metric(self, metric_id: str, value: float) -> None:
        """Update a metric value."""
        metric = self.get_metric(metric_id)
        if metric:
            metric.value = value
            metric.timestamp = datetime.now(timezone.utc)
            
            # Check for alerts
            self._check_alerts(metric)
    
    def _check_alerts(self, metric: HealthMetric) -> None:
        """Check if metric should trigger alerts."""
        if metric.threshold_critical is not None and metric.value >= metric.threshold_critical:
            alert = HealthAlert(
                alert_id=str(uuid4()),
                metric_id=metric.metric_id,
                severity="critical",
                message=f"Critical threshold exceeded for {metric.name}",
                value=metric.value,
                threshold=metric.threshold_critical,
            )
            self.alerts.append(alert)
        elif metric.threshold_warning is not None and metric.value >= metric.threshold_warning:
            alert = HealthAlert(
                alert_id=str(uuid4()),
                metric_id=metric.metric_id,
                severity="warning",
                message=f"Warning threshold exceeded for {metric.name}",
                value=metric.value,
                threshold=metric.threshold_warning,
            )
            self.alerts.append(alert)
    
    def get_overall_status(self) -> HealthStatus:
        """Get overall health status."""
        if not self.metrics:
            return HealthStatus.UNKNOWN
        
        statuses = [m.status for m in self.metrics.values()]
        
        if HealthStatus.CRITICAL in statuses:
            return HealthStatus.CRITICAL
        if HealthStatus.DEGRADED in statuses:
            return HealthStatus.DEGRADED
        if HealthStatus.UNHEALTHY in statuses:
            return HealthStatus.UNHEALTHY
        return HealthStatus.HEALTHY
    
    @property
    def metric_count(self) -> int:
        """Get the number of metrics."""
        return len(self.metrics)
    
    @property
    def alert_count(self) -> int:
        """Get the number of active alerts."""
        return len([a for a in self.alerts if not a.is_resolved])
    
    @property
    def critical_alert_count(self) -> int:
        """Get the number of critical alerts."""
        return len([a for a in self.alerts if a.severity == "critical" and not a.is_resolved])


# Default health metrics for common system components
DEFAULT_HEALTH_METRICS = {
    "cpu_usage": HealthMetric(
        metric_id="metric-cpu-usage",
        name="CPU Usage",
        value=0.0,
        unit="%",
        threshold_warning=70.0,
        threshold_critical=90.0,
    ),
    
    "memory_usage": HealthMetric(
        metric_id="metric-memory-usage",
        name="Memory Usage",
        value=0.0,
        unit="%",
        threshold_warning=80.0,
        threshold_critical=95.0,
    ),
    
    "disk_usage": HealthMetric(
        metric_id="metric-disk-usage",
        name="Disk Usage",
        value=0.0,
        unit="%",
        threshold_warning=80.0,
        threshold_critical=90.0,
    ),
    
    "latency": HealthMetric(
        metric_id="metric-latency",
        name="Latency",
        value=0.0,
        unit="ms",
        threshold_warning=100.0,
        threshold_critical=500.0,
    ),
    
    "error_rate": HealthMetric(
        metric_id="metric-error-rate",
        name="Error Rate",
        value=0.0,
        unit="%",
        threshold_warning=1.0,
        threshold_critical=5.0,
    ),
}


def create_health_monitor(name: str, check_interval: int = 30) -> HealthMonitor:
    """Create a new health monitor."""
    return HealthMonitor(
        monitor_id=str(uuid4()),
        name=name,
        check_interval=check_interval,
    )


def create_health_metric(
    name: str,
    value: float,
    unit: str,
    threshold_warning: Optional[float] = None,
    threshold_critical: Optional[float] = None,
) -> HealthMetric:
    """Create a new health metric."""
    return HealthMetric(
        metric_id=str(uuid4()),
        name=name,
        value=value,
        unit=unit,
        threshold_warning=threshold_warning,
        threshold_critical=threshold_critical,
    )
