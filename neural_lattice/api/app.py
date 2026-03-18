"""FastAPI application — REST API for the Neural Lattice Cognitive Architecture."""

from __future__ import annotations

import sys
from typing import Any

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware

from neural_lattice.api.models import (
    DocumentCreate,
    DocumentUpdate,
    ZoneMigrateRequest,
    ClassifyRequest,
    ValidateRequest,
    SessionCreateRequest,
    WorkEndRequest,
    CognitiveLoadRequest,
)
from neural_lattice.document_store import DocumentStore
from neural_lattice.metadata_engine import MetadataEngine
from neural_lattice.zone_engine import ZoneEngine, TransitionError
from neural_lattice.session_manager import SessionManager
from neural_lattice.meta.schemas import ZoneEnum, validate_metadata

app = FastAPI(
    title="Neural Lattice Cognitive Architecture",
    description="API for zone-based document management with cognitive load tracking",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_methods=["*"],
    allow_headers=["*"],
)


# ---------------------------------------------------------------------------
# Mutable state holder — tests swap these via the module object
# ---------------------------------------------------------------------------
class _State:
    store: DocumentStore = DocumentStore()
    metadata_engine: MetadataEngine = MetadataEngine()
    zone_engine: ZoneEngine = ZoneEngine()
    session_mgr: SessionManager = SessionManager()


state = _State()


# ==========================================================================
# Health
# ==========================================================================

@app.get("/api/health")
def health_check():
    """Return service health status and API version."""
    return {"status": "healthy", "version": "0.1.0"}


# ==========================================================================
# Documents CRUD
# ==========================================================================

@app.post("/api/documents", status_code=201)
def create_document(body: DocumentCreate):
    """Create a new document with generated metadata. Returns 409 if doc_id already exists."""
    meta = state.metadata_engine.generate(
        doc_id=body.doc_id,
        title=body.title,
        cognitive_load=body.cognitive_load,
        artifact_type=body.artifact_type,
        protocol=body.protocol,
        status=body.status,
        dependencies=body.dependencies,
        tags=body.tags,
        zone=body.zone,
    )
    try:
        doc = state.store.create(meta, content=body.content)
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))
    except Exception as e:
        if "UNIQUE constraint" in str(e):
            raise HTTPException(status_code=409, detail=f"Document {body.doc_id} already exists")
        raise
    return doc


@app.get("/api/documents")
def list_documents():
    """Return all documents in the store."""
    return state.store.list_all()


@app.get("/api/documents/{doc_id}")
def get_document(doc_id: str):
    """Retrieve a single document by its ID. Returns 404 if not found."""
    doc = state.store.get(doc_id)
    if doc is None:
        raise HTTPException(status_code=404, detail=f"Document not found: {doc_id}")
    return doc


@app.put("/api/documents/{doc_id}")
def update_document(doc_id: str, body: DocumentUpdate):
    """Update fields on an existing document. Only non-null fields are applied."""
    updates = body.model_dump(exclude_none=True)
    try:
        doc = state.store.update(doc_id, updates)
    except KeyError:
        raise HTTPException(status_code=404, detail=f"Document not found: {doc_id}")
    return doc


@app.delete("/api/documents/{doc_id}")
def delete_document(doc_id: str):
    """Delete a document by ID. Returns 404 if not found."""
    deleted = state.store.delete(doc_id)
    if not deleted:
        raise HTTPException(status_code=404, detail=f"Document not found: {doc_id}")
    return {"deleted": True, "doc_id": doc_id}


# ==========================================================================
# Search
# ==========================================================================

@app.get("/api/search")
def search_documents(
    zone: str | None = Query(None),
    status: str | None = Query(None),
    tag: str | None = Query(None),
    artifact_type: str | None = Query(None),
    q: str | None = Query(None),
):
    """Search documents by zone, status, tag, artifact_type, or free-text query."""
    return state.store.search(zone=zone, status=status, tag=tag, artifact_type=artifact_type, q=q)


# ==========================================================================
# Zone operations
# ==========================================================================

@app.post("/api/classify")
def classify_zone(body: ClassifyRequest):
    """Classify a cognitive load value (1-10) into a zone (GREEN/YELLOW/RED)."""
    zone = state.zone_engine.classify_zone(body.cognitive_load)
    return {"cognitive_load": body.cognitive_load, "zone": zone.value}


@app.post("/api/migrate")
def migrate_document(body: ZoneMigrateRequest):
    """Migrate a document to a new zone, enforcing transition rules and updating status."""
    doc = state.store.get(body.doc_id)
    if doc is None:
        raise HTTPException(status_code=404, detail=f"Document not found: {body.doc_id}")

    from_zone = ZoneEnum(doc["zone"])
    to_zone = ZoneEnum(body.target_zone)

    if from_zone == to_zone:
        return {"message": "Already in target zone", "zone": to_zone.value}

    try:
        result = state.zone_engine.transition(
            from_zone=from_zone,
            to_zone=to_zone,
            cognitive_load=body.cognitive_load,
            status=body.status,
            version=body.version,
            revision_needed=body.revision_needed,
            scope_change_approved=body.scope_change_approved,
        )
    except TransitionError as e:
        raise HTTPException(status_code=422, detail=str(e))

    new_status = state.zone_engine.get_new_status(from_zone, to_zone)
    state.store.update(body.doc_id, {
        "zone": to_zone.value,
        "status": new_status.value,
        "cognitive_load": body.cognitive_load,
    })

    return {
        "success": True,
        "from_zone": result.from_zone.value,
        "to_zone": result.to_zone.value,
        "new_status": new_status.value,
        "timestamp": result.timestamp,
        "message": result.message,
    }


@app.get("/api/zones/summary")
def zone_summary():
    """Return document counts grouped by zone."""
    return state.store.count_by_zone()


# ==========================================================================
# Validation
# ==========================================================================

@app.post("/api/validate")
def validate_document(body: ValidateRequest):
    """Validate document metadata against schema rules. Returns validity status and errors."""
    meta = body.model_dump()
    errors = validate_metadata(meta)
    return {"valid": len(errors) == 0, "errors": errors}


# ==========================================================================
# Session management
# ==========================================================================

@app.post("/api/sessions", status_code=201)
def create_session(body: SessionCreateRequest | None = None):
    """Create a new work session, optionally with a specified session ID."""
    sid = body.session_id if body else None
    session = state.session_mgr.init_session(session_id=sid)
    return session.to_dict()


@app.get("/api/sessions")
def list_sessions():
    """Return all active and closed sessions."""
    return [s.to_dict() for s in state.session_mgr.list_sessions()]


@app.get("/api/sessions/{session_id}")
def get_session(session_id: str):
    """Retrieve a session by ID. Returns 404 if not found."""
    try:
        session = state.session_mgr.get_session(session_id)
    except KeyError:
        raise HTTPException(status_code=404, detail=f"Session not found: {session_id}")
    return session.to_dict()


@app.post("/api/sessions/{session_id}/work")
def start_work(session_id: str):
    """Begin a work interval for the given session. Returns 422 if already working."""
    try:
        session = state.session_mgr.start_work(session_id)
    except KeyError:
        raise HTTPException(status_code=404, detail=f"Session not found: {session_id}")
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))
    return session.to_dict()


@app.post("/api/sessions/{session_id}/end-work")
def end_work(session_id: str, body: WorkEndRequest | None = None):
    """End the current work interval, optionally recording cognitive load and notes."""
    try:
        session = state.session_mgr.end_work(
            session_id,
            cognitive_load=body.cognitive_load if body else None,
            notes=body.notes if body else "",
        )
    except KeyError:
        raise HTTPException(status_code=404, detail=f"Session not found: {session_id}")
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))
    return session.to_dict()


@app.post("/api/sessions/{session_id}/load")
def record_cognitive_load(session_id: str, body: CognitiveLoadRequest):
    """Record a cognitive load measurement (1-10) for the session."""
    try:
        session = state.session_mgr.record_load(session_id, body.cognitive_load)
    except KeyError:
        raise HTTPException(status_code=404, detail=f"Session not found: {session_id}")
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))
    return session.to_dict()


@app.post("/api/sessions/{session_id}/wrap-up")
def wrap_up_session(session_id: str):
    """Transition the session into wrap-up state for final review."""
    try:
        session = state.session_mgr.wrap_up(session_id)
    except KeyError:
        raise HTTPException(status_code=404, detail=f"Session not found: {session_id}")
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))
    return session.to_dict()


@app.post("/api/sessions/{session_id}/close")
def close_session(session_id: str):
    """Permanently close a session. Returns 404 if not found."""
    try:
        session = state.session_mgr.close(session_id)
    except KeyError:
        raise HTTPException(status_code=404, detail=f"Session not found: {session_id}")
    return session.to_dict()
