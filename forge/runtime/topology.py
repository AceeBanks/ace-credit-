"""
GLX FORGE Runtime Topology

This module defines the service topology for the GLX FORGE trading infrastructure.
Topology defines the service graph and communication patterns.

Version: 0.1.0
Phase: Phase 2 - Runtime Foundry
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Optional, Dict, List, Set
from uuid import UUID, uuid4

from forge.runtime.service import Service, ServiceType


class EdgeType(Enum):
    """Edge type enumeration."""
    SYNC = "sync"
    ASYNC = "async"
    STREAM = "stream"
    PUB_SUB = "pub_sub"


@dataclass
class ServiceNode:
    """Service node in the topology graph."""
    node_id: str
    service: Service
    dependencies: Set[str] = field(default_factory=set)
    dependents: Set[str] = field(default_factory=set)
    metadata: Dict = field(default_factory=dict)
    
    def __post_init__(self):
        if not isinstance(self.node_id, str) or not self.node_id:
            self.node_id = str(uuid4())
        if not isinstance(self.service, Service):
            raise ValueError("Service must be a Service instance")
    
    @property
    def service_id(self) -> str:
        """Get service ID."""
        return self.service.service_id
    
    @property
    def service_type(self) -> ServiceType:
        """Get service type."""
        return self.service.service_type
    
    def add_dependency(self, dependency_id: str) -> None:
        """Add a dependency to this node."""
        self.dependencies.add(dependency_id)
    
    def add_dependent(self, dependent_id: str) -> None:
        """Add a dependent to this node."""
        self.dependents.add(dependent_id)
    
    def remove_dependency(self, dependency_id: str) -> None:
        """Remove a dependency from this node."""
        self.dependencies.discard(dependency_id)
    
    def remove_dependent(self, dependent_id: str) -> None:
        """Remove a dependent from this node."""
        self.dependents.discard(dependent_id)


@dataclass
class ServiceEdge:
    """Service edge in the topology graph."""
    edge_id: str
    from_node_id: str
    to_node_id: str
    edge_type: EdgeType
    metadata: Dict = field(default_factory=dict)
    
    def __post_init__(self):
        if not isinstance(self.edge_id, str) or not self.edge_id:
            self.edge_id = str(uuid4())
        if not isinstance(self.from_node_id, str) or not self.from_node_id:
            raise ValueError("From node ID cannot be empty")
        if not isinstance(self.to_node_id, str) or not self.to_node_id:
            raise ValueError("To node ID cannot be empty")
        if not isinstance(self.edge_type, EdgeType):
            raise ValueError("Edge type must be EdgeType enum")
    
    @property
    def is_bidirectional(self) -> bool:
        """Check if edge is bidirectional."""
        return self.metadata.get("bidirectional", False)


@dataclass
class TopologyConfig:
    """Topology configuration contract."""
    topology_id: str
    name: str
    description: str
    environment: str = "development"
    auto_discovery: bool = True
    health_check_interval: int = 30
    metadata: Dict = field(default_factory=dict)
    
    def __post_init__(self):
        if not isinstance(self.topology_id, str) or not self.topology_id:
            self.topology_id = str(uuid4())
        if not isinstance(self.name, str) or not self.name:
            raise ValueError("Name cannot be empty")
        if not isinstance(self.description, str) or not self.description:
            raise ValueError("Description cannot be empty")


@dataclass
class ServiceTopology:
    """Service topology contract."""
    topology_id: str
    config: TopologyConfig
    nodes: Dict[str, ServiceNode] = field(default_factory=dict)
    edges: Dict[str, ServiceEdge] = field(default_factory=dict)
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: Optional[datetime] = None
    
    def __post_init__(self):
        if not isinstance(self.topology_id, str) or not self.topology_id:
            raise ValueError("Topology ID cannot be empty")
        if not isinstance(self.config, TopologyConfig):
            raise ValueError("Config must be a TopologyConfig instance")
    
    def add_node(self, node: ServiceNode) -> None:
        """Add a node to the topology."""
        self.nodes[node.node_id] = node
        self.updated_at = datetime.now(timezone.utc)
    
    def remove_node(self, node_id: str) -> None:
        """Remove a node from the topology."""
        if node_id in self.nodes:
            del self.nodes[node_id]
            # Remove all edges connected to this node
            self.edges = {
                edge_id: edge for edge_id, edge in self.edges.items()
                if edge.from_node_id != node_id and edge.to_node_id != node_id
            }
            self.updated_at = datetime.now(timezone.utc)
    
    def add_edge(self, edge: ServiceEdge) -> None:
        """Add an edge to the topology."""
        self.edges[edge.edge_id] = edge
        
        # Update node dependencies
        if edge.from_node_id in self.nodes:
            self.nodes[edge.from_node_id].add_dependent(edge.to_node_id)
        if edge.to_node_id in self.nodes:
            self.nodes[edge.to_node_id].add_dependency(edge.from_node_id)
        
        self.updated_at = datetime.now(timezone.utc)
    
    def remove_edge(self, edge_id: str) -> None:
        """Remove an edge from the topology."""
        if edge_id in self.edges:
            edge = self.edges[edge_id]
            
            # Update node dependencies
            if edge.from_node_id in self.nodes:
                self.nodes[edge.from_node_id].remove_dependent(edge.to_node_id)
            if edge.to_node_id in self.nodes:
                self.nodes[edge.to_node_id].remove_dependency(edge.from_node_id)
            
            del self.edges[edge_id]
            self.updated_at = datetime.now(timezone.utc)
    
    def get_node(self, node_id: str) -> Optional[ServiceNode]:
        """Get a node by ID."""
        return self.nodes.get(node_id)
    
    def get_edge(self, edge_id: str) -> Optional[ServiceEdge]:
        """Get an edge by ID."""
        return self.edges.get(edge_id)
    
    def get_edges_for_node(self, node_id: str) -> List[ServiceEdge]:
        """Get all edges connected to a node."""
        return [
            edge for edge in self.edges.values()
            if edge.from_node_id == node_id or edge.to_node_id == node_id
        ]
    
    def get_dependencies(self, node_id: str) -> List[ServiceNode]:
        """Get all dependencies of a node."""
        if node_id not in self.nodes:
            return []
        node = self.nodes[node_id]
        return [self.nodes[dep_id] for dep_id in node.dependencies if dep_id in self.nodes]
    
    def get_dependents(self, node_id: str) -> List[ServiceNode]:
        """Get all dependents of a node."""
        if node_id not in self.nodes:
            return []
        node = self.nodes[node_id]
        return [self.nodes[dep_id] for dep_id in node.dependents if dep_id in self.nodes]
    
    @property
    def node_count(self) -> int:
        """Get the number of nodes in the topology."""
        return len(self.nodes)
    
    @property
    def edge_count(self) -> int:
        """Get the number of edges in the topology."""
        return len(self.edges)
    
    @property
    def is_empty(self) -> bool:
        """Check if topology is empty."""
        return self.node_count == 0


def create_topology(name: str, description: str, environment: str = "development") -> ServiceTopology:
    """Create a new service topology."""
    config = TopologyConfig(
        topology_id=str(uuid4()),
        name=name,
        description=description,
        environment=environment,
    )
    
    return ServiceTopology(
        topology_id=config.topology_id,
        config=config,
    )


# Default topology for GLX FORGE
DEFAULT_FORGE_TOPOLOGY = create_topology(
    name="GLX FORGE Runtime Topology",
    description="Default service topology for GLX FORGE trading infrastructure",
    environment="development",
)
