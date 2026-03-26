---
name: project-architect
description: >
  Fullstack project architect for .NET + React applications with Senior DBA and UX/UI Specialist focus. 
  Use this skill to create projects from scratch (scaffold), validate architectures, refactor code to 
  follow DDD/Clean Architecture/SOLID, optimize EF Core performance, or design distinctive user interfaces.
  Trigger on: "criar projeto", "scaffold", "DDD", "clean architecture", "EF Core performance", 
  "multi-tenant isolation", "design system", "UX/UI", "glassmorphism", "melhorar interface".
---

# Project Architect — .NET DDD + React + DBA & UX Mastery

This skill creates production-grade fullstack applications following battle-tested patterns, or validates existing projects against these standards. It encapsulates the architecture wisdom of real-world projects: Domain-Driven Design, Clean Architecture, SOLID principles, High-Performance Database Design, and Distinctive UX/UI.

## When This Skill Activates

There are two modes of operation:
1. **Scaffold Mode** — Generate a new project from scratch (Backend, Database, and Frontend).
2. **Audit Mode** — Analyze an existing project for architectural, database, or usability violations.

---

## Step 1: Gather Requirements

Before generating, ask about:
- **Project name** (namespaces, folders, solution).
- **Domain entities** (what the app manages).
- **Database**: SQL Server (default), PostgreSQL, or MySQL.
- **Multi-tenancy**: Is data isolation required? (Critical for FSI patterns).
- **UI Style**: Glassmorphism (default) or Flat Modern.

---

## Step 2: Architecture & Design Overview

### Backend (.NET) — Clean Architecture + Senior DBA
The backend follows a strict layered architecture where dependencies flow inward.
- **Domain Layer**: Sacred business rules, rich entities, and value objects.
- **Infrastructure Layer**: Explicit Fluent API mappings, optimized indexes, and performance-tuned queries.
- **DB Focus**: No `nvarchar(max)`, mandatory `AsNoTracking` for reads, and `AsSplitQuery` for complex graphs.

### Frontend (React + TypeScript) — Feature-Based + UX Specialist
The frontend follows a feature-based architecture with a "Distinctive, not decorative" philosophy.
- **UI/UX**: Glassmorphism, Plus Jakarta Sans typography, and high-performance animations.
- **Design System**: Strict spacing grid, accessibility (a11y), and consistent HSL color tokens.

---

## Critical Patterns Checklist (The Gold Standard)

### 1. Backend & DBA Must-Haves
- [ ] **Rich Entities**: Business logic IN the entity; private setters for EF Core.
- [ ] **Fluent API**: Use `IEntityTypeConfiguration<T>` (No Data Annotations).
- [ ] **Strict SQL Typing**: Explicit `HasMaxLength(n)` and `HasColumnType("decimal(18,2)")`.
- [ ] **Read Performance**: All read queries MUST use `.AsNoTracking()`.
- [ ] **Data Isolation**: `.HasQueryFilter()` for multi-tenant protection (FSI pattern).
- [ ] **Cartesian Guard**: Use `.AsSplitQuery()` for complex `.Include()` chains.
- [ ] **CancellationToken**: Propagated through all async chains (API to DB).
- [ ] **CQRS**: Commands return `Result<T>`, Queries return DTOs (never entities).

### 2. Frontend & UX Must-Haves
- [ ] **Zero `any` types**: Strict TypeScript throughout.
- [ ] **Lazy Loading**: Route-based code splitting with `React.lazy + Suspense`.
- [ ] **Glassmorphism**: Consistent use of `glass` utility classes and `backdrop-blur`.
- [ ] **Accessibility**: Proper ARIA labels, focus states, and 4.5:1 contrast ratio.
- [ ] **Zustand Persistence**: Stores with `persist` middleware and `partialize`.
- [ ] **Performance**: `React.memo` for list items and `useCallback` for props-drilled handlers.

---

## Design Philosophy

### "The Domain is Sacred, the DB is Optimized"
Business rules belong in the Domain. Database performance is ensured by explicit mappings and index strategies. We avoid generic AI aesthetics by using intentional typography and motion that serves a purpose.

### "Database is not a dump"
The schema must be as clean as the code. Mappings must be explicit to avoid `nvarchar(max)`. Every query is written thinking about the execution plan.

---

## Reference Files

For detailed implementation patterns, read these reference files:

- **`references/dotnet-ddd.md`** — Clean Architecture & DDD patterns.
- **`references/ef-core-dba.md`** — EF Core & SQL Server performance mastery.
- **`references/react-frontend.md`** — Feature-based React & TypeScript patterns.
- **`references/ux-ui-patterns.md`** — Distinctive Design System & Usability.

## Scaffold Scripts

- **`scripts/scaffold_backend.py`** — Generates the .NET Solution.
- **`scripts/scaffold_frontend.py`** — Generates the React App.
- **`scripts/scaffold_dba.py`** — Generates Fluent API and Persistence configurations.
- **`scripts/scaffold_ux.py`** — Generates Design System tokens and UI components.