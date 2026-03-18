"""Application configuration loaded from environment variables."""

from __future__ import annotations

import os
from dataclasses import dataclass, field
from pathlib import Path


@dataclass(frozen=True)
class Settings:
    """Immutable application settings."""

    # Paths
    base_dir: Path = field(default_factory=lambda: Path(os.getenv("NLCA_BASE_DIR", ".")))
    db_path: Path = field(default_factory=lambda: Path(os.getenv("NLCA_DB_PATH", "nlca.db")))

    # Zone directories (relative to base_dir)
    green_dir: str = "active"
    yellow_dir: str = "synthesis"
    red_dir: str = "archive"

    # API
    api_host: str = field(default_factory=lambda: os.getenv("NLCA_API_HOST", "127.0.0.1"))
    api_port: int = field(default_factory=lambda: int(os.getenv("NLCA_API_PORT", "8000")))
    debug: bool = field(default_factory=lambda: os.getenv("NLCA_DEBUG", "false").lower() == "true")

    # Session defaults
    pomodoro_minutes: int = field(default_factory=lambda: int(os.getenv("NLCA_POMODORO_MIN", "25")))
    break_minutes: int = field(default_factory=lambda: int(os.getenv("NLCA_BREAK_MIN", "5")))
    long_break_minutes: int = field(default_factory=lambda: int(os.getenv("NLCA_LONG_BREAK_MIN", "15")))
    long_break_interval: int = 4  # every N pomodoros

    def zone_path(self, zone: str) -> Path:
        mapping = {"GREEN": self.green_dir, "YELLOW": self.yellow_dir, "RED": self.red_dir}
        return self.base_dir / mapping[zone]

    def ensure_directories(self) -> None:
        for zone in ("GREEN", "YELLOW", "RED"):
            self.zone_path(zone).mkdir(parents=True, exist_ok=True)
        (self.base_dir / "meta").mkdir(parents=True, exist_ok=True)


def get_settings() -> Settings:
    return Settings()
