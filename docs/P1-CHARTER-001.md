# P1-CHARTER-001: Project Charter

**Neural Lattice Cognitive Architecture | Phase 1: Initiation**

| Field | Value |
|---|---|
| Document ID | SDLC-CHARTER-001 |
| Version | 1.0 |
| Date | 2026-03-17 |
| Author | Shannon Brian Kelly + Claude AI (Archivist of Wisdom) |
| Status | COMPLETE |
| Classification | GREEN Zone - Active Development |

## 1. Project Overview

### 1.1 Project Name
Neural Lattice Cognitive Architecture (NLCA)

### 1.2 Problem Statement
Traditional AI interactions suffer from three critical limitations: (1) zero persistent memory between sessions, resulting in complete context loss; (2) no structured organization of generated content, making retrieval unreliable; (3) no cognitive load awareness for neurodivergent users, leading to information overload and reduced productivity.

### 1.3 Proposed Solution
Build a working software application that implements the Neural Lattice Cognitive Architecture as a deployable tool. The system provides: file-based persistent memory across sessions, a three-zone organization system (GREEN/YELLOW/RED) mapped to cognitive load, structured protocol-driven interactions, automated metadata generation and tagging, and neurodivergent-optimized information formatting.

### 1.4 Project Objectives
1. Implement the three-zone filing system (GREEN/YELLOW/RED) as a functional backend service with API endpoints
2. Build a metadata engine that auto-generates YAML frontmatter with 10+ required fields per document
3. Create a session management system supporting Pomodoro cycles, cognitive load tracking (1-10 scale), and break enforcement
4. Deliver a web-based dashboard for zone visualization, document triage, and Eisenhower matrix integration
5. Package the system for deployment via GitHub with CI/CD pipeline

### 1.5 Success Criteria

| Metric | Target | Measurement |
|---|---|---|
| Cross-session retention | 100% preserved | Retrieval test after 24hr gap |
| Metadata coverage | 100% tagged | Automated validation script |
| Zone accuracy | 95%+ correct | Manual audit of 50 documents |
| API response time | < 200ms p95 | Load testing |
| Test coverage | > 80% | pytest + coverage report |

## 2. Scope Definition

### 2.1 In Scope
- Zone-based filing system backend (GREEN/YELLOW/RED lifecycle management)
- Metadata engine with automated YAML frontmatter generation
- Document CRUD operations with zone classification and migration
- Session management API (init, work blocks, breaks, wrap-up)
- Cognitive load tracking and Pomodoro timer integration
- Dependency graph tracking between documents
- Web dashboard for zone visualization and document triage
- REST API endpoints for all core operations
- GitHub repository with CI/CD pipeline
- Comprehensive test suite (unit, integration, API)

### 2.2 Out of Scope (Phase 1)
- Multi-user support and authentication
- Cloud deployment (Azure/AWS) - local and GitHub Pages only
- Real-time collaboration features
- Mobile application
- Integration with external platforms (PointClickCare, Slack)
- Payment processing or SaaS infrastructure

## 3. Architecture

### 3.1 System Components

| Component | Tech | Function | Priority |
|---|---|---|---|
| Zone Engine | Python | GREEN/YELLOW/RED lifecycle state machine | P0-MVP |
| Metadata Engine | Python+YAML | Auto-generate 10+ field metadata blocks | P0-MVP |
| Document Store | SQLite | CRUD for documents with zone tracking | P0-MVP |
| Session Manager | FastAPI | Pomodoro, load tracking, break enforcement | P1 |
| REST API | FastAPI | Endpoints for all core operations | P0-MVP |
| Dashboard | React | Zone visualization, Eisenhower matrix | P1 |
| Dependency Graph | NetworkX | Track relationships between documents | P2 |
| CLI Tool | Click | Command-line interface for power users | P2 |

### 3.2 Zone State Machine

| Transition | Trigger | Guard | Action |
|---|---|---|---|
| GREEN->YELLOW | dev_complete | cognitive_load < 7 AND status != DRAFT | Migrate, update zone |
| YELLOW->RED | stable | cognitive_load < 4 AND version >= 1.0 | Migrate, ARCHIVED |
| RED->YELLOW | reactivation | revision_needed | Migrate, ACTIVE |

### 3.3 Metadata Schema (10 Required Fields)

| Field | Type | Validation | Purpose |
|---|---|---|---|
| doc_id | String | `^[A-Z]{3,4}-[A-Z]{3,6}-[0-9]{3}$` | Unique identification |
| title | String | 1-200 chars, unique | Human-readable label |
| zone | Enum | GREEN\|YELLOW\|RED | Activity classification |
| protocol | String | Onset_Omega_1\|Joy\|Combined | Governance framework |
| artifact_type | Enum | Predefined list | Content category |
| cognitive_load | Integer | 1-10, aligned w/ zone | Mental effort rating |
| timestamp | ISO8601 | RFC3339 | Temporal anchor |
| dependencies | Array | Valid doc_id refs | Relationship map |
| tags | Array | lowercase_underscore | Search tags |
| status | Enum | DRAFT\|ACTIVE\|TESTING\|ARCHIVED | Lifecycle state |

## 4. Stakeholders

| Role | Person/System | Responsibility |
|---|---|---|
| Product Owner | Shannon Brian Kelly | Requirements, priorities, acceptance, final decisions |
| Documentation | Claude AI (Claude.ai) | Architecture docs, specs, Word deliverables |
| Development | Claude Code (API) | Code implementation, testing, Git operations |
| Visual/Code | Grok 4 (xAI) | Visual generation, code assistance |
| Operations Hub | Microsoft 365 Copilot | Central document management |

## 5. Risks and Mitigations

| Risk | Likelihood | Impact | Mitigation |
|---|---|---|---|
| Scope creep | HIGH | HIGH | Strict scope fence. Defer to Phase 2. |
| Context loss between sessions | MEDIUM | HIGH | Charter doc as authoritative handoff. |
| Tech stack mismatch | LOW | MEDIUM | Python+FastAPI confirmed. |
| Neurodivergent workflow gaps | MEDIUM | HIGH | Pomodoro + load tracking are P0/P1. |
| Over-engineering metadata | MEDIUM | MEDIUM | Start with 10 required fields. |

## 6. Approvals

| Name | Role | Date |
|---|---|---|
| Shannon Brian Kelly | Product Owner / Architect | 2026-03-17 |
| Claude AI | Documentation Partner | 2026-03-17 |
| Claude Code | Development Partner | 2026-03-17 |
