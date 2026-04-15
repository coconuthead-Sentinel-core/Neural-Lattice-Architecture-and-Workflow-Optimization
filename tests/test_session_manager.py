"""Tests for the Session Manager (Pomodoro + cognitive load tracking)."""

import pytest

from neural_lattice.session_manager import SessionManager, SessionPhase


@pytest.fixture
def mgr():
    return SessionManager(pomodoro_minutes=25, break_minutes=5, long_break_interval=4)


class TestSessionLifecycle:
    def test_init(self, mgr):
        session = mgr.init_session("s1")
        assert session.session_id == "s1"
        assert session.phase == SessionPhase.INIT

    def test_start_work(self, mgr):
        mgr.init_session("s1")
        session = mgr.start_work("s1")
        assert session.phase == SessionPhase.WORK
        assert len(session.work_blocks) == 1

    def test_end_work_triggers_break(self, mgr):
        mgr.init_session("s1")
        mgr.start_work("s1")
        session = mgr.end_work("s1", cognitive_load=7)
        assert session.phase == SessionPhase.REFLECT
        assert session.pomodoro_count == 1
        assert session.cognitive_loads == [7]
        # Complete the ouroboros loop: reflect → break
        session = mgr.reflect("s1", insight="Test insight", carry_forward="Next focus")
        assert session.phase == SessionPhase.BREAK
        assert len(session.reflections) == 1
        assert session.reflections[0].insight == "Test insight"
        assert session.latest_carry_forward == "Next focus"

    def test_long_break_after_4_pomodoros(self, mgr):
        mgr.init_session("s1")
        for i in range(4):
            mgr.start_work("s1")
            mgr.end_work("s1", cognitive_load=5)
            mgr.reflect("s1", insight=f"Cycle {i + 1} reflection")
        session = mgr.get_session("s1")
        assert session.phase == SessionPhase.LONG_BREAK
        assert session.pomodoro_count == 4
        assert len(session.reflections) == 4

    def test_wrap_up_and_close(self, mgr):
        mgr.init_session("s1")
        mgr.start_work("s1")
        mgr.end_work("s1")
        mgr.reflect("s1", insight="Wrapping up")
        session = mgr.wrap_up("s1")
        assert session.phase == SessionPhase.WRAP_UP
        session = mgr.close("s1")
        assert session.phase == SessionPhase.CLOSED
        assert session.ended_at is not None

    def test_cannot_work_from_work(self, mgr):
        mgr.init_session("s1")
        mgr.start_work("s1")
        with pytest.raises(ValueError, match="Cannot start work"):
            mgr.start_work("s1")

    def test_cannot_end_work_from_break(self, mgr):
        mgr.init_session("s1")
        mgr.start_work("s1")
        mgr.end_work("s1")
        with pytest.raises(ValueError, match="Cannot end work"):
            mgr.end_work("s1")

    def test_double_close_raises(self, mgr):
        mgr.init_session("s1")
        mgr.wrap_up("s1")
        mgr.close("s1")
        with pytest.raises(ValueError):
            mgr.wrap_up("s1")


class TestCognitiveLoad:
    def test_record_load(self, mgr):
        mgr.init_session("s1")
        session = mgr.record_load("s1", 7)
        assert session.cognitive_loads == [7]

    def test_average_load(self, mgr):
        mgr.init_session("s1")
        mgr.record_load("s1", 6)
        mgr.record_load("s1", 8)
        session = mgr.get_session("s1")
        assert session.average_cognitive_load == 7.0

    def test_invalid_load_rejected(self, mgr):
        mgr.init_session("s1")
        with pytest.raises(ValueError, match="1-10"):
            mgr.record_load("s1", 11)

    def test_none_average_when_empty(self, mgr):
        session = mgr.init_session("s1")
        assert session.average_cognitive_load is None


class TestSessionLookup:
    def test_missing_session_raises(self, mgr):
        with pytest.raises(KeyError):
            mgr.get_session("nonexistent")

    def test_list_sessions(self, mgr):
        mgr.init_session("s1")
        mgr.init_session("s2")
        assert len(mgr.list_sessions()) == 2

    def test_to_dict(self, mgr):
        session = mgr.init_session("s1")
        d = session.to_dict()
        assert d["session_id"] == "s1"
        assert d["phase"] == "INIT"
        assert "work_blocks" in d
        assert "reflections" in d
        assert d["latest_carry_forward"] == ""


class TestStructuredReflection:
    """Tests for the Structured Reflection ouroboros pattern.

    The closed loop: WORK → REFLECT → BREAK → WORK
    Each reflection captures an insight and carry_forward that feeds the next cycle.
    """

    def test_reflect_creates_entry(self, mgr):
        mgr.init_session("sr1")
        mgr.start_work("sr1")
        mgr.end_work("sr1", cognitive_load=7)
        session = mgr.reflect("sr1", insight="Discovered pattern", carry_forward="Apply pattern")
        assert len(session.reflections) == 1
        r = session.reflections[0]
        assert r.insight == "Discovered pattern"
        assert r.carry_forward == "Apply pattern"
        assert r.pomodoro_number == 1
        assert r.cognitive_load_before == 7

    def test_reflect_with_post_load(self, mgr):
        mgr.init_session("sr2")
        mgr.start_work("sr2")
        mgr.end_work("sr2", cognitive_load=8)
        session = mgr.reflect(
            "sr2", insight="Heavy work", cognitive_load_after=4, carry_forward="Simplify"
        )
        r = session.reflections[0]
        assert r.cognitive_load_before == 8
        assert r.cognitive_load_after == 4
        # Post-reflection load is recorded in session cognitive_loads
        assert 4 in session.cognitive_loads

    def test_reflect_requires_reflect_phase(self, mgr):
        mgr.init_session("sr3")
        with pytest.raises(ValueError, match="Cannot reflect"):
            mgr.reflect("sr3", insight="Should fail")

    def test_reflect_from_work_phase_fails(self, mgr):
        mgr.init_session("sr4")
        mgr.start_work("sr4")
        with pytest.raises(ValueError, match="Cannot reflect"):
            mgr.reflect("sr4", insight="Should fail")

    def test_carry_forward_persists_across_cycles(self, mgr):
        mgr.init_session("sr5")

        # Cycle 1
        mgr.start_work("sr5")
        mgr.end_work("sr5", cognitive_load=6)
        mgr.reflect("sr5", insight="Cycle 1", carry_forward="Focus on API")
        assert mgr.get_session("sr5").latest_carry_forward == "Focus on API"

        # Cycle 2
        mgr.start_work("sr5")
        mgr.end_work("sr5", cognitive_load=5)
        mgr.reflect("sr5", insight="Cycle 2", carry_forward="Write tests")
        session = mgr.get_session("sr5")
        assert session.latest_carry_forward == "Write tests"
        assert len(session.reflections) == 2

    def test_ouroboros_full_loop(self, mgr):
        """Test the complete ouroboros cycle: INIT→WORK→REFLECT→BREAK→WORK→REFLECT→BREAK."""
        mgr.init_session("ouro")

        # First turn of the ouroboros
        session = mgr.start_work("ouro")
        assert session.phase == SessionPhase.WORK
        session = mgr.end_work("ouro", cognitive_load=7)
        assert session.phase == SessionPhase.REFLECT
        session = mgr.reflect("ouro", insight="First turn", carry_forward="Optimize")
        assert session.phase == SessionPhase.BREAK

        # Second turn — the loop feeds back
        session = mgr.start_work("ouro")
        assert session.phase == SessionPhase.WORK
        session = mgr.end_work("ouro", cognitive_load=5)
        assert session.phase == SessionPhase.REFLECT
        session = mgr.reflect("ouro", insight="Second turn", carry_forward="Verify")
        assert session.phase == SessionPhase.BREAK

        assert session.pomodoro_count == 2
        assert len(session.reflections) == 2
        assert session.reflections[0].carry_forward == "Optimize"
        assert session.reflections[1].carry_forward == "Verify"

    def test_reflect_invalid_cognitive_load_after(self, mgr):
        mgr.init_session("sr6")
        mgr.start_work("sr6")
        mgr.end_work("sr6", cognitive_load=5)
        with pytest.raises(ValueError, match="cognitive_load_after must be 1-10"):
            mgr.reflect("sr6", insight="Test", cognitive_load_after=11)

    def test_to_dict_includes_reflections(self, mgr):
        mgr.init_session("sr7")
        mgr.start_work("sr7")
        mgr.end_work("sr7", cognitive_load=6)
        mgr.reflect("sr7", insight="Dict test", carry_forward="Check dict")
        d = mgr.get_session("sr7").to_dict()
        assert len(d["reflections"]) == 1
        assert d["reflections"][0]["insight"] == "Dict test"
        assert d["reflections"][0]["carry_forward"] == "Check dict"
        assert d["latest_carry_forward"] == "Check dict"
