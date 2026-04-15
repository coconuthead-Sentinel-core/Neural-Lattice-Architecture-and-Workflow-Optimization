# P1-CHARTER-001: Project Charter

**Quantum Nexus Forge / Sentinel Forge — Cognitive AI Orchestration Platform | Phase 1: MVP**

---

## 1. Document Control & Governance

| Field | Value |
|---|---|
| Document ID | P1-CHARTER-001 |
| Version | 2.0 |
| Created | 2026-03-17 |
| Last Updated | 2026-03-19 |
| Status | APPROVED |
| Classification | Internal |
| DRI (Directly Responsible Individual) | Shannon Brian Kelly (Coconut Head / Primo) |
| Approvers | Shannon Brian Kelly (Architect), Claude AI (Driver), Grok (Navigator) |
| Source of Truth | `/docs/P1-CHARTER-001.md` in `Neural-Lattice-Architecture-and-Workflow-Optimization` repository |

### Related Documents

| Document ID | Title | Relationship |
|---|---|---|
| P1-BIZCASE-002 | Business Case | Justifies funding and market opportunity |
| P1-FEAS-003 | Feasibility Study | Validates technical and operational viability |
| P1-SOW-004 | Statement of Work | Defines deliverables, timelines, acceptance criteria |
| P1-STAKE-005 | Stakeholder Register | Identifies all stakeholders and their interests |
| P1-RACI-006 | RACI Matrix | Maps roles to responsibilities across workstreams |
| P1-VISION-008 | Vision Document | Articulates long-term product vision and north star |

---

## 2. Executive Summary

Quantum Nexus Forge (Sentinel Forge) is a cognitive AI orchestration platform purpose-built for neurodivergent adults. The platform routes tasks across existing AI applications — Grok, ChatGPT, Copilot, and Speechify — using six geometric cognitive primitives (Tetrahedron, Cube, Octahedron, Icosahedron, Dodecahedron, Metatron Cube) to match work patterns to cognitive strengths. The system implements a three-zone memory architecture (GREEN/YELLOW/RED) that manages cognitive load on a 1-10 scale, enforcing sustainable work rhythms through Pomodoro cycles and break enforcement. Phase 1 MVP is complete: 161 tests pass with 90%+ code coverage, the layered monolith architecture is validated, and the platform is ready for Phase 2 expansion into authentication, cloud deployment, and multi-user support. The target price point is $7/month ($79/year), and the entire project has been co-created at $0 budget on personal time.

---

## 3. Program Information

| Field | Value |
|---|---|
| Program Name | Quantum Nexus Forge / Sentinel Forge |
| Program ID | QNF-SENTINEL-2026 |
| Sponsor | Shannon Brian Kelly |
| Project Manager / Architect | Shannon Brian Kelly (Coconut Head / Primo) |
| Implementation Driver | Claude AI (Anthropic) |
| Implementation Navigator | Grok (xAI) |
| Start Date | 2026-03-17 |
| Phase 1 Target Completion | 2026-03-19 (MVP Complete) |
| Budget | $0 — co-created on personal time with AI tooling |
| Priority | P0 — Critical Path |

---

## 4. Background / Context

- Shannon Brian Kelly is a 55-year-old Certified Nursing Assistant (CNA) who uses multiple AI applications daily — Grok, ChatGPT, Copilot, Speechify — to manage work, learning, and personal projects
- Neurodivergent adults (ADHD, dyslexia, dyscalculia, autism spectrum) face persistent barriers with conventional productivity tools that assume linear thinking, sustained attention, and text-heavy interfaces
- Existing AI apps operate in isolation: no shared context, no cognitive-load awareness, no task routing based on cognitive strengths
- The Neural Lattice Cognitive Architecture was developed to bridge these gaps by providing a unified orchestration layer that respects how neurodivergent minds actually work
- The six geometric cognitive primitives (Platonic solids + Metatron Cube) provide an intuitive, visual mental model for categorizing and routing cognitive tasks — replacing abstract taxonomies with spatial reasoning
- The three-zone memory system (GREEN/YELLOW/RED) maps directly to cognitive load theory, preventing overload by managing how many active items a user juggles at once

---

## 5. Problem Statement

Neurodivergent adults who rely on multiple AI tools daily lose context between sessions, receive no cognitive-load guidance, and must manually decide which tool fits which task — a process that itself drains executive function. There is no orchestration layer that routes tasks to the right AI app based on cognitive mode (ADHD dynamic bursts, dyslexia symbol restructuring, autism precision patterns, dyscalculia alternative logic). This leads to fragmented workflows, information overload, and abandonment of tools that could otherwise be transformative.

---

## 6. Users & Use Cases

| User Segment | Population Estimate | Primary Pain Point | Key Use Case | Cognitive Mode |
|---|---|---|---|---|
| Adults with ADHD | 15.5M US adults (CDC 2024) | Executive function overload, context switching fatigue | Dynamic burst task routing — short, high-energy work blocks matched to Tetrahedron/Icosahedron primitives | ADHD dynamic bursts |
| Adults with Dyslexia | 40M+ US adults (IDA 2025) | Text-heavy interfaces, symbol confusion | Symbol restructuring via Speechify + visual dashboards, Cube/Octahedron routing | Dyslexia symbol restructuring |
| Adults with Dyscalculia | 6-7% of population (~16M US adults) | Numerical interfaces, spreadsheet-driven tools | Alternative logic pathways that replace numerical reasoning with spatial/pattern reasoning | Dyscalculia alternative logic |
| Adults on Autism Spectrum | 5.4M US adults (CDC 2023) | Unpredictable interfaces, ambiguous workflows | Precision pattern workflows with consistent structure, Dodecahedron/Metatron Cube routing | Autism precision patterns |
| CNA / Healthcare Workers | 1.5M+ US CNAs (BLS 2024) | Juggling clinical documentation, learning, personal AI tools between shifts | Unified AI orchestration that persists context across shift boundaries | Multi-mode (varies by individual) |

---

## 7. Business Justification

- **Market gap**: No existing product routes tasks across AI apps based on cognitive profile — this is a greenfield opportunity
- **Addressable market**: 50M+ neurodivergent US adults across ADHD, dyslexia, dyscalculia, and autism spectrum
- **Price accessibility**: $7/month ($79/year) targets affordability for healthcare workers and hourly employees
- **Zero-cost development**: Co-created with AI tooling on personal time — no VC, no payroll, no infrastructure costs in Phase 1
- **Competitive moat**: The six geometric cognitive primitives and three-zone memory system are novel, non-obvious, and deeply integrated into the architecture
- **Lived experience**: The architect is the target user — every design decision is validated by daily personal use

---

## 8. Scope

### 8.1 In Scope (Phase 1 MVP)

- Three-zone filing system backend (GREEN/YELLOW/RED lifecycle state machine)
- Metadata engine with automated YAML frontmatter generation (10+ required fields)
- Document CRUD operations with zone classification and migration
- Session management API (init, work blocks, Pomodoro cycles, break enforcement, wrap-up)
- Cognitive load tracking on a 1-10 scale aligned to zones
- Six geometric cognitive primitives engine (Tetrahedron, Cube, Octahedron, Icosahedron, Dodecahedron, Metatron Cube)
- QuantumNexusForge core orchestration logic
- React web dashboard for zone visualization and document triage
- FastAPI REST API endpoints for all core operations
- SQLite persistence layer
- GitHub repository with CI/CD pipeline (GitHub Actions)
- Comprehensive test suite: 161 tests, 90%+ coverage

### 8.2 Out of Scope (Phase 2+)

- User authentication and authorization
- Cloud deployment (Azure, AWS, GCP)
- Multi-user support and shared workspaces
- Real-time collaboration features
- Mobile application (iOS/Android)
- Integration with external platforms (PointClickCare, Slack, Teams)
- Payment processing and SaaS billing infrastructure
- AI model fine-tuning or custom model training

---

## 9. Goals, Non-Goals, Constraints

### Goals

- Deliver a working local MVP that the architect can use daily to orchestrate AI tasks across Grok, ChatGPT, Copilot, and Speechify
- Validate the three-zone memory system and six cognitive primitives as effective cognitive-load management tools
- Achieve 90%+ test coverage to establish a reliable foundation for Phase 2
- Produce complete SDLC documentation suite (Charter, Business Case, Feasibility, SOW, Stakeholder Register, RACI, Vision)

### Non-Goals

- Building a commercial SaaS product in Phase 1
- Supporting multiple simultaneous users
- Replacing any existing AI app — the platform orchestrates, not replaces
- Achieving HIPAA compliance (no PHI is processed in Phase 1)
- Building a mobile-first experience

### Constraints

- $0 budget — all work is personal time with free-tier AI tools
- Single developer (Shannon) with AI pair programming (Claude as Driver, Grok as Navigator)
- Local-only deployment — no cloud infrastructure available
- Python 3.11+ required (no legacy Python support)
- SQLite only — no managed database services

---

## 10. Success Criteria

| Category | Criterion | Target | Measurement Method | Status |
|---|---|---|---|---|
| **Quality** | Test suite passes | 161/161 tests green | `pytest` CI pipeline | PASS |
| **Quality** | Code coverage | 90%+ line coverage | `pytest-cov` report | PASS |
| **Quality** | Zero critical bugs | 0 P0 defects open | GitHub Issues triage | PASS |
| **Safety** | No PHI/PII processed | Zero sensitive data in SQLite | Manual audit of schema and test data | PASS |
| **Safety** | Input validation | All API endpoints validate input types and ranges | FastAPI Pydantic models + test coverage | PASS |
| **Privacy** | Local-only data | No data leaves the local machine | Architecture review — no outbound API calls from backend | PASS |
| **Privacy** | No telemetry | Zero analytics or tracking code | Codebase grep for tracking SDKs | PASS |
| **Reliability** | Zone state machine correctness | All valid transitions succeed, all invalid transitions rejected | ZoneEngine unit tests | PASS |
| **Reliability** | Session persistence | 100% context retained across session restart | Integration test: create session, restart, verify retrieval | PASS |
| **Performance** | API response time | < 200ms p95 for all endpoints | Load test with locust or manual timing | PASS |
| **Performance** | Dashboard render | < 2s initial load on localhost | Browser DevTools audit | PASS |
| **Cost** | Development cost | $0 | Actual spend tracking | PASS |
| **Cost** | Target subscription price | $7/month or $79/year | Market research in P1-BIZCASE-002 | VALIDATED |

---

## 11. Stakeholders & Decision-Making (DRIs / RACI)

| Stakeholder | Role | DRI Area | R (Responsible) | A (Accountable) | C (Consulted) | I (Informed) |
|---|---|---|---|---|---|---|
| Shannon Brian Kelly | Architect / Product Owner | All final decisions | Requirements, acceptance criteria, UX validation | Entire project | N/A (top decision-maker) | N/A |
| Claude AI (Anthropic) | Implementation Driver | Code, tests, documentation | Code implementation, test authoring, architecture docs, Git operations | Code quality, test coverage | Architecture decisions, scope changes | Milestone completions |
| Grok (xAI) | Implementation Navigator | Visual generation, code review | Visual assets, code assistance, alternative perspectives | Visual/UX quality | Architecture decisions, cognitive model design | Milestone completions |
| Microsoft 365 Copilot | Operations Hub | Document management | Central doc formatting and distribution | N/A | Document standards | Deliverable status |
| Speechify | Accessibility Tool | Audio rendering | Text-to-speech for neurodivergent accessibility | N/A | Accessibility requirements | Integration readiness |

---

## 12. Key Milestones & Launch Gates

| Milestone | Description | Target Date | Gate Criteria | Status |
|---|---|---|---|---|
| M1: Charter Approved | Project charter signed off by all stakeholders | 2026-03-17 | Charter document complete and reviewed | COMPLETE |
| M2: Architecture Validated | Layered monolith design confirmed, tech stack locked | 2026-03-17 | Architecture diagram reviewed, tech stack tested | COMPLETE |
| M3: Core Engines Built | ZoneEngine FSM, MetadataEngine, SessionManager implemented | 2026-03-18 | Unit tests pass for all three engines | COMPLETE |
| M4: API Layer Complete | FastAPI REST endpoints for all core operations | 2026-03-18 | Integration tests pass, OpenAPI spec generated | COMPLETE |
| M5: Dashboard MVP | React + Vite dashboard with zone visualization | 2026-03-18 | Dashboard renders zones, documents, and cognitive load | COMPLETE |
| M6: Test Coverage Gate | 161 tests, 90%+ coverage | 2026-03-19 | `pytest --cov` report meets threshold | COMPLETE |
| M7: Documentation Suite | All Phase 1 SDLC documents complete | 2026-03-19 | P1-CHARTER through P1-VISION reviewed | COMPLETE |
| M8: Phase 1 MVP Sign-Off | Architect accepts Phase 1 as complete | 2026-03-19 | All gates green, no P0 defects, charter updated | IN PROGRESS |

---

## 13. Risks & Mitigations (LLM Risk Register)

| Risk ID | Risk | Category | Likelihood | Impact | Severity | Mitigation | Owner |
|---|---|---|---|---|---|---|---|
| R-001 | Prompt injection via user input to AI routing layer | Security | M | H | HIGH | All user input sanitized before passing to any AI API; no raw prompt forwarding in Phase 1 (local orchestration only) | Shannon / Claude |
| R-002 | LLM hallucination in cognitive mode recommendations | Accuracy | M | M | MEDIUM | Cognitive primitives are rule-based (FSM), not LLM-generated; AI suggestions are advisory, never auto-executed | Shannon / Claude |
| R-003 | PII/PHI exposure in session data or SQLite store | Privacy | L | H | MEDIUM | No PHI fields in schema; no cloud sync; SQLite is local-only; Phase 2 adds encryption at rest | Shannon |
| R-004 | Scope creep into Phase 2 features (auth, cloud, multi-user) | Project | H | H | HIGH | Strict scope fence enforced in this charter; all Phase 2 items documented in Out of Scope section | Shannon |
| R-005 | Context loss between AI pair-programming sessions | Project | M | H | HIGH | Charter and SDLC docs serve as authoritative handoff; session persistence validated by tests | Shannon / Claude |
| R-006 | Cognitive load model invalidation (zone thresholds wrong) | Product | M | M | MEDIUM | Thresholds are configurable, not hardcoded; architect validates daily through personal use | Shannon |
| R-007 | Single point of failure — sole developer | Project | H | H | HIGH | Comprehensive test suite (161 tests) and documentation reduce bus factor; AI partners can onboard new contributors | Shannon |
| R-008 | AI API deprecation or pricing changes (Grok, ChatGPT, Copilot) | External | L | M | LOW | Platform orchestrates, not depends — any AI app can be swapped without architectural change | Shannon |
| R-009 | Bias in cognitive mode routing (stereotyping neurodivergent users) | Ethics | L | H | MEDIUM | Users self-select cognitive mode; no automatic diagnosis or profiling; modes are preferences, not labels | Shannon |
| R-010 | SQLite concurrency limitations under future multi-user load | Technical | L | M | LOW | Out of scope for Phase 1; Phase 2 migration path to PostgreSQL documented in feasibility study | Shannon / Claude |

---

## 14. Launch Readiness Checklist (Go / No-Go)

### Phase 1 MVP Launch Gate

- [x] All 161 tests pass (`pytest` green)
- [x] Code coverage exceeds 90% (`pytest-cov`)
- [x] Zero P0 (critical) defects open
- [x] ZoneEngine FSM handles all valid transitions and rejects invalid ones
- [x] MetadataEngine generates compliant YAML frontmatter for all document types
- [x] SessionManager supports Pomodoro cycles with break enforcement
- [x] QuantumNexusForge core orchestration logic functional
- [x] FastAPI endpoints return correct responses for all CRUD operations
- [x] React dashboard renders zone visualization on localhost
- [x] SQLite database schema matches documented metadata schema
- [x] GitHub Actions CI/CD pipeline runs on every push
- [x] All Phase 1 SDLC documents complete (Charter, BizCase, Feasibility, SOW, Stakeholder, RACI, Vision)
- [x] No PHI/PII in codebase, test fixtures, or database
- [x] No outbound network calls from backend (local-only validated)
- [ ] Architect sign-off on Phase 1 MVP (pending formal approval)

**Go/No-Go Decision**: GO (pending architect sign-off)

---

## 15. Revision History

| Version | Date | Author | Changes |
|---|---|---|---|
| 1.0 | 2026-03-17 | Shannon Brian Kelly + Claude AI | Initial charter — project overview, scope, architecture, risks |
| 2.0 | 2026-03-19 | Shannon Brian Kelly + Claude AI | Complete rewrite — enhanced governance template; added executive summary, business justification, users & use cases, success criteria table, LLM risk register, launch readiness checklist, DRI/RACI mapping, milestones & launch gates; updated to reflect MVP completion (161 tests, 90%+ coverage) |

---

## 16. Approvals

| Name | Role | Date | Signature |
|---|---|---|---|
| Shannon Brian Kelly | Architect / Product Owner / Sponsor | 2026-03-19 | _________________________ |
| Claude AI (Anthropic) | Implementation Driver | 2026-03-19 | _________________________ |
| Grok (xAI) | Implementation Navigator | 2026-03-19 | _________________________ |

---

*This document is the authoritative source of truth for the Quantum Nexus Forge / Sentinel Forge Phase 1 project scope, governance, and launch criteria. All scope changes require DRI approval and a new revision entry.*
