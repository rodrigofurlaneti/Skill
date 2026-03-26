---
name: project-architect
description: >
  Fullstack project architect for .NET + React applications with PO, Senior DBA, 
  UX/UI, Tech Lead, and DevOps/SRE focus. 
  Use this skill to map business processes (PO), create projects (scaffold), 
  validate architectures, refactor code to follow DDD/SOLID, optimize EF Core, 
  perform code reviews, or configure cloud infrastructure (Docker/CI/CD).
  Trigger on: "mapear negócio", "product discovery", "analise de requisitos", "criar projeto", 
  "scaffold", "DDD", "clean architecture", "EF Core performance", "multi-tenant isolation", 
  "code review", "revisar código", "refatoração", "design system", "configurar devops", "dockerizar".
---

# Project Architect — From Business Discovery to DevOps Mastery

This skill creates production-grade fullstack applications, maps business requirements, validates existing projects, or performs senior-level governance. It encapsulates the architecture wisdom of real-world projects: Domain-Driven Design, Clean Architecture, SOLID, High-Performance Database Design, Distinctive UX/UI, and SRE Resilience.

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
Process Mapping: Happy Path vs Exception flows mapping.

User Stories: INVEST standard with Gherkin (BDD) acceptance criteria.

Prioritization: MoSCoW methodology for MVP definition.

Backend (.NET) — Clean Architecture + Senior DBA
The backend follows a strict layered architecture where dependencies flow inward.

Domain Layer: Sacred business rules, rich entities, value objects, domain events.

Application Layer: CQRS with MediatR, FluentValidation, Result Pattern.

Infrastructure Layer: EF Core with Fluent API, Repository implementations, JWT security.

DB Mastery: No nvarchar(max), mandatory AsNoTracking, AsSplitQuery, and strict typing.

Frontend (React + TypeScript) — Feature-Based + UX Specialist
UI/UX: Glassmorphism, Plus Jakarta Sans, and high-performance animations.

State: Zustand for client state, React Query for server state.

Components: Typed props (zero any), accessible UI library (Button, Card, Input, Modal).

Code Review & DevOps — Tech Lead + SRE Governance
Tech Lead: DRY, KISS, Result Pattern, NetArchTest enforcement.

SRE: Multi-stage Dockerfiles (Alpine), CI/CD pipelines, Serilog, Health Checks.

Critical Patterns Checklist (The Gold Standard)
1. Product Discovery (PO) Must-Haves
[ ] Persona Definition: Clear understanding of who is using the feature.

[ ] INVEST Stories: Stories are Independent, Valuable, Small, and Testable.

[ ] Acceptance Criteria: Defined in BDD/Gherkin format.

2. Technical Must-Haves (Architecture & DB)
[ ] Rich Entities: Business logic IN the entity; private setters.

[ ] Fluent API: Use IEntityTypeConfiguration<T> (No Data Annotations).

[ ] Read Performance: All read queries MUST use .AsNoTracking().

[ ] Async Hygiene: CancellationToken propagated through all async calls.

Project Structure
project-architect/
├── SKILL.md                          ← This file
├── blueprints/
│   ├── discovery/                    ← PO/Business templates
│   ├── backend/                      ← .NET code templates
│   ├── frontend/                     ← React code templates
│   ├── auth/                         ← Security templates
│   └── review/                       ← Governance templates
├── references/                       ← Knowledge base
│   ├── product-discovery.md          ← Business & PO patterns
│   ├── dotnet-ddd.md                 ← Architecture patterns
│   ├── ef-core-dba.md                ← Database mastery
│   ├── react-frontend.md             ← Frontend patterns
│   ├── ux-ui-patterns.md             ← Design System
│   ├── code-review.md                ← Tech Lead governance
│   ├── security-identity.md          ← Auth patterns
│   └── devops-observability.md       ← SRE patterns
├── scripts/                          ← Scaffold generators
│   ├── scaffold_discovery.py         ← PO Document generator
│   ├── scaffold_all.py               ← Master orchestrator
│   └── ... (layer specific scripts)
├── evals/                            ← Test scenarios
└── adrs/                             ← Architecture Decisions
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

