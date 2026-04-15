"""Tests for the Quantum Nexus Forge engine."""

from neural_lattice.quantum_nexus_forge import (
    CognitiveNode,
    CognitivePrimitiveType,
    QuantumNexusForge,
)


class TestCognitivePrimitiveType:
    def test_all_primitives_have_required_attrs(self):
        for ptype in CognitivePrimitiveType:
            assert isinstance(ptype.operation, str)
            assert isinstance(ptype.faces, int)
            assert isinstance(ptype.resonance, float)
            assert isinstance(ptype.mode, str)

    def test_tetrahedron(self):
        t = CognitivePrimitiveType.TETRAHEDRON
        assert t.faces == 4
        assert t.mode == "triangulation"

    def test_metatron_cube(self):
        m = CognitivePrimitiveType.METATRON_CUBE
        assert m.faces == 13
        assert m.mode == "core_synthesis"
        assert m.resonance == 2048.0


class TestCognitiveNode:
    def test_default_creation(self):
        node = CognitiveNode()
        assert node.energy == 1.0
        assert node.coherence == 1.0
        assert node.primitive_type == CognitivePrimitiveType.TETRAHEDRON
        assert len(node.connections) == 0

    def test_signature_is_deterministic(self):
        node = CognitiveNode()
        sig1 = node.signature()
        sig2 = node.signature()
        assert sig1 == sig2

    def test_different_nodes_different_signatures(self):
        n1 = CognitiveNode()
        n2 = CognitiveNode()
        assert n1.signature() != n2.signature()


class TestQuantumNexusForge:
    def test_add_node(self):
        forge = QuantumNexusForge()
        node = forge.add_node(CognitivePrimitiveType.CUBE)
        assert node.node_id in forge.nodes
        assert forge.energy_map[node.node_id] == 1.0

    def test_connect_nodes(self):
        forge = QuantumNexusForge()
        n1 = forge.add_node(CognitivePrimitiveType.TETRAHEDRON)
        n2 = forge.add_node(CognitivePrimitiveType.OCTAHEDRON)
        edge = forge.connect_nodes(n1.node_id, n2.node_id, weight=0.8)
        assert edge is not None
        assert edge.weight == 0.8
        assert n2.node_id in n1.connections
        assert n1.node_id in n2.connections

    def test_connect_invalid_node_returns_none(self):
        forge = QuantumNexusForge()
        n1 = forge.add_node(CognitivePrimitiveType.TETRAHEDRON)
        assert forge.connect_nodes(n1.node_id, "nonexistent") is None

    def test_compute_resonance_no_connections(self):
        forge = QuantumNexusForge()
        node = forge.add_node(CognitivePrimitiveType.CUBE)
        resonance = forge.compute_resonance(node.node_id)
        assert resonance == 0.0  # no connections -> 0 factor

    def test_compute_resonance_with_connections(self):
        forge = QuantumNexusForge()
        n1 = forge.add_node(CognitivePrimitiveType.CUBE)
        n2 = forge.add_node(CognitivePrimitiveType.TETRAHEDRON)
        forge.connect_nodes(n1.node_id, n2.node_id)
        resonance = forge.compute_resonance(n1.node_id)
        assert resonance > 0.0

    def test_apply_transform_all_types(self):
        forge = QuantumNexusForge()
        for ptype in CognitivePrimitiveType:
            node = forge.add_node(ptype, energy=1.0)
            # Add a connection so resonance > 0
            other = forge.add_node(CognitivePrimitiveType.TETRAHEDRON)
            forge.connect_nodes(node.node_id, other.node_id)
            result = forge.apply_transform(node.node_id)
            assert result["operation"] == ptype.operation
            assert result["mode"] == ptype.mode
            assert "transform" in result

    def test_apply_transform_invalid_node(self):
        forge = QuantumNexusForge()
        result = forge.apply_transform("nonexistent")
        assert result == {"error": "node_not_found"}

    def test_propagate_energy(self):
        forge = QuantumNexusForge()
        n1 = forge.add_node(CognitivePrimitiveType.CUBE, energy=10.0)
        n2 = forge.add_node(CognitivePrimitiveType.TETRAHEDRON, energy=1.0)
        forge.connect_nodes(n1.node_id, n2.node_id, weight=1.0)
        deltas = forge.propagate_energy()
        assert deltas[n1.node_id] < 0  # lost energy
        assert deltas[n2.node_id] > 0  # gained energy (net)

    def test_get_lattice_state(self):
        forge = QuantumNexusForge()
        forge.add_node(CognitivePrimitiveType.ICOSAHEDRON)
        forge.add_node(CognitivePrimitiveType.DODECAHEDRON)
        state = forge.get_lattice_state()
        assert state["node_count"] == 2
        assert state["edge_count"] == 0
        assert state["total_energy"] == 2.0

    def test_forge_cycle(self):
        forge = QuantumNexusForge()
        n1 = forge.add_node(CognitivePrimitiveType.METATRON_CUBE, energy=5.0)
        n2 = forge.add_node(CognitivePrimitiveType.CUBE, energy=3.0)
        forge.connect_nodes(n1.node_id, n2.node_id)
        results = forge.forge_cycle()
        assert len(results) == 2
        assert forge.cycle_count == 2

    def test_compute_resonance_nonexistent(self):
        forge = QuantumNexusForge()
        assert forge.compute_resonance("fake") == 0.0
