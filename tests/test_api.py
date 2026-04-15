"""Tests for the FastAPI REST API endpoints."""

import pytest
from fastapi.testclient import TestClient

from neural_lattice.api.app import app, state
from neural_lattice.document_store import DocumentStore
from neural_lattice.session_manager import SessionManager


@pytest.fixture(autouse=True)
def fresh_state():
    """Reset shared state before each test."""
    state.store = DocumentStore(":memory:")
    state.session_mgr = SessionManager()
    yield


@pytest.fixture
def client():
    return TestClient(app)


# ==========================================================================
# Health
# ==========================================================================


class TestHealth:
    def test_health(self, client):
        r = client.get("/api/health")
        assert r.status_code == 200
        assert r.json()["status"] == "healthy"


# ==========================================================================
# Documents CRUD
# ==========================================================================


class TestDocumentsCRUD:
    def test_create_document(self, client):
        r = client.post(
            "/api/documents",
            json={
                "doc_id": "TST-DOC-001",
                "title": "Test Document",
                "cognitive_load": 8,
                "content": "Hello",
            },
        )
        assert r.status_code == 201
        assert r.json()["doc_id"] == "TST-DOC-001"
        assert r.json()["zone"] == "GREEN"

    def test_get_document(self, client):
        client.post(
            "/api/documents",
            json={
                "doc_id": "TST-DOC-001",
                "title": "Test",
                "cognitive_load": 8,
            },
        )
        r = client.get("/api/documents/TST-DOC-001")
        assert r.status_code == 200
        assert r.json()["title"] == "Test"

    def test_get_missing_404(self, client):
        r = client.get("/api/documents/NOPE-DOC-999")
        assert r.status_code == 404

    def test_list_documents(self, client):
        client.post(
            "/api/documents",
            json={
                "doc_id": "TST-DOC-001",
                "title": "First",
                "cognitive_load": 8,
            },
        )
        client.post(
            "/api/documents",
            json={
                "doc_id": "TST-DOC-002",
                "title": "Second",
                "cognitive_load": 5,
            },
        )
        r = client.get("/api/documents")
        assert len(r.json()) == 2

    def test_update_document(self, client):
        client.post(
            "/api/documents",
            json={
                "doc_id": "TST-DOC-001",
                "title": "Original",
                "cognitive_load": 8,
            },
        )
        r = client.put("/api/documents/TST-DOC-001", json={"title": "Updated"})
        assert r.status_code == 200
        assert r.json()["title"] == "Updated"

    def test_delete_document(self, client):
        client.post(
            "/api/documents",
            json={
                "doc_id": "TST-DOC-001",
                "title": "Test",
                "cognitive_load": 8,
            },
        )
        r = client.delete("/api/documents/TST-DOC-001")
        assert r.status_code == 200
        assert r.json()["deleted"] is True

    def test_delete_missing_404(self, client):
        r = client.delete("/api/documents/NOPE-DOC-999")
        assert r.status_code == 404

    def test_duplicate_409(self, client):
        body = {"doc_id": "TST-DOC-001", "title": "Test", "cognitive_load": 8}
        client.post("/api/documents", json=body)
        r = client.post("/api/documents", json=body)
        assert r.status_code == 409


# ==========================================================================
# Search
# ==========================================================================


class TestSearch:
    def test_search_by_zone(self, client):
        client.post(
            "/api/documents",
            json={
                "doc_id": "TST-DOC-001",
                "title": "Green",
                "cognitive_load": 8,
            },
        )
        r = client.get("/api/search?zone=GREEN")
        assert len(r.json()) == 1

    def test_search_by_tag(self, client):
        client.post(
            "/api/documents",
            json={
                "doc_id": "TST-DOC-001",
                "title": "Tagged",
                "cognitive_load": 8,
                "tags": ["api_test"],
            },
        )
        r = client.get("/api/search?tag=api_test")
        assert len(r.json()) == 1

    def test_search_empty(self, client):
        r = client.get("/api/search?zone=RED")
        assert r.json() == []


# ==========================================================================
# Zone operations
# ==========================================================================


class TestZoneOps:
    def test_classify(self, client):
        r = client.post("/api/classify", json={"cognitive_load": 8})
        assert r.json()["zone"] == "GREEN"

    def test_classify_yellow(self, client):
        r = client.post("/api/classify", json={"cognitive_load": 5})
        assert r.json()["zone"] == "YELLOW"

    def test_migrate_success(self, client):
        client.post(
            "/api/documents",
            json={
                "doc_id": "TST-DOC-001",
                "title": "Migrate Me",
                "cognitive_load": 8,
                "status": "ACTIVE",
            },
        )
        r = client.post(
            "/api/migrate",
            json={
                "doc_id": "TST-DOC-001",
                "target_zone": "YELLOW",
                "cognitive_load": 5,
                "status": "ACTIVE",
            },
        )
        assert r.status_code == 200
        assert r.json()["success"] is True
        assert r.json()["to_zone"] == "YELLOW"

    def test_migrate_guard_violation(self, client):
        client.post(
            "/api/documents",
            json={
                "doc_id": "TST-DOC-001",
                "title": "Stay Put",
                "cognitive_load": 8,
                "status": "DRAFT",
            },
        )
        r = client.post(
            "/api/migrate",
            json={
                "doc_id": "TST-DOC-001",
                "target_zone": "YELLOW",
                "cognitive_load": 5,
                "status": "DRAFT",
            },
        )
        assert r.status_code == 422

    def test_zone_summary(self, client):
        client.post(
            "/api/documents",
            json={
                "doc_id": "TST-DOC-001",
                "title": "Test",
                "cognitive_load": 8,
            },
        )
        r = client.get("/api/zones/summary")
        assert r.json()["GREEN"] == 1


# ==========================================================================
# Validation
# ==========================================================================


class TestValidation:
    def test_validate_valid(self, client):
        r = client.post(
            "/api/validate",
            json={
                "doc_id": "TST-DOC-001",
                "title": "Test",
                "zone": "GREEN",
                "protocol": "Onset_Omega_1",
                "artifact_type": "note",
                "cognitive_load": 8,
                "timestamp": "2026-03-17T00:00:00+00:00",
                "dependencies": [],
                "tags": [],
                "status": "DRAFT",
            },
        )
        assert r.json()["valid"] is True

    def test_validate_invalid(self, client):
        r = client.post(
            "/api/validate",
            json={
                "doc_id": "bad",
                "title": "Test",
                "zone": "GREEN",
                "protocol": "Onset_Omega_1",
                "artifact_type": "note",
                "cognitive_load": 8,
                "timestamp": "2026-03-17T00:00:00+00:00",
                "dependencies": [],
                "tags": [],
                "status": "DRAFT",
            },
        )
        assert r.json()["valid"] is False


# ==========================================================================
# Sessions
# ==========================================================================


class TestSessions:
    def test_create_session(self, client):
        r = client.post("/api/sessions", json={"session_id": "s1"})
        assert r.status_code == 201
        assert r.json()["phase"] == "INIT"

    def test_session_lifecycle(self, client):
        client.post("/api/sessions", json={"session_id": "s1"})
        r = client.post("/api/sessions/s1/work")
        assert r.json()["phase"] == "WORK"

        r = client.post("/api/sessions/s1/end-work", json={"cognitive_load": 7})
        assert r.json()["phase"] == "REFLECT"
        assert r.json()["pomodoro_count"] == 1

        r = client.post("/api/sessions/s1/wrap-up")
        assert r.json()["phase"] == "WRAP_UP"

        r = client.post("/api/sessions/s1/close")
        assert r.json()["phase"] == "CLOSED"

    def test_list_sessions(self, client):
        client.post("/api/sessions", json={"session_id": "s1"})
        client.post("/api/sessions", json={"session_id": "s2"})
        r = client.get("/api/sessions")
        assert len(r.json()) == 2

    def test_get_session_404(self, client):
        r = client.get("/api/sessions/nonexistent")
        assert r.status_code == 404

    def test_record_cognitive_load(self, client):
        client.post("/api/sessions", json={"session_id": "s1"})
        r = client.post("/api/sessions/s1/load", json={"cognitive_load": 8})
        assert r.json()["cognitive_loads"] == [8]
