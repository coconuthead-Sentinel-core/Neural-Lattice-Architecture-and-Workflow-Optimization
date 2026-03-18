"""Tests for configuration module."""

from neural_lattice.meta.config import Settings, get_settings


class TestSettings:
    def test_defaults(self):
        s = Settings()
        assert s.api_host == "127.0.0.1"
        assert s.api_port == 8000
        assert s.pomodoro_minutes == 25

    def test_zone_path(self):
        s = Settings()
        green = s.zone_path("GREEN")
        assert str(green).endswith("active")
        yellow = s.zone_path("YELLOW")
        assert str(yellow).endswith("synthesis")
        red = s.zone_path("RED")
        assert str(red).endswith("archive")

    def test_get_settings(self):
        s = get_settings()
        assert isinstance(s, Settings)
