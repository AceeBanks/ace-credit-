"""
GLX FORGE Intelligence Causal Mapping

This module defines the causal mapping system for the GLX FORGE trading infrastructure.
Causal mapping models cause-effect relationships between market variables.

Version: 0.1.0
Phase: Phase 4 - Intelligence Forge
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Optional, Dict, List, Set
from uuid import UUID, uuid4


class CausalRelationship(Enum):
    """Causal relationship enumeration."""
    POSITIVE = "positive"  # A causes B to increase
    NEGATIVE = "negative"  # A causes B to decrease
    BIDIRECTIONAL = "bidirectional"  # A and B cause each other
    UNKNOWN = "unknown"


class CausalStrength(Enum):
    """Causal strength enumeration."""
    VERY_WEAK = "very_weak"
    WEAK = "weak"
    MODERATE = "moderate"
    STRONG = "strong"
    VERY_STRONG = "very_strong"


@dataclass
class CausalNode:
    """Causal node contract."""
    node_id: str
    variable_name: str
    variable_type: str  # "price", "volume", "sentiment", etc.
    instrument_id: str
    metadata: Dict = field(default_factory=dict)
    
    def __post_init__(self):
        if not isinstance(self.node_id, str) or not self.node_id:
            self.node_id = str(uuid4())
        if not isinstance(self.variable_name, str) or not self.variable_name:
            raise ValueError("Variable name cannot be empty")
        if not isinstance(self.variable_type, str) or not self.variable_type:
            raise ValueError("Variable type cannot be empty")
        if not isinstance(self.instrument_id, str) or not self.instrument_id:
            raise ValueError("Instrument ID cannot be empty")
    
    @property
    def key(self) -> str:
        """Get unique key for this node."""
        return f"{self.instrument_id}:{self.variable_name}"


@dataclass
class CausalEdge:
    """Causal edge contract."""
    edge_id: str
    from_node_id: str
    to_node_id: str
    relationship: CausalRelationship
    strength: CausalStrength
    confidence: float  # 0.0 to 1.0
    lag_seconds: int = 0
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: Optional[datetime] = None
    metadata: Dict = field(default_factory=dict)
    
    def __post_init__(self):
        if not isinstance(self.edge_id, str) or not self.edge_id:
            self.edge_id = str(uuid4())
        if not isinstance(self.from_node_id, str) or not self.from_node_id:
            raise ValueError("From node ID cannot be empty")
        if not isinstance(self.to_node_id, str) or not self.to_node_id:
            raise ValueError("To node ID cannot be empty")
        if not isinstance(self.relationship, CausalRelationship):
            raise ValueError("Relationship must be CausalRelationship enum")
        if not isinstance(self.strength, CausalStrength):
            raise ValueError("Strength must be CausalStrength enum")
        if not isinstance(self.confidence, (int, float)):
            raise ValueError(f"Confidence must be numeric, got {type(self.confidence)}")
        if not 0.0 <= self.confidence <= 1.0:
            raise ValueError(f"Confidence must be between 0.0 and 1.0, got {self.confidence}")
    
    @property
    def is_positive(self) -> bool:
        """Check if relationship is positive."""
        return self.relationship == CausalRelationship.POSITIVE
    
    @property
    def is_negative(self) -> bool:
        """Check if relationship is negative."""
        return self.relationship == CausalRelationship.NEGATIVE
    
    @property
    def is_bidirectional(self) -> bool:
        """Check if relationship is bidirectional."""
        return self.relationship == CausalRelationship.BIDIRECTIONAL
    
    @property
    def is_high_confidence(self) -> bool:
        """Check if edge has high confidence."""
        return self.confidence >= 0.8
    
    @property
    def is_strong(self) -> bool:
        """Check if edge is strong."""
        return self.strength in [CausalStrength.STRONG, CausalStrength.VERY_STRONG]


@dataclass
class CausalInference:
    """Causal inference contract."""
    inference_id: str
    cause_node_id: str
    effect_node_id: str
    relationship: CausalRelationship
    strength: CausalStrength
    confidence: float
    evidence_count: int = 0
    p_value: Optional[float] = None
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    
    def __post_init__(self):
        if not isinstance(self.inference_id, str) or not self.inference_id:
            self.inference_id = str(uuid4())
        if not isinstance(self.cause_node_id, str) or not self.cause_node_id:
            raise ValueError("Cause node ID cannot be empty")
        if not isinstance(self.effect_node_id, str) or not self.effect_node_id:
            raise ValueError("Effect node ID cannot be empty")
        if not isinstance(self.relationship, CausalRelationship):
            raise ValueError("Relationship must be CausalRelationship enum")
        if not isinstance(self.strength, CausalStrength):
            raise ValueError("Strength must be CausalStrength enum")
        if not isinstance(self.confidence, (int, float)):
            raise ValueError(f"Confidence must be numeric, got {type(self.confidence)}")
        if not 0.0 <= self.confidence <= 1.0:
            raise ValueError(f"Confidence must be between 0.0 and 1.0, got {self.confidence}")
    
    @property
    def is_statistically_significant(self) -> bool:
        """Check if inference is statistically significant."""
        if self.p_value is None:
            return False
        return self.p_value < 0.05


@dataclass
class CausalGraph:
    """Causal graph contract."""
    graph_id: str
    name: str
    instrument_id: str
    nodes: Dict[str, CausalNode] = field(default_factory=dict)
    edges: Dict[str, CausalEdge] = field(default_factory=dict)
    inferences: Dict[str, CausalInference] = field(default_factory=dict)
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: Optional[datetime] = None
    
    def __post_init__(self):
        if not isinstance(self.graph_id, str) or not self.graph_id:
            raise ValueError("Graph ID cannot be empty")
        if not isinstance(self.name, str) or not self.name:
            raise ValueError("Name cannot be empty")
        if not isinstance(self.instrument_id, str) or not self.instrument_id:
            raise ValueError("Instrument ID cannot be empty")
    
    def add_node(self, node: CausalNode) -> None:
        """Add a node to the graph."""
        self.nodes[node.node_id] = node
        self.updated_at = datetime.now(timezone.utc)
    
    def remove_node(self, node_id: str) -> None:
        """Remove a node from the graph."""
        if node_id in self.nodes:
            del self.nodes[node_id]
            # Remove all edges connected to this node
            self.edges = {
                edge_id: edge for edge_id, edge in self.edges.items()
                if edge.from_node_id != node_id and edge.to_node_id != node_id
            }
            self.updated_at = datetime.now(timezone.utc)
    
    def add_edge(self, edge: CausalEdge) -> None:
        """Add an edge to the graph."""
        self.edges[edge.edge_id] = edge
        self.updated_at = datetime.now(timezone.utc)
    
    def remove_edge(self, edge_id: str) -> None:
        """Remove an edge from the graph."""
        if edge_id in self.edges:
            del self.edges[edge_id]
            self.updated_at = datetime.now(timezone.utc)
    
    def add_inference(self, inference: CausalInference) -> None:
        """Add an inference to the graph."""
        self.inferences[inference.inference_id] = inference
        self.updated_at = datetime.now(timezone.utc)
    
    def get_node(self, node_id: str) -> Optional[CausalNode]:
        """Get a node by ID."""
        return self.nodes.get(node_id)
    
    def get_edge(self, edge_id: str) -> Optional[CausalEdge]:
        """Get an edge by ID."""
        return self.edges.get(edge_id)
    
    def get_edges_for_node(self, node_id: str) -> List[CausalEdge]:
        """Get all edges connected to a node."""
        return [
            edge for edge in self.edges.values()
            if edge.from_node_id == node_id or edge.to_node_id == node_id
        ]
    
    def get_causes(self, node_id: str) -> List[CausalEdge]:
        """Get all edges where this node is the effect."""
        return [
            edge for edge in self.edges.values()
            if edge.to_node_id == node_id
        ]
    
    def get_effects(self, node_id: str) -> List[CausalEdge]:
        """Get all edges where this node is the cause."""
        return [
            edge for edge in self.edges.values()
            if edge.from_node_id == node_id
        ]
    
    @property
    def node_count(self) -> int:
        """Get the number of nodes in the graph."""
        return len(self.nodes)
    
    @property
    def edge_count(self) -> int:
        """Get the number of edges in the graph."""
        return len(self.edges)
    
    @property
    def inference_count(self) -> int:
        """Get the number of inferences in the graph."""
        return len(self.inferences)


@dataclass
class CausalModel:
    """Causal model contract."""
    model_id: str
    name: str
    graphs: Dict[str, CausalGraph] = field(default_factory=dict)
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: Optional[datetime] = None
    
    def __post_init__(self):
        if not isinstance(self.model_id, str) or not self.model_id:
            self.model_id = str(uuid4())
        if not isinstance(self.name, str) or not self.name:
            raise ValueError("Name cannot be empty")
    
    def add_graph(self, graph: CausalGraph) -> None:
        """Add a graph to the model."""
        self.graphs[graph.graph_id] = graph
        self.updated_at = datetime.now(timezone.utc)
    
    def remove_graph(self, graph_id: str) -> None:
        """Remove a graph from the model."""
        if graph_id in self.graphs:
            del self.graphs[graph_id]
            self.updated_at = datetime.now(timezone.utc)
    
    def get_graph(self, graph_id: str) -> Optional[CausalGraph]:
        """Get a graph by ID."""
        return self.graphs.get(graph_id)
    
    def get_graph_by_instrument(self, instrument_id: str) -> Optional[CausalGraph]:
        """Get a graph by instrument ID."""
        for graph in self.graphs.values():
            if graph.instrument_id == instrument_id:
                return graph
        return None
    
    @property
    def graph_count(self) -> int:
        """Get the number of graphs in the model."""
        return len(self.graphs)


def create_causal_node(
    variable_name: str,
    variable_type: str,
    instrument_id: str,
) -> CausalNode:
    """Create a new causal node."""
    return CausalNode(
        node_id=str(uuid4()),
        variable_name=variable_name,
        variable_type=variable_type,
        instrument_id=instrument_id,
    )


def create_causal_edge(
    from_node_id: str,
    to_node_id: str,
    relationship: CausalRelationship,
    strength: CausalStrength,
    confidence: float,
    lag_seconds: int = 0,
) -> CausalEdge:
    """Create a new causal edge."""
    return CausalEdge(
        edge_id=str(uuid4()),
        from_node_id=from_node_id,
        to_node_id=to_node_id,
        relationship=relationship,
        strength=strength,
        confidence=confidence,
        lag_seconds=lag_seconds,
    )


def create_causal_inference(
    cause_node_id: str,
    effect_node_id: str,
    relationship: CausalRelationship,
    strength: CausalStrength,
    confidence: float,
    evidence_count: int = 0,
    p_value: Optional[float] = None,
) -> CausalInference:
    """Create a new causal inference."""
    return CausalInference(
        inference_id=str(uuid4()),
        cause_node_id=cause_node_id,
        effect_node_id=effect_node_id,
        relationship=relationship,
        strength=strength,
        confidence=confidence,
        evidence_count=evidence_count,
        p_value=p_value,
    )


def create_causal_graph(name: str, instrument_id: str) -> CausalGraph:
    """Create a new causal graph."""
    return CausalGraph(
        graph_id=str(uuid4()),
        name=name,
        instrument_id=instrument_id,
    )


def create_causal_model(name: str) -> CausalModel:
    """Create a new causal model."""
    return CausalModel(
        model_id=str(uuid4()),
        name=name,
    )
