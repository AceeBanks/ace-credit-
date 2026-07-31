"""
GLX FORGE Governance Roles

This module defines the role system for the GLX FORGE trading infrastructure.
Roles define groups of permissions that can be assigned to users or services.

Version: 0.1.0
Phase: Phase 1 - Forge Constitution
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Set
from uuid import UUID, uuid4

from forge.governance.authority import (
    Authority,
    AuthorityLevel,
    Permission,
    DEFAULT_PERMISSIONS,
)


class RoleType(Enum):
    """Role type enumeration."""
    USER = "user"
    SERVICE = "service"
    SYSTEM = "system"


@dataclass
class Role:
    """Role contract."""
    role_id: str
    name: str
    role_type: RoleType
    permissions: Set[Permission] = field(default_factory=set)
    authority_level: AuthorityLevel = AuthorityLevel.READ
    description: str = ""
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    
    def __post_init__(self):
        if not isinstance(self.role_id, str) or not self.role_id:
            self.role_id = str(uuid4())
        if not isinstance(self.name, str) or not self.name:
            raise ValueError("Name cannot be empty")
        if not isinstance(self.role_type, RoleType):
            raise ValueError("Role type must be RoleType enum")
        if not isinstance(self.authority_level, AuthorityLevel):
            raise ValueError("Authority level must be AuthorityLevel enum")
    
    def has_permission(self, resource: str, action: str) -> bool:
        """Check if role has a specific permission."""
        permission_key = f"{resource}:{action}"
        return any(p.key == permission_key for p in self.permissions)
    
    def add_permission(self, permission: Permission) -> None:
        """Add a permission to this role."""
        if not isinstance(permission, Permission):
            raise ValueError("Permission must be a Permission instance")
        self.permissions.add(permission)
    
    def remove_permission(self, resource: str, action: str) -> None:
        """Remove a permission from this role."""
        permission_key = f"{resource}:{action}"
        self.permissions = {p for p in self.permissions if p.key != permission_key}
    
    def to_authority(self, authority_id: Optional[str] = None) -> Authority:
        """Convert this role to an Authority."""
        return Authority(
            authority_id=authority_id or str(uuid4()),
            name=self.name,
            permissions=self.permissions.copy(),
            authority_level=self.authority_level,
        )


# Default roles for the GLX FORGE system
DEFAULT_ROLES = {
    # Read-only role
    "viewer": Role(
        role_id="role-viewer",
        name="Viewer",
        role_type=RoleType.USER,
        permissions={
            DEFAULT_PERMISSIONS["phase:advance"],
            DEFAULT_PERMISSIONS["strategy:read"],
            DEFAULT_PERMISSIONS["capital:read"],
            DEFAULT_PERMISSIONS["system:read"],
        },
        authority_level=AuthorityLevel.READ,
        description="Read-only access to all resources",
    ),
    
    # Researcher role
    "researcher": Role(
        role_id="role-researcher",
        name="Researcher",
        role_type=RoleType.USER,
        permissions={
            DEFAULT_PERMISSIONS["phase:advance"],
            DEFAULT_PERMISSIONS["strategy:read"],
            DEFAULT_PERMISSIONS["strategy:write"],
            DEFAULT_PERMISSIONS["capital:read"],
            DEFAULT_PERMISSIONS["system:read"],
        },
        authority_level=AuthorityLevel.WRITE,
        description="Can read and write strategies, but cannot deploy",
    ),
    
    # Strategist role
    "strategist": Role(
        role_id="role-strategist",
        name="Strategist",
        role_type=RoleType.USER,
        permissions={
            DEFAULT_PERMISSIONS["phase:advance"],
            DEFAULT_PERMISSIONS["strategy:read"],
            DEFAULT_PERMISSIONS["strategy:write"],
            DEFAULT_PERMISSIONS["strategy:deploy"],
            DEFAULT_PERMISSIONS["capital:read"],
            DEFAULT_PERMISSIONS["system:read"],
        },
        authority_level=AuthorityLevel.APPROVE,
        description="Can deploy strategies and approve capital allocations",
    ),
    
    # Admin role
    "admin": Role(
        role_id="role-admin",
        name="Administrator",
        role_type=RoleType.USER,
        permissions=set(DEFAULT_PERMISSIONS.values()),
        authority_level=AuthorityLevel.ADMIN,
        description="Full administrative access to all resources",
    ),
    
    # Service roles
    "data_service": Role(
        role_id="role-data-service",
        name="Data Service",
        role_type=RoleType.SERVICE,
        permissions={
            DEFAULT_PERMISSIONS["system:read"],
            DEFAULT_PERMISSIONS["system:write"],
        },
        authority_level=AuthorityLevel.WRITE,
        description="Service role for data ingestion and processing",
    ),
    
    "execution_service": Role(
        role_id="role-execution-service",
        name="Execution Service",
        role_type=RoleType.SERVICE,
        permissions={
            DEFAULT_PERMISSIONS["system:read"],
            DEFAULT_PERMISSIONS["system:write"],
            DEFAULT_PERMISSIONS["strategy:read"],
        },
        authority_level=AuthorityLevel.WRITE,
        description="Service role for order execution",
    ),
    
    "backtest_service": Role(
        role_id="role-backtest-service",
        name="Backtest Service",
        role_type=RoleType.SERVICE,
        permissions={
            DEFAULT_PERMISSIONS["system:read"],
            DEFAULT_PERMISSIONS["system:write"],
            DEFAULT_PERMISSIONS["strategy:read"],
            DEFAULT_PERMISSIONS["strategy:write"],
        },
        authority_level=AuthorityLevel.WRITE,
        description="Service role for backtesting",
    ),
}


def get_role(role_name: str) -> Role:
    """Get a role by name."""
    role = DEFAULT_ROLES.get(role_name)
    if role is None:
        raise ValueError(f"Role not found: {role_name}")
    return role


def assign_role(role: Role, authority_id: str) -> Authority:
    """Assign a role to an authority."""
    return role.to_authority(authority_id)


def remove_role(authority: Authority, role_name: str) -> None:
    """Remove a role's permissions from an authority."""
    role = get_role(role_name)
    for permission in role.permissions:
        authority.revoke_permission(permission.resource, permission.action)
