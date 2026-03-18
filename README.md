# Neural Lattice Cognitive Architecture (NLCA)

> A structured, neurodiversity‑aligned workflow framework that explains the Neural Lattice Architecture and its role in optimizing AI‑supported project management.

A cognitive workflow framework providing persistent memory, zone-based organization (GREEN/YELLOW/RED), and neurodivergent-optimized workflows for AI-human collaboration. It expands on the concepts introduced in the LinkedIn article and provides a comprehensive guide to implementing the NLA in practice.

---

## Overview

The Neural Lattice Cognitive Architecture addresses three critical limitations in AI interactions:

1. **Zero persistent memory** — complete context loss between sessions
2. **No structured organization** — generated content has no metadata or lifecycle
3. **No cognitive load awareness** — information overload for neurodivergent users

NLCA provides: file-based persistent memory, a three-zone organization system mapped to cognitive load, automated metadata generation, session management with Pomodoro timing, and a REST API for all operations.

## Three-Zone System

| Zone | Cognitive Load | Purpose |
|------|---------------|---------|
| **GREEN** | 7-10 (High) | Active development, frequent access |
| **YELLOW** | 4-6 (Medium) | Synthesis, pattern recognition, moderate demand |
| **RED** | 1-3 (Low) | Reference materials, archived work |

Zone transitions enforce guard conditions (e.g., a document can only move GREEN→YELLOW when `cognitive_load < 7 AND status != DRAFT`).

## Quick Start

```bash
# Clone and install
git clone https://github.com/coconuthead-Sentinel-core/Neural-Lattice-Architecture-and-Workflow-Optimization.git
cd Neural-Lattice-Architecture-and-Workflow-Optimization
pip install -e ".[dev]"

# Run the API server
uvicorn neural_lattice.api.app:app --reload

# API docs available at http://127.0.0.1:8000/docs
```

## Dashboard (frontend)

```bash
cd dashboard
cp .env.example .env   # optional: override API base URL
npm install
npm run dev            # http://localhost:5173
```

The dashboard defaults to `http://127.0.0.1:8000` for API calls. Override by setting `VITE_API_BASE` in `dashboard/.env`.

## Configuration

Copy `.env.example` to `.env` and adjust settings:

```bash
cp .env.example .env
```

Key settings: `NLCA_DB_PATH`, `NLCA_API_PORT`, `NLCA_POMODORO_MIN`.

## API Endpoints

### Documents
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/documents` | Create document with auto-generated metadata |
| GET | `/api/documents` | List all documents |
| GET | `/api/documents/{doc_id}` | Get document by ID |
| PUT | `/api/documents/{doc_id}` | Update document |
| DELETE | `/api/documents/{doc_id}` | Delete document |
| GET | `/api/search` | Search by zone, status, tag, artifact_type, text |

### Zones
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/classify` | Classify zone from cognitive load |
| POST | `/api/migrate` | Migrate document between zones (with guard enforcement) |
| GET | `/api/zones/summary` | Document count per zone |
| POST | `/api/validate` | Validate metadata completeness |

### Sessions
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/sessions` | Initialize a new session |
| POST | `/api/sessions/{id}/work` | Start a work block |
| POST | `/api/sessions/{id}/end-work` | End work block (triggers break) |
| POST | `/api/sessions/{id}/load` | Record cognitive load (1-10) |
| POST | `/api/sessions/{id}/wrap-up` | Begin session wrap-up |
| POST | `/api/sessions/{id}/close` | Close session |

## Metadata Schema (10 Required Fields)

Every document receives YAML frontmatter with:

| Field | Type | Validation |
|-------|------|------------|
| `doc_id` | String | `^[A-Z]{3,4}-[A-Z]{3,6}-[0-9]{3}$` |
| `title` | String | 1-200 characters |
| `zone` | Enum | GREEN \| YELLOW \| RED |
| `protocol` | String | Onset_Omega_1 \| Joy_Protocol \| Coconut_Head \| Combined |
| `artifact_type` | Enum | charter, spec, code, test, etc. |
| `cognitive_load` | Integer | 1-10, must align with zone |
| `timestamp` | ISO8601 | RFC3339 compliant |
| `dependencies` | Array | Valid doc_id references |
| `tags` | Array | lowercase_underscore format |
| `status` | Enum | DRAFT \| ACTIVE \| TESTING \| ARCHIVED \| REFERENCE |

## Project Structure

```
neural_lattice/
├── api/              # FastAPI REST API
│   ├── app.py        # Application and endpoints
│   └── models.py     # Pydantic request/response models
├── meta/             # System layer
│   ├── config.py     # Environment-based configuration
│   └── schemas.py    # Metadata schema definitions and validation
├── zone_engine.py    # Zone FSM with transition guards
├── metadata_engine.py # Auto-generates YAML frontmatter
├── document_store.py # SQLite-backed document CRUD
└── session_manager.py # Pomodoro + cognitive load tracking
docs/                 # SDLC documentation (13 documents)
tests/                # Test suite (103 tests, 90% coverage)
.github/workflows/    # CI/CD pipeline
```

## Repository Structure (Recommended Zones)

```
Neural-Lattice-Architecture-and-Workflow-Optimization/
├── README.md                   # This document – framework overview and article
├── LICENSE                     # CC BY 4.0 International License
├── GREEN/                      # Active work with highest cognitive load
│   ├── current-projects/
│   └── in-progress-tasks/
├── YELLOW/                     # Synthesis, pattern recognition, review
│   ├── templates/
│   └── drafts/
└── RED/                        # Reference materials and completed work
    ├── archived-projects/
    └── reference-docs/
```

## Testing

```bash
# Run tests
pytest -v

# Run with coverage
pytest --cov=neural_lattice --cov-report=term-missing
```

Current: **103 tests, 90% code coverage**.

## SDLC Documentation

Full SDLC documentation suite in `docs/`:

| Document | Status |
|----------|--------|
| P1-CHARTER-001: Project Charter | COMPLETE |
| P1-BIZCASE-002: Business Case | COMPLETE |
| P1-FEAS-003: Feasibility Study | COMPLETE |
| P1-SOW-004: Statement of Work | COMPLETE |
| P1-STAKE-005: Stakeholder Analysis | COMPLETE |
| P1-RACI-006: RACI Matrix | COMPLETE |
| P1-VISION-008: Project Vision | COMPLETE |
| P9-CLOSE-075: Closure Report | COMPLETE |
| P9-ACCEPT-076: Acceptance Document | COMPLETE |
| P9-TRANS-077: Transition Plan | COMPLETE |
| P9-MAINT-078: Maintenance Plan | COMPLETE |
| P9-DRP-080: Disaster Recovery Plan | COMPLETE |
| P9-PIR-079: Post-Implementation Review | COMPLETE |

## License

This project is shared under the Creative Commons Attribution 4.0 International License (CC BY 4.0).
You are free to share and adapt the material with appropriate credit.

Full license text: https://creativecommons.org/licenses/by/4.0/
