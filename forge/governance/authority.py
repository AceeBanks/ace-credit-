"""
GLX FORGE Governance Authority

This module defines the authority system for the GLX FORGE trading infrastructure.
Authority defines who can approve what actions and changes.

Version: 0.1.0
Phase: Phase 1 - Forge Constitution
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Optional, Set
from uuid import UUID, uuid4


class AuthorityLevel(Enum):
    """Authority level enumeration."""
    NONE = "none"
    READ = "read"
    WRITE = "write"
    APPROVE = "approve"
    ADMIN = "admin"


class ApprovalStatus(Enum):
    """Approval status enumeration."""
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    CANCELLED = "cancelled"


@dataclass(frozen=True)
class Permission:
    """Permission contract."""
    resource: str  # Resource identifier (e.g., "phase:advance", "strategy:deploy")
    action: str  # Action identifier (e.g., "read", "write", "approve")
    authority_level: AuthorityLevel
    
    def __post_init__(self):
        if not isinstance(self.resource, str) or not self.resource:
            raise ValueError("Resource cannot be empty")
        if not isinstance(self.action, str) or not self.action:
            raise ValueError("Action cannot be empty")
        if not isinstance(self.authority_level, AuthorityLevel):
            raise ValueError("Authority level must be AuthorityLevel enum")
    
    @property
    def key(self) -> str:
        """Unique permission key."""
        return f"{self.resource}:{self.action}"


@dataclass
class Approval:
    """Approval contract."""
    approval_id: str
    requester: str
    approver: Optional[str]
    permission: Permission
    status: ApprovalStatus
    requested_at: datetime
    reviewed_at: Optional[datetime] = None
    reason: Optional[str] = None
    metadata: dict = field(default_factory=dict)
    
    def __post_init__(self):
        if not isinstance(self.approval_id, str) or not self.approval_id:
            self.approval_id = str(uuid4())
        if not isinstance(self.requester, str) or not self.requester:
            raise ValueError("Requester cannot be empty")
        if not isinstance(self.permission, Permission):
            raise ValueError("Permission must be a Permission instance")
        if not isinstance(self.status, ApprovalStatus):
            raise ValueError("Status must be ApprovalStatus enum")
    
    @property
    def is_approved(self) -> bool:
        """Check if approval is approved."""
        return self.status == ApprovalStatus.APPROVED
    
    @property
    def is_pending(self) -> bool:
        """Check if approval is pending."""
        return self.status == ApprovalStatus.PENDING
    
    @property
    def is_rejected(self) -> bool:
        """Check if approval is rejected."""
        return self.status == ApprovalStatus.REJECTED


@dataclass
class Authority:
    """Authority contract."""
    authority_id: str
    name: str
    permissions: Set[Permission] = field(default_factory=set)
    authority_level: AuthorityLevel = AuthorityLevel.READ
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    
    def __post_init__(self):
        if not isinstance(self.authority_id, str) or not self.authority_id:
            self.authority_id = str(uuid4())
        if not isinstance(self.name, str) or not self.name:
            raise ValueError("Name cannot be empty")
        if not isinstance(self.authority_level, AuthorityLevel):
            raise ValueError("Authority level must be AuthorityLevel enum")
    
    def has_permission(self, resource: str, action: str) -> bool:
        """Check if authority has a specific permission."""
        permission_key = f"{resource}:{action}"
        return any(p.key == permission_key for p in self.permissions)
    
    def grant_permission(self, permission: Permission) -> None:
        """Grant a permission to this authority."""
        if not isinstance(permission, Permission):
            raise ValueError("Permission must be a Permission instance")
        self.permissions.add(permission)
    
    def revoke_permission(self, resource: str, action: str) -> None:
        """Revoke a permission from this authority."""
        permission_key = f"{resource}:{action}"
        self.permissions = {p for p in self.permissions if p.key != permission_key}
    
    def can_approve(self, permission: Permission) -> bool:
        """Check if this authority can approve a permission."""
        if not isinstance(permission, Permission):
            return False
        
        # Authority must have higher or equal authority level
        if self.authority_level.value < permission.authority_level.value:
            return False
        
        # Authority must have the permission itself
        return self.has_permission(permission.resource, permission.action)


def check_permission(authority: Authority, resource: str, action: str) -> bool:
    """Check if an authority has permission for a resource/action."""
    if not isinstance(authority, Authority):
        return False
    return authority.has_permission(resource, action)


def request_approval(
    requester: str,
    permission: Permission,
    reason: Optional[str] = None,
    metadata: Optional[dict] = None,
) -> Approval:
    """Request approval for a permission."""
    return Approval(
        approval_id=str(uuid4()),
        requester=requester,
        approver=None,
        permission=permission,
        status=ApprovalStatus.PENDING,
        requested_at=datetime.now(timezone.utc),
        reason=reason,
        metadata=metadata or {},
    )


def grant_permission(authority: Authority, resource: str, action: str, authority_level: AuthorityLevel) -> None:
    """Grant a permission to an authority."""
    permission = Permission(resource=resource, action=action, authority_level=authority_level)
    authority.grant_permission(permission)


def revoke_permission(authority: Authority, resource: str, action: str) -> None:
    """Revoke a permission from an authority."""
    authority.revoke_permission(resource, action)


# Default permissions for common operations
DEFAULT_PERMISSIONS = {
    # Phase operations
    "phase:advance": Permission(resource="phase", action="advance", authority_level=AuthorityLevel.APPROVE),
    "phase:rollback": Permission(resource="phase", action="rollback", authority_level=AuthorityLevel.ADMIN),
    "phase:skip": Permission(resource="phase", action="skip", authority_level=AuthorityLevel.ADMIN),
    
    # Strategy operations
    "strategy:read": Permission(resource="strategy", action="read", authority_level=AuthorityLevel.READ),
    "strategy:write": Permission(resource="strategy", action="write", authority_level=AuthorityLevel.WRITE),
    "strategy:deploy": Permission(resource="strategy", action="deploy", authority_level=AuthorityLevel.APPROVE),
    "strategy:delete": Permission(resource="strategy", action="delete", authority_level=AuthorityLevel.ADMIN),
    
    # Capital operations
    "capital:read": Permission(resource="capital", action="read", authority_level=AuthorityLevel.READ),
    "capital:allocate": Permission(resource="capital", action="allocate", authority_level=AuthorityLevel.APPROVE),
    "capital:withdraw": Permission(resource="capital", action="withdraw", authority_level=AuthorityLevel.ADMIN),
    
    # System operations
    "system:read": Permission(resource="system", action="read", authority_level=AuthorityLevel.READ),
    "system:write": Permission(resource="system", action="write", authority_level=AuthorityLevel.WRITE),
    "system:admin": Permission(resource="system", action="admin", authority_level=AuthorityLevel.ADMIN),
}
