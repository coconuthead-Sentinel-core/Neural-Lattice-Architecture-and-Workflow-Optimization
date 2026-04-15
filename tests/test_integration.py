"""Integration tests for the Neural Lattice Cognitive Architecture."""

from __future__ import annotations

from fastapi.testclient import TestClient


class TestDocumentLifecycle:
    """Test full document lifecycle: create -> classify zone -> migrate -> archive."""

    def test_create_classify_migrate_archive(self, client: TestClient):
        # 1. Create a document in GREEN zone (cognitive_load=8)
        r = client.post(
            "/api/documents",
            json={
                "doc_id": "INT-LIFE-001",
                "title": "Lifecycle Test",
                "cognitive_load": 8,
                "status": "ACTIVE",
                "tags": ["lifecycle"],
            },
        )
        assert r.status_code == 201
        doc = r.json()
        assert doc["zone"] == "GREEN"

        # 2. Classify confirms zone
        r = client.post("/api/classify", json={"cognitive_load": 8})
        assert r.json()["zone"] == "GREEN"

        # 3. Migrate GREEN -> YELLOW (needs status!=DRAFT and cognitive_load<7)
        r = client.post(
            "/api/migrate",
            json={
                "doc_id": "INT-LIFE-001",
                "target_zone": "YELLOW",
                "cognitive_load": 5,
                "status": "ACTIVE",
            },
        )
        assert r.status_code == 200
        assert r.json()["success"] is True
        assert r.json()["to_zone"] == "YELLOW"

        # 4. Verify the document is now YELLOW with ACTIVE status
        r = client.get("/api/documents/INT-LIFE-001")
        assert r.json()["zone"] == "YELLOW"
        assert r.json()["status"] == "ACTIVE"

        # 5. Migrate YELLOW -> RED (needs cognitive_load<4 and version>=1.0)
        # First update version to 1.0
        client.put("/api/documents/INT-LIFE-001", json={"version": "1.0"})
        r = client.post(
            "/api/migrate",
            json={
                "doc_id": "INT-LIFE-001",
                "target_zone": "RED",
                "cognitive_load": 2,
                "version": "1.0",
            },
        )
        assert r.status_code == 200
        assert r.json()["to_zone"] == "RED"

        # 6. Verify archived status
        r = client.get("/api/documents/INT-LIFE-001")
        assert r.json()["zone"] == "RED"
        assert r.json()["status"] == "ARCHIVED"


class TestMultiFilterSearch:
    """Test search with multiple filters combined."""

    def _seed_documents(self, client: TestClient):
        """Create several documents across zones and types."""
        docs = [
            {
                "doc_id": "INT-SRCH-001",
                "title": "Green Note",
                "cognitive_load": 8,
                "artifact_type": "note",
                "tags": ["alpha"],
                "status": "ACTIVE",
            },
            {
                "doc_id": "INT-SRCH-002",
                "title": "Green Code",
                "cognitive_load": 9,
                "artifact_type": "code",
                "tags": ["alpha", "beta"],
                "status": "ACTIVE",
            },
            {
                "doc_id": "INT-SRCH-003",
                "title": "Yellow Spec",
                "cognitive_load": 5,
                "artifact_type": "spec",
                "tags": ["beta"],
                "status": "DRAFT",
            },
            {
                "doc_id": "INT-SRCH-004",
                "title": "Red Report",
                "cognitive_load": 2,
                "artifact_type": "report",
                "tags": ["gamma"],
                "status": "DRAFT",
            },
        ]
        for d in docs:
            r = client.post("/api/documents", json=d)
            assert r.status_code == 201

    def test_search_zone_and_tag(self, client: TestClient):
        self._seed_documents(client)
        r = client.get("/api/search?zone=GREEN&tag=alpha")
        results = r.json()
        assert len(results) == 2
        for doc in results:
            assert doc["zone"] == "GREEN"
            assert "alpha" in doc["tags"]

    def test_search_zone_and_status(self, client: TestClient):
        self._seed_documents(client)
        r = client.get("/api/search?zone=GREEN&status=ACTIVE")
        results = r.json()
        assert len(results) == 2
        for doc in results:
            assert doc["zone"] == "GREEN"
            assert doc["status"] == "ACTIVE"

    def test_search_zone_and_artifact_type(self, client: TestClient):
        self._seed_documents(client)
        r = client.get("/api/search?zone=GREEN&artifact_type=code")
        results = r.json()
        assert len(results) == 1
        assert results[0]["artifact_type"] == "code"
        assert results[0]["zone"] == "GREEN"


class TestSessionDocumentInteraction:
    """Test session + document interaction flow."""

    def test_session_work_create_document_end_work_with_load(self, client: TestClient):
        # 1. Create a session
        r = client.post("/api/sessions", json={"session_id": "int-sess-001"})
        assert r.status_code == 201
        assert r.json()["phase"] == "INIT"

        # 2. Start work
        r = client.post("/api/sessions/int-sess-001/work")
        assert r.json()["phase"] == "WORK"

        # 3. Create a document during the work block
        r = client.post(
            "/api/documents",
            json={
                "doc_id": "INT-SESS-001",
                "title": "Document Created During Session",
                "cognitive_load": 7,
                "tags": ["session_work"],
            },
        )
        assert r.status_code == 201

        # 4. End work with cognitive load — enters REFLECT phase
        r = client.post(
            "/api/sessions/int-sess-001/end-work",
            json={
                "cognitive_load": 7,
                "notes": "Created INT-SESS-001",
            },
        )
        assert r.json()["phase"] == "REFLECT"
        assert r.json()["pomodoro_count"] == 1
        assert 7 in r.json()["cognitive_loads"]

        # 5. Verify load is recorded in the session
        r = client.get("/api/sessions/int-sess-001")
        session = r.json()
        assert session["cognitive_loads"] == [7]
        assert session["average_cognitive_load"] == 7.0
        assert session["work_blocks"][-1]["cognitive_load"] == 7
        assert session["work_blocks"][-1]["notes"] == "Created INT-SESS-001"


class TestCORSHeaders:
    """Test CORS headers for the allowed origin."""

    def test_cors_preflight(self, client: TestClient):
        r = client.options(
            "/api/health",
            headers={
                "Origin": "http://localhost:5173",
                "Access-Control-Request-Method": "GET",
                "Access-Control-Request-Headers": "Content-Type",
            },
        )
        assert r.status_code == 200
        assert "http://localhost:5173" in r.headers.get("access-control-allow-origin", "")
        assert "GET" in r.headers.get("access-control-allow-methods", "")


class TestZoneSummaryAccuracy:
    """Test zone summary accuracy after creating multiple documents."""

    def test_zone_summary_counts(self, client: TestClient):
        # Create documents in each zone
        docs = [
            {"doc_id": "INT-ZSUM-001", "title": "Green1", "cognitive_load": 8},
            {"doc_id": "INT-ZSUM-002", "title": "Green2", "cognitive_load": 9},
            {"doc_id": "INT-ZSUM-003", "title": "Yellow1", "cognitive_load": 5},
            {"doc_id": "INT-ZSUM-004", "title": "Red1", "cognitive_load": 2},
            {"doc_id": "INT-ZSUM-005", "title": "Red2", "cognitive_load": 1},
            {"doc_id": "INT-ZSUM-006", "title": "Red3", "cognitive_load": 3},
        ]
        for d in docs:
            r = client.post("/api/documents", json=d)
            assert r.status_code == 201

        r = client.get("/api/zones/summary")
        summary = r.json()
        assert summary["GREEN"] == 2
        assert summary["YELLOW"] == 1
        assert summary["RED"] == 3


class TestUpdateThenMigrate:
    """Test updating a document and then migrating it."""

    def test_update_then_migrate(self, client: TestClient):
        # Create document
        client.post(
            "/api/documents",
            json={
                "doc_id": "INT-UMIG-001",
                "title": "Update Then Migrate",
                "cognitive_load": 8,
                "status": "ACTIVE",
            },
        )

        # Update the title and content
        r = client.put(
            "/api/documents/INT-UMIG-001",
            json={
                "title": "Updated Title",
                "content": "New content after update",
            },
        )
        assert r.status_code == 200
        assert r.json()["title"] == "Updated Title"
        assert r.json()["content"] == "New content after update"

        # Migrate GREEN -> YELLOW
        r = client.post(
            "/api/migrate",
            json={
                "doc_id": "INT-UMIG-001",
                "target_zone": "YELLOW",
                "cognitive_load": 5,
                "status": "ACTIVE",
            },
        )
        assert r.status_code == 200
        assert r.json()["to_zone"] == "YELLOW"

        # Verify updated fields persist after migration
        r = client.get("/api/documents/INT-UMIG-001")
        doc = r.json()
        assert doc["title"] == "Updated Title"
        assert doc["content"] == "New content after update"
        assert doc["zone"] == "YELLOW"
