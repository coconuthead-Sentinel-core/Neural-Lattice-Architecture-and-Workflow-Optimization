"""Edge case tests for the Neural Lattice Cognitive Architecture."""

from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path

import pytest
from pydantic import ValidationError

from neural_lattice.api.models import DocumentUpdate, ValidateRequest
from neural_lattice.document_store import DocumentStore
from neural_lattice.meta.config import Settings, get_settings
from neural_lattice.meta.schemas import ZoneEnum
from neural_lattice.metadata_engine import MetadataEngine
from neural_lattice.session_manager import SessionManager
from neural_lattice.zone_engine import TransitionError, ZoneEngine

# ==========================================================================
# MetadataEngine edge cases
# ==========================================================================


class TestMetadataEngineEdgeCases:
    def test_malformed_yaml_parsing(self, metadata_engine: MetadataEngine):
        """Non-YAML string should raise or return a non-dict result."""
        import yaml

        # Truly malformed YAML raises a ScannerError
        with pytest.raises(yaml.scanner.ScannerError):
            metadata_engine.from_yaml("this is not: valid: yaml: [broken")

        # A simple string parses to the string itself, not a dict
        plain = metadata_engine.from_yaml("just a plain string")
        assert isinstance(plain, str)

    def test_extract_frontmatter_no_delimiters(self, metadata_engine: MetadataEngine):
        """Content without --- delimiters returns (None, original content)."""
        content = "This is just regular content without any frontmatter."
        meta, body = metadata_engine.extract_frontmatter(content)
        assert meta is None
        assert body == content

    def test_extract_frontmatter_single_delimiter(self, metadata_engine: MetadataEngine):
        """Content with only one --- delimiter returns (None, original content)."""
        content = "---\nSome text without a closing delimiter"
        meta, body = metadata_engine.extract_frontmatter(content)
        assert meta is None
        assert body == content

    def test_generate_with_explicit_zone_override(self, metadata_engine: MetadataEngine):
        """Explicit zone parameter should override auto-classification."""
        # cognitive_load=8 would auto-classify to GREEN, but we force YELLOW
        meta = metadata_engine.generate(
            doc_id="TST-ZONE-001",
            title="Zone Override Test",
            cognitive_load=8,
            zone="YELLOW",
        )
        assert meta["zone"] == "YELLOW"
        assert meta["cognitive_load"] == 8

    def test_generate_with_zone_enum_override(self, metadata_engine: MetadataEngine):
        """Explicit ZoneEnum should be accepted."""
        meta = metadata_engine.generate(
            doc_id="TST-ZONE-002",
            title="Enum Override",
            cognitive_load=8,
            zone=ZoneEnum.RED,
        )
        assert meta["zone"] == "RED"


# ==========================================================================
# DocumentStore search edge cases
# ==========================================================================


class TestDocumentStoreSearchEdgeCases:
    def _create_doc(self, store: DocumentStore, doc_id: str, **overrides):
        """Helper to create a document with defaults."""
        meta = {
            "doc_id": doc_id,
            "title": f"Doc {doc_id}",
            "zone": "GREEN",
            "protocol": "Onset_Omega_1",
            "artifact_type": "note",
            "cognitive_load": 8,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "dependencies": [],
            "tags": [],
            "status": "DRAFT",
        }
        meta.update(overrides)
        return store.create(meta)

    def test_search_with_status_filter(self, store: DocumentStore):
        self._create_doc(store, "TST-STAT-001", status="DRAFT")
        self._create_doc(store, "TST-STAT-002", status="ACTIVE")
        self._create_doc(store, "TST-STAT-003", status="DRAFT")

        results = store.search(status="DRAFT")
        assert len(results) == 2
        for r in results:
            assert r["status"] == "DRAFT"

        results = store.search(status="ACTIVE")
        assert len(results) == 1
        assert results[0]["doc_id"] == "TST-STAT-002"

    def test_search_with_artifact_type_filter(self, store: DocumentStore):
        self._create_doc(store, "TST-ATYP-001", artifact_type="code")
        self._create_doc(store, "TST-ATYP-002", artifact_type="spec")
        self._create_doc(store, "TST-ATYP-003", artifact_type="code")

        results = store.search(artifact_type="code")
        assert len(results) == 2
        for r in results:
            assert r["artifact_type"] == "code"

        results = store.search(artifact_type="spec")
        assert len(results) == 1

    def test_search_no_results(self, store: DocumentStore):
        results = store.search(zone="RED", status="ARCHIVED")
        assert results == []


# ==========================================================================
# Config edge cases
# ==========================================================================


class TestConfigEdgeCases:
    def test_env_override_db_path(self, monkeypatch):
        monkeypatch.setenv("NLCA_DB_PATH", "/tmp/test_nlca.db")
        settings = get_settings()
        assert settings.db_path == Path("/tmp/test_nlca.db")

    def test_env_override_pomodoro_min(self, monkeypatch):
        monkeypatch.setenv("NLCA_POMODORO_MIN", "50")
        settings = get_settings()
        assert settings.pomodoro_minutes == 50

    def test_env_override_break_min(self, monkeypatch):
        monkeypatch.setenv("NLCA_BREAK_MIN", "10")
        settings = get_settings()
        assert settings.break_minutes == 10

    def test_env_override_long_break_min(self, monkeypatch):
        monkeypatch.setenv("NLCA_LONG_BREAK_MIN", "30")
        settings = get_settings()
        assert settings.long_break_minutes == 30

    def test_env_override_api_host(self, monkeypatch):
        monkeypatch.setenv("NLCA_API_HOST", "0.0.0.0")
        settings = get_settings()
        assert settings.api_host == "0.0.0.0"

    def test_env_override_debug(self, monkeypatch):
        monkeypatch.setenv("NLCA_DEBUG", "true")
        settings = get_settings()
        assert settings.debug is True

    def test_ensure_directories_creates_zone_dirs(self, tmp_path, monkeypatch):
        monkeypatch.setenv("NLCA_BASE_DIR", str(tmp_path))
        settings = Settings(base_dir=tmp_path)
        settings.ensure_directories()

        assert (tmp_path / "active").is_dir()
        assert (tmp_path / "synthesis").is_dir()
        assert (tmp_path / "archive").is_dir()
        assert (tmp_path / "meta").is_dir()


# ==========================================================================
# SessionManager edge cases
# ==========================================================================


class TestSessionManagerEdgeCases:
    def test_custom_pomodoro_intervals(self):
        mgr = SessionManager(pomodoro_minutes=50, break_minutes=10)
        session = mgr.init_session("custom-sess")
        assert session.pomodoro_minutes == 50
        assert session.break_minutes == 10

    def test_custom_long_break_settings(self):
        mgr = SessionManager(long_break_minutes=30, long_break_interval=2)
        session = mgr.init_session("lb-sess")
        assert session.long_break_minutes == 30
        assert session.long_break_interval == 2

    def test_end_work_with_notes(self, session_mgr: SessionManager):
        session = session_mgr.init_session("notes-sess")
        session_mgr.start_work("notes-sess")
        session = session_mgr.end_work("notes-sess", cognitive_load=5, notes="Did some refactoring")
        assert session.work_blocks[-1].notes == "Did some refactoring"
        assert session.work_blocks[-1].cognitive_load == 5

    def test_end_work_without_load(self, session_mgr: SessionManager):
        session = session_mgr.init_session("no-load-sess")
        session_mgr.start_work("no-load-sess")
        session = session_mgr.end_work("no-load-sess")
        assert session.work_blocks[-1].cognitive_load is None
        assert session.cognitive_loads == []

    def test_long_break_triggers_after_interval(self):
        mgr = SessionManager(long_break_interval=2)
        session = mgr.init_session("lb-test")

        # First pomodoro -> REFLECT -> BREAK
        mgr.start_work("lb-test")
        session = mgr.end_work("lb-test", cognitive_load=5)
        assert session.phase.value == "REFLECT"
        session = mgr.reflect("lb-test", insight="First cycle done")
        assert session.phase.value == "BREAK"

        # Second pomodoro -> REFLECT -> LONG_BREAK
        mgr.start_work("lb-test")
        session = mgr.end_work("lb-test", cognitive_load=5)
        assert session.phase.value == "REFLECT"
        session = mgr.reflect("lb-test", insight="Second cycle done")
        assert session.phase.value == "LONG_BREAK"

    def test_cannot_start_work_from_work(self, session_mgr: SessionManager):
        session_mgr.init_session("bad-flow")
        session_mgr.start_work("bad-flow")
        with pytest.raises(ValueError, match="Cannot start work"):
            session_mgr.start_work("bad-flow")

    def test_session_not_found(self, session_mgr: SessionManager):
        with pytest.raises(KeyError, match="Session not found"):
            session_mgr.get_session("nonexistent")


# ==========================================================================
# Pydantic model validator edge cases
# ==========================================================================


class TestPydanticModelValidators:
    def test_document_update_invalid_tags(self):
        """DocumentUpdate with tags containing invalid characters should fail."""
        with pytest.raises(ValidationError):
            # DocumentUpdate doesn't have the tag validator from DocumentCreate,
            # but cognitive_load out of range should fail
            DocumentUpdate(cognitive_load=0)

    def test_document_update_cognitive_load_too_high(self):
        with pytest.raises(ValidationError):
            DocumentUpdate(cognitive_load=11)

    def test_validate_request_missing_required_fields(self):
        """ValidateRequest requires all 10 metadata fields."""
        with pytest.raises(ValidationError):
            ValidateRequest(
                doc_id="TST-VAL-001",
                title="Test",
                # Missing zone, protocol, artifact_type, etc.
            )

    def test_validate_request_all_fields_present(self):
        """ValidateRequest with all fields should succeed."""
        vr = ValidateRequest(
            doc_id="TST-VAL-001",
            title="Test",
            zone="GREEN",
            protocol="Onset_Omega_1",
            artifact_type="note",
            cognitive_load=8,
            timestamp="2026-03-17T00:00:00+00:00",
            dependencies=[],
            tags=[],
            status="DRAFT",
        )
        assert vr.doc_id == "TST-VAL-001"

    def test_document_create_invalid_tags(self):
        """DocumentCreate with uppercase tags should fail validation."""
        from neural_lattice.api.models import DocumentCreate

        with pytest.raises(ValidationError, match="Invalid tag"):
            DocumentCreate(
                doc_id="TST-TAG-001",
                title="Bad Tags",
                cognitive_load=8,
                tags=["UPPERCASE"],
            )


# ==========================================================================
# ZoneEngine version edge cases
# ==========================================================================


class TestZoneEngineVersionEdgeCases:
    def test_version_below_one_fails_yellow_to_red(self, zone_engine: ZoneEngine):
        """Version '0.9999' should fail the YELLOW->RED guard."""
        can, error = zone_engine.can_transition(
            ZoneEnum.YELLOW,
            ZoneEnum.RED,
            cognitive_load=2,
            version="0.9999",
        )
        assert can is False
        assert "version must be >= 1.0" in error

    def test_version_one_passes_yellow_to_red(self, zone_engine: ZoneEngine):
        """Version '1.0' should pass the YELLOW->RED guard."""
        can, error = zone_engine.can_transition(
            ZoneEnum.YELLOW,
            ZoneEnum.RED,
            cognitive_load=2,
            version="1.0",
        )
        assert can is True
        assert error is None

    def test_version_above_one_passes(self, zone_engine: ZoneEngine):
        """Version '2.5' should pass the YELLOW->RED guard."""
        can, error = zone_engine.can_transition(
            ZoneEnum.YELLOW,
            ZoneEnum.RED,
            cognitive_load=2,
            version="2.5",
        )
        assert can is True

    def test_invalid_version_string(self, zone_engine: ZoneEngine):
        """Non-numeric version should fail the YELLOW->RED guard."""
        can, error = zone_engine.can_transition(
            ZoneEnum.YELLOW,
            ZoneEnum.RED,
            cognitive_load=2,
            version="abc",
        )
        assert can is False
        assert "Invalid version" in error

    def test_transition_raises_on_guard_failure(self, zone_engine: ZoneEngine):
        """transition() should raise TransitionError when guard fails."""
        with pytest.raises(TransitionError, match="version must be >= 1.0"):
            zone_engine.transition(
                ZoneEnum.YELLOW,
                ZoneEnum.RED,
                cognitive_load=2,
                version="0.9999",
            )

    def test_invalid_transition_path(self, zone_engine: ZoneEngine):
        """GREEN->RED has no valid transition."""
        can, error = zone_engine.can_transition(ZoneEnum.GREEN, ZoneEnum.RED)
        assert can is False
        assert "No valid transition" in error
