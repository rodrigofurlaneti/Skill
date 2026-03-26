---
name: project-architect
description: >
  Fullstack project architect for .NET + React applications with Senior DBA, UX/UI,
  Tech Lead Code Review, and DevOps/SRE focus.
  Use this skill to create projects (scaffold), validate architectures, refactor code to
  follow DDD/Clean Architecture/SOLID, optimize EF Core performance, perform professional
  code reviews, or configure cloud-native infrastructure (Docker/CI/CD).
  Trigger on: "criar projeto", "scaffold", "DDD", "clean architecture", "EF Core performance",
  "multi-tenant isolation", "code review", "revisar código", "refatoração", "design system",
  "configurar devops", "dockerizar", "pipeline ci/cd".
---

# Project Architect — .NET DDD + React + DBA, UX, Code Review & DevOps Mastery

This skill creates production-grade fullstack applications, validates existing projects, or performs senior-level governance. It encapsulates the architecture wisdom of real-world projects: Domain-Driven Design, Clean Architecture, SOLID, High-Performance Database Design, Distinctive UX/UI, and SRE Resilience.

## Modes of Operation

1. **Scaffold Mode** — Generate a new project from scratch (Backend, Database, Frontend, UX, DevOps, Security).
2. **Audit Mode** — Analyze an existing project for architectural, database, or usability violations.
3. **Review Mode (Tech Lead)** — Professional code review of snippets or Pull Requests to ensure the "Gold Standard".
4. **Ops Mode (SRE)** — Configure Docker, CI/CD pipelines, and structured observability.

---

## Quick Start — Full Scaffold

To generate a complete project with a single command:

```bash
python scripts/scaffold_all.py --name MyApp --output ./output --db sqlserver --entities Task Project
```

This orchestrator runs all 7 scaffold generators in order:
1. Backend (Clean Architecture + DDD)
2. Database (Fluent API + Performance)
3. Security (JWT + Identity)
4. Frontend (React + TypeScript + Glassmorphism)
5. UX/UI Design System
6. Code Review & Governance
7. DevOps (Docker + CI/CD)

---

## Step 1: Gather Requirements

Before generating or reviewing, ask (if not provided):
- **Project/Feature name** & **Domain context**.
- **Entities**: Which domain entities to scaffold (default: Task, Project).
- **Database**: SQL Server (default) or PostgreSQL.
- **Multi-tenancy**: Is data isolation required? (Critical for FSI patterns).
- **Infrastructure**: Docker required? Target CI/CD (GitHub Actions default).

---

## Step 2: Architecture & Governance Overview

### Backend (.NET) — Clean Architecture + Senior DBA
The backend follows a strict layered architecture where dependencies flow inward.
- **Domain Layer**: Sacred business rules, rich entities, value objects, domain events, and repository interfaces.
- **Application Layer**: CQRS with MediatR, FluentValidation, Result Pattern, Pipeline Behaviors.
- **Infrastructure Layer**: EF Core with Fluent API, repository implementations, JWT security.
- **API Layer**: Base ApiController with Result-to-HTTP mapping, Swagger, Health Checks.
- **DB Mastery**: No `nvarchar(max)`, mandatory `AsNoTracking` for reads, `AsSplitQuery`, and strict typing.

### Frontend (React + TypeScript) — Feature-Based + UX Specialist
- **UI/UX**: Glassmorphism, Plus Jakarta Sans typography, and high-performance animations.
- **State**: Zustand for client state, React Query for server state.
- **Components**: Typed props (zero `any`), accessible UI library (Button, Card, Input, Modal).
- **API Layer**: Axios client with interceptors, typed service layer.

### Code Review & DevOps — Tech Lead + SRE Governance
- **Tech Lead**: DRY, KISS, Result Pattern, NetArchTest enforcement, comprehensive PR checklist.
- **SRE**: Multi-stage Dockerfiles (Alpine), CI/CD pipelines, Structured Logging (Serilog), Health Checks.

---

## Critical Patterns Checklist (The Gold Standard)

### 1. Backend & DBA Must-Haves
- [ ] **Rich Entities**: Business logic IN the entity; private setters, factory methods.
- [ ] **Fluent API**: Use `IEntityTypeConfiguration<T>` (No Data Annotations).
- [ ] **Read Performance**: All read queries MUST use `.AsNoTracking()`.
- [ ] **Data Isolation**: `.HasQueryFilter()` for multi-tenant protection (FSI pattern).
- [ ] **Result Pattern**: Explicit success/failure handling (No business exceptions).
- [ ] **CancellationToken**: Propagated through all async calls.
- [ ] **Strict Typing**: `HasMaxLength` for strings, `decimal(18,2)` for money.

### 2. Frontend & UX Must-Haves
- [ ] **Zero `any` types**: Strict TypeScript throughout.
- [ ] **Glassmorphism**: Consistent use of `glass` utility classes and `backdrop-blur`.
- [ ] **A11y**: Proper ARIA labels, keyboard navigation, and contrast compliance.
- [ ] **State Separation**: Zustand for client state, React Query for server state.
- [ ] **Lazy Loading**: All pages loaded with `React.lazy()` for bundle splitting.

### 3. Review & Ops (The Safety Net)
- [ ] **Async Hygiene**: `CancellationToken` propagated through all async calls.
- [ ] **Result Pattern**: Explicit success/failure handling (No business exceptions).
- [ ] **Docker Security**: Non-root users and Alpine-based images.
- [ ] **Observability**: Structured JSON logs (Serilog), `/health/live` and `/health/ready` endpoints.
- [ ] **CI/CD**: Build + Test + Lint on every push/PR.

---

## Project Structure

```
project-architect/
├── SKILL.md                          ← This file
├── blueprints/
│   ├── backend/                      ← .NET code templates
│   │   ├── BaseEntity.cs.blueprint
│   │   ├── Entity.cs.blueprint
│   │   ├── DomainEvent.cs.blueprint
│   │   ├── DomainException.cs.blueprint
│   │   ├── IRepository.cs.blueprint
│   │   ├── ResultPattern.cs.blueprint
│   │   ├── CreateCommand.cs.blueprint
│   │   ├── ApplicationDI.cs.blueprint
│   │   ├── AppDbContext.cs.blueprint
│   │   ├── Repository.cs.blueprint
│   │   ├── InfrastructureDI.cs.blueprint
│   │   ├── Program.cs.blueprint
│   │   ├── ApiController.cs.blueprint
│   │   └── EntityController.cs.blueprint
│   ├── frontend/                     ← React code templates
│   │   ├── package.json.blueprint
│   │   ├── tailwind.config.js.blueprint
│   │   ├── index.css.blueprint
│   │   ├── authStore.ts.blueprint
│   │   ├── api_client.ts.blueprint
│   │   ├── App.tsx.blueprint
│   │   ├── Page.tsx.blueprint
│   │   ├── Component.tsx.blueprint
│   │   └── ui/
│   │       ├── Button.tsx.blueprint
│   │       ├── Card.tsx.blueprint
│   │       ├── Input.tsx.blueprint
│   │       └── Modal.tsx.blueprint
│   ├── auth/                         ← Security templates
│   │   ├── AuthController.cs.blueprint
│   │   └── JwtProvider.cs.blueprint
│   └── review/                       ← Governance templates
│       ├── ArchTests.csproj.blueprint
│       ├── ArchitectureTests.cs.blueprint
│       ├── pull_request.md.blueprint
│       └── review_guidelines.md.blueprint
├── references/                       ← Knowledge base
│   ├── dotnet-ddd.md                 ← Clean Architecture & DDD patterns
│   ├── ef-core-dba.md               ← EF Core & SQL Server performance
│   ├── react-frontend.md            ← Feature-based React patterns
│   ├── ux-ui-patterns.md            ← Design System & Usability
│   ├── code-review.md               ← Tech Lead code governance
│   ├── security-identity.md         ← JWT, OWASP, Auth patterns
│   └── devops-observability.md      ← SRE Docker, CI/CD, Logs
├── scripts/                          ← Scaffold generators
│   ├── scaffold_all.py              ← Master orchestrator (runs all)
│   ├── scaffold_backend.py          ← .NET Solution generator
│   ├── scaffold_frontend.py         ← React App generator
│   ├── scaffold_auth.py             ← Security & Identity generator
│   ├── scaffold_dba.py              ← Fluent API configurations
│   ├── scaffold_ux.py               ← Design System tokens
│   ├── scaffold_review.py           ← PR templates & ArchTests
│   └── scaffold_devops.py           ← Dockerfiles & CI/CD
├── evals/
│   └── evals.json                    ← Test scenarios for skill validation
└── adrs/
    └── template-adr.md              ← Architecture Decision Record template
```

---

## Reference Files

- **`references/dotnet-ddd.md`** — Clean Architecture & DDD patterns (Domain, Application, Infrastructure, API layers).
- **`references/ef-core-dba.md`** — EF Core performance mastery (indexing, multi-tenancy, strict typing, migrations).
- **`references/react-frontend.md`** — Feature-based React patterns (components, state, API, routing).
- **`references/ux-ui-patterns.md`** — Distinctive Design System & Usability (Glassmorphism, a11y, animations).
- **`references/code-review.md`** — Tech Lead guidelines for code governance (backend, DB, frontend, PR checklist).
- **`references/security-identity.md`** — JWT, RBAC, OWASP Top 10, secure communication.
- **`references/devops-observability.md`** — SRE patterns for Docker, CI/CD, Logging, and Resilience.

## Scaffold Scripts

- **`scripts/scaffold_all.py`** — Master orchestrator that runs all generators in order.
- **`scripts/scaffold_backend.py`** — Generates the .NET Solution (all 4 layers + extras).
- **`scripts/scaffold_frontend.py`** — Generates the React App with UI library.
- **`scripts/scaffold_auth.py`** — Generates JWT authentication & controllers.
- **`scripts/scaffold_dba.py`** — Generates Fluent API configurations & interceptors.
- **`scripts/scaffold_ux.py`** — Generates Design System tokens & shell layouts.
- **`scripts/scaffold_review.py`** — Generates PR templates and Architecture Tests.
- **`scripts/scaffold_devops.py`** — Generates Dockerfiles and CI/CD Workflows.
