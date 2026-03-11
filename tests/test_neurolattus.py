"""Tests for the Neurolattus workflow architecture."""

import pytest

from neurolattus import NeuralLattice
from neurolattus.zones import Zone, ZoneType, Task
from neurolattus.workflow import WorkflowEngine, CycleStage, STAGE_ZONE_MAP
from neurolattus.optimizer import WorkflowOptimizer


# ── Zone tests ────────────────────────────────────────────────────────

class TestZone:
    def test_cognitive_load_empty(self):
        zone = Zone(ZoneType.GREEN)
        assert zone.cognitive_load == 0.0

    def test_cognitive_load_with_active_tasks(self):
        zone = Zone(ZoneType.GREEN)
        zone.add_task(Task(id="1", title="A"))
        zone.add_task(Task(id="2", title="B"))
        assert zone.cognitive_load == 2.0  # 2 tasks * 1.0 weight

    def test_completed_tasks_excluded_from_load(self):
        zone = Zone(ZoneType.GREEN)
        t = Task(id="1", title="A")
        t.complete()
        zone.add_task(t)
        assert zone.cognitive_load == 0.0

    def test_yellow_zone_weight(self):
        zone = Zone(ZoneType.YELLOW)
        zone.add_task(Task(id="1", title="A"))
        assert zone.cognitive_load == 0.5

    def test_red_zone_weight(self):
        zone = Zone(ZoneType.RED)
        zone.add_task(Task(id="1", title="A"))
        assert zone.cognitive_load == pytest.approx(0.1)


# ── Workflow engine tests ─────────────────────────────────────────────

class TestWorkflowEngine:
    def test_ingest_task_goes_to_green(self):
        engine = WorkflowEngine()
        t = Task(id="1", title="A")
        engine.ingest_task(t)
        assert t in engine.zones[ZoneType.GREEN].tasks

    def test_full_cycle_completes_task(self):
        engine = WorkflowEngine()
        t = Task(id="1", title="A")
        engine.ingest_task(t)
        engine.run_full_cycle(t)
        assert t.is_complete

    def test_full_cycle_lands_in_red(self):
        engine = WorkflowEngine()
        t = Task(id="1", title="A")
        engine.ingest_task(t)
        engine.run_full_cycle(t)
        # Last two stages (FILE_STORAGE, PERIODIC_PRINTOUTS) are RED
        assert t in engine.zones[ZoneType.RED].tasks

    def test_handler_called(self):
        engine = WorkflowEngine()
        called = []

        def handler(task, ctx):
            called.append(task.id)
            return ctx

        engine.register_handler(CycleStage.CREATIVE_SESSION, handler)
        t = Task(id="x", title="X")
        engine.ingest_task(t)
        engine.advance(t)
        assert called == ["x"]

    def test_stage_advances(self):
        engine = WorkflowEngine()
        t = Task(id="1", title="A")
        engine.ingest_task(t)
        assert engine.current_stage == CycleStage.CREATIVE_SESSION
        engine.advance(t)
        assert engine.current_stage == CycleStage.TEMPLATE_STRUCTURING


# ── Optimizer tests ───────────────────────────────────────────────────

class TestOptimizer:
    def test_analyze_empty(self):
        engine = WorkflowEngine()
        opt = WorkflowOptimizer(engine)
        result = opt.analyze()
        assert result.cognitive_load == 0.0
        assert result.bottleneck_zone is None

    def test_detects_bottleneck(self):
        engine = WorkflowEngine()
        for i in range(10):
            engine.ingest_task(Task(id=str(i), title=f"Task {i}"))
        opt = WorkflowOptimizer(engine, max_green_load=5.0)
        result = opt.analyze()
        assert result.bottleneck_zone == ZoneType.GREEN

    def test_rebalance_reduces_green_load(self):
        engine = WorkflowEngine()
        for i in range(10):
            engine.ingest_task(Task(id=str(i), title=f"Task {i}"))
        opt = WorkflowOptimizer(engine, max_green_load=5.0)
        migrations = opt.rebalance()
        assert len(migrations) > 0
        assert engine.zones[ZoneType.GREEN].cognitive_load <= 5.0


# ── NeuralLattice façade tests ────────────────────────────────────────

class TestNeuralLattice:
    def test_create_and_run(self):
        lattice = NeuralLattice()
        task = lattice.create_task("t1", "Design schema")
        lattice.run(task)
        assert task.is_complete

    def test_summary(self):
        lattice = NeuralLattice()
        lattice.create_task("t1", "A")
        s = lattice.summary()
        assert "cognitive_load" in s
        assert "recommendations" in s

    def test_optimize_returns_result(self):
        lattice = NeuralLattice()
        lattice.create_task("t1", "A")
        result = lattice.optimize()
        assert result.cognitive_load > 0

    def test_rebalance(self):
        lattice = NeuralLattice(max_green_load=2.0)
        for i in range(5):
            lattice.create_task(f"t{i}", f"Task {i}")
        migrations = lattice.rebalance()
        assert len(migrations) > 0
        assert lattice.cognitive_load <= lattice.engine.total_cognitive_load()
