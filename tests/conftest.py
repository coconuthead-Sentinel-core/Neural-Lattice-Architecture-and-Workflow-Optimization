"""Shared pytest fixtures for the Neural Lattice test suite."""

from __future__ import annotations

from datetime import datetime, timezone

import pytest
from fastapi.testclient import TestClient

from neural_lattice.api.app import app, state
from neural_lattice.document_store import DocumentStore
from neural_lattice.metadata_engine import MetadataEngine
from neural_lattice.session_manager import SessionManager
from neural_lattice.zone_engine import ZoneEngine


@pytest.fixture
def store() -> DocumentStore:
    """Fresh in-memory DocumentStore."""
    return DocumentStore(":memory:")


@pytest.fixture
def metadata_engine() -> MetadataEngine:
    """Fresh MetadataEngine instance."""
    return MetadataEngine()


@pytest.fixture
def zone_engine() -> ZoneEngine:
    """Fresh ZoneEngine instance."""
    return ZoneEngine()


@pytest.fixture
def session_mgr() -> SessionManager:
    """Fresh SessionManager instance."""
    return SessionManager()


@pytest.fixture
def client() -> TestClient:
    """TestClient for the FastAPI app with reset state before each test."""
    state.store = DocumentStore(":memory:")
    state.metadata_engine = MetadataEngine()
    state.zone_engine = ZoneEngine()
    state.session_mgr = SessionManager()
    return TestClient(app)


@pytest.fixture
def sample_metadata() -> dict:
    """Return a dict with all 10 required metadata fields (valid)."""
    return {
        "doc_id": "TST-META-001",
        "title": "Sample Metadata Document",
        "zone": "GREEN",
        "protocol": "Onset_Omega_1",
        "artifact_type": "note",
        "cognitive_load": 8,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "dependencies": [],
        "tags": ["sample", "test"],
        "status": "DRAFT",
    }


@pytest.fixture
def sample_document_payload() -> dict:
    """Return a valid dict for POST /api/documents."""
    return {
        "doc_id": "TST-DOC-001",
        "title": "Sample Document",
        "cognitive_load": 8,
        "artifact_type": "note",
        "protocol": "Onset_Omega_1",
        "status": "DRAFT",
        "dependencies": [],
        "tags": ["sample"],
        "content": "Sample content for testing.",
    }
