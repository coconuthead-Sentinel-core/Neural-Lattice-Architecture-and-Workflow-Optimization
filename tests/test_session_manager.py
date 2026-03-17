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
        assert session.phase == SessionPhase.BREAK
        assert session.pomodoro_count == 1
        assert session.cognitive_loads == [7]

    def test_long_break_after_4_pomodoros(self, mgr):
        mgr.init_session("s1")
        for i in range(4):
            mgr.start_work("s1")
            mgr.end_work("s1", cognitive_load=5)
        session = mgr.get_session("s1")
        assert session.phase == SessionPhase.LONG_BREAK
        assert session.pomodoro_count == 4

    def test_wrap_up_and_close(self, mgr):
        mgr.init_session("s1")
        mgr.start_work("s1")
        mgr.end_work("s1")
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
