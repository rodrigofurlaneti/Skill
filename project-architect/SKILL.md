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

1. **Scaffold Mode** — Generate a new project from scratch (Backend, Database, Frontend, UX, DevOps).
2. **Audit Mode** — Analyze an existing project for architectural, database, or usability violations.
3. **Review Mode (Tech Lead)** — Professional code review of snippets or Pull Requests to ensure the "Gold Standard".
4. **Ops Mode (SRE)** — Configure Docker, CI/CD pipelines, and structured observability.

---

## Step 1: Gather Requirements

Before generating or reviewing, ask (if not provided):
- **Project/Feature name** & **Domain context**.
- **Database**: SQL Server (default), PostgreSQL, or MySQL.
- **Multi-tenancy**: Is data isolation required? (Critical for FSI patterns).
- **Infrastructure**: Docker required? Target CI/CD (GitHub Actions default).

---

## Step 2: Architecture & Governance Overview

### Backend (.NET) — Clean Architecture + Senior DBA
The backend follows a strict layered architecture where dependencies flow inward.
- **Domain Layer**: Sacred business rules, rich entities, and value objects.
- **Infrastructure Layer**: Explicit Fluent API mappings and performance-tuned queries.
- **DB Mastery**: No `nvarchar(max)`, mandatory `AsNoTracking` for reads, and `AsSplitQuery`.

### Frontend (React + TypeScript) — Feature-Based + UX Specialist
- **UI/UX**: Glassmorphism, Plus Jakarta Sans typography, and high-performance animations.
- **State**: Zustand with persistence and strict TypeScript interfaces.

### Code Review & DevOps — Tech Lead + SRE Governance
- **Tech Lead**: DRY, KISS, Result Pattern, and NetArchTest enforcement.
- **SRE**: Multi-stage Dockerfiles (Alpine), CI/CD pipelines, and Structured Logging (Serilog).

---

## Critical Patterns Checklist (The Gold Standard)

### 1. Backend & DBA Must-Haves
- [ ] **Rich Entities**: Business logic IN the entity; private setters for EF Core.
- [ ] **Fluent API**: Use `IEntityTypeConfiguration<T>` (No Data Annotations).
- [ ] **Read Performance**: All read queries MUST use `.AsNoTracking()`.
- [ ] **Data Isolation**: `.HasQueryFilter()` for multi-tenant protection (FSI pattern).

### 2. Frontend & UX Must-Haves
- [ ] **Zero `any` types**: Strict TypeScript throughout.
- [ ] **Glassmorphism**: Consistent use of `glass` utility classes and `backdrop-blur`.
- [ ] **A11y**: Proper ARIA labels and contrast compliance.

### 3. Review & Ops (The Safety Net)
- [ ] **Async Hygiene**: `CancellationToken` propagated through all async calls.
- [ ] **Result Pattern**: Explicit success/failure handling (No business exceptions).
- [ ] **Docker Security**: Non-root users and Alpine-based images.
- [ ] **Observability**: Structured JSON logs and `/health` endpoints.

---

## Reference Files

- **`references/dotnet-ddd.md`** — Clean Architecture & DDD patterns.
- **`references/ef-core-dba.md`** — EF Core & SQL Server performance mastery.
- **`references/react-frontend.md`** — Feature-based React patterns.
- **`references/ux-ui-patterns.md`** — Distinctive Design System & Usability.
- **`references/code-review.md`** — Tech Lead guidelines for code governance.
- **`references/devops-observability.md`** — SRE patterns for Docker, CI/CD, and Logs.

## Scaffold & Automation Scripts

- **`scripts/scaffold_backend.py`** — Generates the .NET Solution.
- **`scripts/scaffold_frontend.py`** — Generates the React App.
- **`scripts/scaffold_dba.py`** — Generates Fluent API configurations.
- **`scripts/scaffold_ux.py`** — Generates Design System tokens.
- **`scripts/scaffold_review.py`** — Generates PR templates and ArchTests.
- **`scripts/scaffold_devops.py`** — Generates Dockerfiles and CI/CD Workflows.