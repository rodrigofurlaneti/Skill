---
name: project-architect
description: >
	Fullstack project architect for .NET + React applications with PO, Senior DBA,
	UX/UI, Tech Lead, and DevOps/SRE focus.
	Use this skill to map business processes (PO), create projects (scaffold),
	validate architectures, refactor code to follow DDD/SOLID, optimize EF Core,
	perform code reviews, configure cloud infrastructure (Docker/CI/CD),
	and ensure responsive multi-screen compatibility.

	Trigger on: "business mapping", "product discovery", "requirements analysis", "create project",
	"scaffold", "DDD", "clean architecture", "EF Core performance", "multi-tenant isolation",
	"code review", "refactoring", "design system", "setup devops", "dockerize",
	"responsive UI", "multi-device".
---

# Project Architect — From Business Discovery to DevOps Mastery

This skill creates production-grade fullstack applications, maps business requirements, validates existing projects, or performs senior-level governance. It encapsulates the architecture wisdom of real-world projects: Domain-Driven Design, Clean Architecture, SOLID, High-Performance Database Design, Responsive/Adaptive UX, and SRE Resilience.
## Modes of Operation

1. **Discovery Mode (PO)** — Map business processes, generate user stories (INVEST), and functional requirements.
2. **Scaffold Mode** — Generate a new project from scratch (Backend, Database, Frontend, UX, DevOps, Security).
3. **Audit Mode** — Analyze an existing project for architectural, database, or usability violations.
4. **Review Mode (Tech Lead)** — Professional code review of snippets or PRs to ensure the "Gold Standard".
5. **Ops Mode (SRE)** — Configure Docker, CI/CD pipelines, and structured observability.

---

## Quick Start — Full Lifecycle

To start a new product from discovery to scaffold:

```bash
# 1. Discovery Phase (PO Agent)
python scripts/scaffold_discovery.py --name MyApp --context "Business context description"

# 2. Execution Phase (Orchestrator runs technical generators)
python scripts/scaffold_all.py --name MyApp --output ./output --db sqlserver --entities Task Project
```

Step 1: Architecture & Governance Overview
Product & Discovery (PO Agent)
Process Mapping: Happy Path vs. Exception flows mapping.

User Stories: INVEST standard with Gherkin (BDD) acceptance criteria.

Prioritization: MoSCoW methodology for MVP definition.

Backend (.NET) — Clean Architecture + Senior DBA
Domain Layer: Sacred business rules, rich entities, value objects, domain events.

Application Layer: CQRS with MediatR, FluentValidation, Result Pattern.

Infrastructure Layer: EF Core with Fluent API, Repository implementations, JWT security.

DB Mastery: No nvarchar(max), mandatory AsNoTracking, AsSplitQuery, and strict typing.

Frontend (React + TypeScript) — Feature-Based + UX Specialist
UI/UX: Glassmorphism, Plus Jakarta Sans, and high-performance animations.

Responsiveness: Mobile-First Adaptive Design. Full support for Mobile, Tablet, and Desktop via CSS Grid/Flexbox.

State: Zustand for client state, React Query for server state.

Components: Typed props (zero any), accessible UI library (a11y), and responsive breakpoints.

Code Review & DevOps — Tech Lead + SRE Governance
Tech Lead: DRY, KISS, Result Pattern, NetArchTest enforcement.

SRE: Multi-stage Dockerfiles (Alpine), CI/CD pipelines, Serilog, Health Checks.

Critical Patterns Checklist (The Gold Standard)
### 1. Product Discovery (PO) Must-Haves
- [ ] Persona Definition: Clear understanding of who is using the feature.
- [ ] INVEST Stories: Stories are Independent, Valuable, Small, and Testable.
- [ ] Acceptance Criteria: Defined in BDD/Gherkin format.

### 2. Technical Must-Haves (Architecture & DB)
- [ ] Rich Entities: Business logic INSIDE the entity; private setters.
- [ ] Fluent API: Use IEntityTypeConfiguration<T> (No Data Annotations).
- [ ] Read Performance: All read queries MUST use .AsNoTracking().
- [ ] Async Hygiene: CancellationToken propagated through all async calls.

### 4. Frontend Must-Haves
- [ ] **Zero `any`:** All props and functions must be fully typed.
- [ ] **Feature Folders:** Components organized by feature, not by type.
- [ ] **Error Boundaries:** Every async operation wrapped with proper error handling.
- [ ] **Accessibility:** All interactive elements have `aria-*` labels.

### 3. UI/UX & Responsiveness
- [ ] Mobile-First: Styles written for small screens first, then scaled up.
- [ ] Fluid Layout: Relative units (rem, vh/vw) instead of fixed pixels.
- [ ] Touch Targets: Minimum 44x44px for mobile interactivity.

### 5. Security Must-Haves
- [ ] **JWT Validation:** Token expiration, audience, and issuer always validated.
- [ ] **OWASP Top 10:** Input sanitization, SQL injection prevention, XSS protection.
- [ ] **Secrets Management:** No secrets in `appsettings.json`; use environment variables or Key Vault.

> Reference: `references/security-identity.md`

Project Structure
project-architect/
├── SKILL.md                ← This file
├── blueprints/
│   ├── discovery/          ← PO/Business templates
│   ├── backend/            ← .NET code templates (DDD)
│   ├── frontend/           ← React code templates (Responsive)
│   ├── auth/               ← Security templates
│   └── review/             ← Governance templates
├── references/             ← Knowledge base
│   ├── product-discovery.md
│   ├── dotnet-ddd.md
│   ├── ef-core-dba.md
│   ├── react-frontend.md   ← Including Multi-screen patterns
│   ├── ux-ui-patterns.md   ← Including Responsive standards
│   ├── code-review.md
│   ├── security-identity.md
│   └── devops-observability.md
├── scripts/                ← Scaffold generators
│   ├── scaffold_discovery.py
│   └── scaffold_all.py
├── evals/                  ← Test scenarios
└── adrs/                   ← Architecture Decisions

Reference Files & Scaffold Scripts
references/product-discovery.md: PO patterns, INVEST stories, MoSCoW prioritization.

references/dotnet-ddd.md: Clean Architecture & DDD patterns.

references/ef-core-dba.md: EF Core performance mastery.

references/react-frontend.md: Feature-based React & TypeScript patterns.

references/ux-ui-patterns.md: Distinctive UX (Glassmorphism, a11y).

references/code-review.md: Tech Lead guidelines for code governance.

references/security-identity.md: JWT, OWASP, and Auth patterns.

references/devops-observability.md: SRE patterns for Docker, CI/CD, and Logs.

scripts/scaffold_discovery.py: Generates PO Documentation and Backlog.

scripts/scaffold_all.py: Master orchestrator that runs all generators in order.
---

