# Quantum Nexus Forge
# Date: August 10, 2025
# Version: 6.0.0 - HYPHENATOR RULE OF COGNITIVE PRIMITIVES

import hashlib
import math
import threading
import uuid
from collections import defaultdict, deque
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, List, Optional

# ====================================
# ENHANCED COGNITIVE PRIMITIVES
# ====================================

class CognitivePrimitiveType(Enum):
    """Enhanced geometric primitives for cognitive lattice operations."""
    TETRAHEDRON = ("tetrahedron_transform", 4, 256.0, "triangulation")
    CUBE = ("cube_stabilize", 6, 639.0, "stabilization")
    OCTAHEDRON = ("octahedron_process", 8, 512.0, "processing")
    ICOSAHEDRON = ("icosahedron_flow", 20, 1024.0, "flow_routing")
    DODECAHEDRON = ("dodecahedron_unify", 12, 768.0, "unification")
    METATRON_CUBE = ("metatron_core", 13, 2048.0, "core_synthesis")

    def __init__(self, operation: str, faces: int, resonance: float, mode: str):
        self.operation = operation
        self.faces = faces
        self.resonance = resonance
        self.mode = mode


@dataclass
class CognitiveNode:
    """A node in the cognitive lattice representing a primitive operation."""
    node_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    primitive_type: CognitivePrimitiveType = CognitivePrimitiveType.TETRAHEDRON
    energy: float = 1.0
    coherence: float = 1.0
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    connections: List[str] = field(default_factory=list)
    state: Dict[str, Any] = field(default_factory=dict)

    def signature(self) -> str:
        """Generate a unique hash signature for this node's current state."""
        data = f"{self.node_id}:{self.primitive_type.operation}:{self.energy}:{self.coherence}"
        return hashlib.sha256(data.encode()).hexdigest()[:16]


@dataclass
class LatticeEdge:
    """An edge connecting two cognitive nodes with a weighted relationship."""
    source_id: str
    target_id: str
    weight: float = 1.0
    edge_type: str = "resonance"
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


# ====================================
# QUANTUM NEXUS FORGE ENGINE
# ====================================

class QuantumNexusForge:
    """
    Core engine for the Quantum Nexus Forge system.

    Manages a lattice of cognitive primitive nodes, applies geometric
    transformations, and orchestrates resonance-based processing flows.
    """

    def __init__(self, lattice_depth: int = 6, resonance_threshold: float = 0.5):
        self.lattice_depth = lattice_depth
        self.resonance_threshold = resonance_threshold
        self.nodes: Dict[str, CognitiveNode] = {}
        self.edges: List[LatticeEdge] = []
        self.processing_queue: deque = deque()
        self.energy_map: Dict[str, float] = defaultdict(float)
        self._lock = threading.Lock()
        self.forge_id = str(uuid.uuid4())
        self.created_at = datetime.now(timezone.utc)
        self.cycle_count = 0

    def add_node(
        self, primitive_type: CognitivePrimitiveType, energy: float = 1.0
    ) -> CognitiveNode:
        """Add a new cognitive node to the lattice."""
        node = CognitiveNode(
            primitive_type=primitive_type,
            energy=energy,
        )
        with self._lock:
            self.nodes[node.node_id] = node
            self.energy_map[node.node_id] = energy
        return node

    def connect_nodes(
        self, source_id: str, target_id: str, weight: float = 1.0
    ) -> Optional[LatticeEdge]:
        """Create a resonance edge between two nodes."""
        if source_id not in self.nodes or target_id not in self.nodes:
            return None
        edge = LatticeEdge(source_id=source_id, target_id=target_id, weight=weight)
        with self._lock:
            self.edges.append(edge)
            self.nodes[source_id].connections.append(target_id)
            self.nodes[target_id].connections.append(source_id)
        return edge

    def compute_resonance(self, node_id: str) -> float:
        """Compute the resonance value for a node based on its connections and primitive type."""
        if node_id not in self.nodes:
            return 0.0
        node = self.nodes[node_id]
        base_resonance = node.primitive_type.resonance
        connection_factor = len(node.connections) / max(node.primitive_type.faces, 1)
        energy_factor = node.energy * node.coherence
        resonance = base_resonance * connection_factor * energy_factor
        return min(resonance, base_resonance * 2)

    def apply_transform(self, node_id: str) -> Dict[str, Any]:
        """Apply the geometric transformation associated with the node's primitive type."""
        if node_id not in self.nodes:
            return {"error": "node_not_found"}

        node = self.nodes[node_id]
        primitive = node.primitive_type
        resonance = self.compute_resonance(node_id)

        result = {
            "node_id": node_id,
            "operation": primitive.operation,
            "mode": primitive.mode,
            "resonance": resonance,
            "faces": primitive.faces,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }

        # Apply mode-specific transformations
        if primitive.mode == "triangulation":
            result["transform"] = self._triangulate(node, resonance)
        elif primitive.mode == "stabilization":
            result["transform"] = self._stabilize(node, resonance)
        elif primitive.mode == "processing":
            result["transform"] = self._process_octahedral(node, resonance)
        elif primitive.mode == "flow_routing":
            result["transform"] = self._route_flow(node, resonance)
        elif primitive.mode == "unification":
            result["transform"] = self._unify(node, resonance)
        elif primitive.mode == "core_synthesis":
            result["transform"] = self._synthesize_core(node, resonance)

        with self._lock:
            self.cycle_count += 1

        return result

    def _triangulate(self, node: CognitiveNode, resonance: float) -> Dict[str, float]:
        """Tetrahedron triangulation transform."""
        phi = (1 + math.sqrt(5)) / 2  # Golden ratio
        return {
            "vertices": 4,
            "phi_factor": phi * resonance,
            "energy_delta": node.energy * math.sin(
                resonance / node.primitive_type.resonance * math.pi
            ),
        }

    def _stabilize(self, node: CognitiveNode, resonance: float) -> Dict[str, float]:
        """Cube stabilization transform."""
        return {
            "vertices": 8,
            "stability_index": resonance / 639.0,
            "energy_delta": node.energy * math.cos(
                resonance / node.primitive_type.resonance * math.pi / 2
            ),
        }

    def _process_octahedral(self, node: CognitiveNode, resonance: float) -> Dict[str, float]:
        """Octahedron processing transform."""
        return {
            "vertices": 6,
            "processing_depth": int(resonance / 128),
            "energy_delta": node.energy * (1 - math.exp(-resonance / 512.0)),
        }

    def _route_flow(self, node: CognitiveNode, resonance: float) -> Dict[str, float]:
        """Icosahedron flow routing transform."""
        return {
            "vertices": 12,
            "flow_channels": min(int(resonance / 64), 20),
            "energy_delta": node.energy * math.log1p(resonance / node.primitive_type.resonance),
        }

    def _unify(self, node: CognitiveNode, resonance: float) -> Dict[str, float]:
        """Dodecahedron unification transform."""
        return {
            "vertices": 20,
            "unity_factor": resonance / node.primitive_type.resonance,
            "energy_delta": node.energy * math.tanh(resonance / 768.0),
        }

    def _synthesize_core(self, node: CognitiveNode, resonance: float) -> Dict[str, float]:
        """Metatron cube core synthesis transform."""
        phi = (1 + math.sqrt(5)) / 2
        return {
            "vertices": 13,
            "synthesis_depth": int(math.log2(max(resonance, 1))),
            "phi_harmonic": phi ** (resonance / node.primitive_type.resonance),
            "energy_delta": node.energy * (1 - math.exp(-resonance / 1024.0)),
        }

    def propagate_energy(self) -> Dict[str, float]:
        """Propagate energy through the lattice along resonance edges."""
        deltas: Dict[str, float] = defaultdict(float)
        for edge in self.edges:
            if edge.source_id in self.nodes and edge.target_id in self.nodes:
                source = self.nodes[edge.source_id]
                transfer = source.energy * edge.weight * 0.1
                deltas[edge.source_id] -= transfer
                deltas[edge.target_id] += transfer

        with self._lock:
            for node_id, delta in deltas.items():
                if node_id in self.nodes:
                    self.nodes[node_id].energy = max(0.0, self.nodes[node_id].energy + delta)
                    self.energy_map[node_id] = self.nodes[node_id].energy

        return dict(deltas)

    def get_lattice_state(self) -> Dict[str, Any]:
        """Return a snapshot of the current lattice state."""
        return {
            "forge_id": self.forge_id,
            "cycle_count": self.cycle_count,
            "node_count": len(self.nodes),
            "edge_count": len(self.edges),
            "total_energy": sum(n.energy for n in self.nodes.values()),
            "avg_coherence": (
                sum(n.coherence for n in self.nodes.values()) / len(self.nodes)
                if self.nodes
                else 0.0
            ),
            "nodes": {
                nid: {
                    "type": n.primitive_type.name,
                    "energy": n.energy,
                    "coherence": n.coherence,
                    "connections": len(n.connections),
                }
                for nid, n in self.nodes.items()
            },
        }

    def forge_cycle(self) -> List[Dict[str, Any]]:
        """Run a full forge cycle: transform all nodes and propagate energy."""
        results = []
        for node_id in list(self.nodes.keys()):
            result = self.apply_transform(node_id)
            results.append(result)
        self.propagate_energy()
        return results
