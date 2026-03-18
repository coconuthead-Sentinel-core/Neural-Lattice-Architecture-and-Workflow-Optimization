"""Tests for the Zone Engine FSM (Charter Section 3.2)."""

import pytest

from neural_lattice.zone_engine import ZoneEngine, TransitionError
from neural_lattice.meta.schemas import ZoneEnum, StatusEnum


class TestClassifyZone:
    def test_green_zone(self):
        for load in (7, 8, 9, 10):
            assert ZoneEngine.classify_zone(load) == ZoneEnum.GREEN

    def test_yellow_zone(self):
        for load in (4, 5, 6):
            assert ZoneEngine.classify_zone(load) == ZoneEnum.YELLOW

    def test_red_zone(self):
        for load in (1, 2, 3):
            assert ZoneEngine.classify_zone(load) == ZoneEnum.RED

    def test_invalid_load(self):
        with pytest.raises(ValueError):
            ZoneEngine.classify_zone(0)
        with pytest.raises(ValueError):
            ZoneEngine.classify_zone(11)


class TestGreenToYellow:
    def test_success(self):
        result = ZoneEngine.transition(
            ZoneEnum.GREEN, ZoneEnum.YELLOW,
            cognitive_load=5, status="ACTIVE",
        )
        assert result.success
        assert result.from_zone == ZoneEnum.GREEN
        assert result.to_zone == ZoneEnum.YELLOW

    def test_blocked_high_load(self):
        with pytest.raises(TransitionError, match="cognitive_load must be < 7"):
            ZoneEngine.transition(
                ZoneEnum.GREEN, ZoneEnum.YELLOW,
                cognitive_load=8, status="ACTIVE",
            )

    def test_blocked_draft_status(self):
        with pytest.raises(TransitionError, match="must not be DRAFT"):
            ZoneEngine.transition(
                ZoneEnum.GREEN, ZoneEnum.YELLOW,
                cognitive_load=5, status="DRAFT",
            )


class TestYellowToRed:
    def test_success(self):
        result = ZoneEngine.transition(
            ZoneEnum.YELLOW, ZoneEnum.RED,
            cognitive_load=2, version="1.0",
        )
        assert result.success

    def test_blocked_high_load(self):
        with pytest.raises(TransitionError, match="cognitive_load must be < 4"):
            ZoneEngine.transition(
                ZoneEnum.YELLOW, ZoneEnum.RED,
                cognitive_load=5, version="1.0",
            )

    def test_blocked_low_version(self):
        with pytest.raises(TransitionError, match="version must be >= 1.0"):
            ZoneEngine.transition(
                ZoneEnum.YELLOW, ZoneEnum.RED,
                cognitive_load=2, version="0.5",
            )


class TestRedToYellow:
    def test_success(self):
        result = ZoneEngine.transition(
            ZoneEnum.RED, ZoneEnum.YELLOW,
            revision_needed=True,
        )
        assert result.success

    def test_blocked(self):
        with pytest.raises(TransitionError, match="revision_needed"):
            ZoneEngine.transition(ZoneEnum.RED, ZoneEnum.YELLOW)


class TestRedToGreen:
    def test_success(self):
        result = ZoneEngine.transition(
            ZoneEnum.RED, ZoneEnum.GREEN,
            scope_change_approved=True,
        )
        assert result.success

    def test_blocked(self):
        with pytest.raises(TransitionError, match="scope_change_approved"):
            ZoneEngine.transition(ZoneEnum.RED, ZoneEnum.GREEN)


class TestInvalidTransitions:
    def test_green_to_red(self):
        with pytest.raises(TransitionError, match="No valid transition"):
            ZoneEngine.transition(ZoneEnum.GREEN, ZoneEnum.RED)

    def test_yellow_to_green(self):
        with pytest.raises(TransitionError, match="No valid transition"):
            ZoneEngine.transition(ZoneEnum.YELLOW, ZoneEnum.GREEN)


class TestCanTransition:
    def test_returns_true(self):
        ok, err = ZoneEngine.can_transition(
            ZoneEnum.GREEN, ZoneEnum.YELLOW,
            cognitive_load=5, status="ACTIVE",
        )
        assert ok is True
        assert err is None

    def test_returns_false_with_reason(self):
        ok, err = ZoneEngine.can_transition(
            ZoneEnum.GREEN, ZoneEnum.YELLOW,
            cognitive_load=9, status="ACTIVE",
        )
        assert ok is False
        assert "cognitive_load" in err


class TestGetNewStatus:
    def test_green_yellow(self):
        assert ZoneEngine.get_new_status(ZoneEnum.GREEN, ZoneEnum.YELLOW) == StatusEnum.ACTIVE

    def test_yellow_red(self):
        assert ZoneEngine.get_new_status(ZoneEnum.YELLOW, ZoneEnum.RED) == StatusEnum.ARCHIVED

    def test_red_green(self):
        assert ZoneEngine.get_new_status(ZoneEnum.RED, ZoneEnum.GREEN) == StatusEnum.DRAFT
