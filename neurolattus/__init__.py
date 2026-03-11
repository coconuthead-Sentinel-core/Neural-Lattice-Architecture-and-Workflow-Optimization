"""
Neurolattus - Neural Lattice Architecture for Workflow Optimization.

A cognitive workflow framework that organizes work into three zones
(GREEN, YELLOW, RED) and provides an optimized execution cycle for
AI-human collaboration.
"""

from neurolattus.core import NeuralLattice
from neurolattus.zones import Zone, ZoneType
from neurolattus.workflow import WorkflowEngine
from neurolattus.optimizer import WorkflowOptimizer

__version__ = "0.1.0"
__all__ = ["NeuralLattice", "Zone", "ZoneType", "WorkflowEngine", "WorkflowOptimizer"]
