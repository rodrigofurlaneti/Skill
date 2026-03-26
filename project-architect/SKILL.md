---
name: project-architect
description: >
  Fullstack project architect for .NET + React applications. Use this skill whenever the user wants to:
  create a new project from scratch (scaffold), validate an existing project's architecture,
  refactor code to follow DDD/Clean Architecture/SOLID/Repository patterns, or generate boilerplate
  for .NET WebAPI backends and React TypeScript frontends. Trigger on mentions of: "criar projeto",
  "new project", "scaffold", "arquitetura", "DDD", "clean architecture", "SOLID", "repository pattern",
  "validate architecture", "project structure", "boilerplate", ".NET + React", "fullstack template",
  "refactor to DDD", "projeto novo", "estrutura de pastas", or any request to generate or review
  a professional fullstack application. Also trigger when the user mentions wanting to follow best
  practices for backend API design or frontend component architecture. Even if they just say
  "start a new app" or "create an API with frontend" — this skill applies.
---

# Project Architect — .NET DDD + React Fullstack Skill

This skill creates production-grade fullstack applications following battle-tested patterns, or validates existing projects against these standards. It encapsulates the architecture wisdom of real-world projects: Domain-Driven Design, Clean Architecture, SOLID principles, Repository Pattern, and distinctive frontend design.

## When This Skill Activates

There are two modes of operation:

1. **Scaffold Mode** — Generate a new project from scratch
2. **Audit Mode** — Analyze an existing project and fix architectural violations

Detect which mode based on the user's request. If ambiguous, ask.

---

## Step 1: Gather Requirements

Before generating anything, understand what the user needs. Ask about:

- **Project name** (used for namespaces, folder names, solution name)
- **Domain entities** (what the app manages — e.g., Tasks, Projects, Users)
- **Database** preference: SQL Server, PostgreSQL, or SQLite (default: SQL Server)
- **Frontend CSS** approach: Tailwind CSS, Styled Components, or CSS Modules (default: Tailwind)
- **Authentication**: JWT Bearer (default), Identity, or External (Auth0/Azure AD)
- **Deployment target**: Azure, AWS, Docker, or Local-only

If the user already provided context (e.g., "create a task management app"), infer what you can and confirm.

---

## Step 2: Architecture Overview

### Backend (.NET) — Clean Architecture + DDD

The backend follows a strict layered architecture where dependencies flow inward. Every project references only the layers below it, never above.

```
Solution/
├── src/
│   ├── {Name}.Domain/           ← Innermost: entities, value objects, domain events
│   ├── {Name}.Application/      ← Use cases: CQRS commands/queries, validators, DTOs
│   ├── {Name}.Infrastructure/   ← Outer: EF Core, repositories, external services
│   └── {Name}.API/              ← Entry point: controllers, middleware, DI config
├── tests/
│   ├── {Name}.Domain.Tests/
│   ├── {Name}.Application.Tests/
│   └── {Name}.API.Tests/
└── {Name}.sln
```

**Why this structure matters**: Domain logic has zero dependencies on frameworks or infrastructure. You can swap databases, APIs, or UI layers without touching business rules. This is the core promise of Clean Architecture — and it only works if the dependency rule is strictly enforced.

Read `references/dotnet-ddd.md` for the complete .NET patterns, code templates, and implementation details.

### Frontend (React + TypeScript)

The frontend follows a feature-based architecture with distinctive, non-generic design.

```
src/
├── api/              ← Service layer (one file per domain)
├── components/
│   ├── ui/           ← Reusable primitives (Button, Card, Modal, Input, etc.)
│   └── layout/       ← Shell components (Sidebar, Header, Layout)
├── pages/            ← Feature folders (auth/, dashboard/, tasks/, etc.)
│   └── {feature}/
│       ├── {Feature}Page.tsx
│       └── components/    ← Feature-specific components
├── store/            ← Zustand stores (one per concern)
├── types/            ← TypeScript interfaces (one per domain)
├── routes/           ← Route guards (ProtectedRoute, RoleGuard)
├── i18n/             ← Internationalization
├── lib/              ← Utilities
└── test/             ← Test configuration
```

Read `references/react-frontend.md` for the complete React patterns, component templates, and design system guidelines.

---

## Step 3: Generate or Audit

### Scaffold Mode

When generating a new project, follow this exact sequence:

1. **Create the .NET solution structure** — Use the scaffold script or generate files manually
2. **Domain Layer first** — Entities with rich behavior, Value Objects, Domain Events, Interfaces
3. **Application Layer** — CQRS with MediatR, Validators with FluentValidation, DTOs, Pipeline Behaviors
4. **Infrastructure Layer** — EF Core DbContext, Repository implementations, external service adapters
5. **API Layer** — Controllers inheriting ApiController base, middleware, Program.cs with proper DI
6. **Frontend structure** — Vite + React + TypeScript, feature-based pages, Zustand stores, API services
7. **UI Component Library** — Button, Card, Modal, Input, Badge, Avatar, Spinner, Select, EmptyState
8. **Pages** — Auth (Login/Register), Dashboard, feature pages with CRUD
9. **Configuration** — appsettings.json, .env, docker-compose (if requested)

Run `scripts/scaffold_backend.py` and `scripts/scaffold_frontend.py` if available. Otherwise, generate files directly.

### Audit Mode

When auditing an existing project:

1. **Map the current structure** — List all projects/folders, identify the architectural layers
2. **Check dependency rule** — Domain must not reference Application, Infrastructure, or API
3. **Verify DDD patterns** — Rich entities (not anemic), Value Objects, Domain Events, Aggregates
4. **Verify CQRS** — Commands vs Queries separated, proper use of MediatR
5. **Check SOLID violations** — Single Responsibility in controllers, Open/Closed in services, etc.
6. **Review API patterns** — Consistent error handling, proper status codes, validation
7. **Frontend patterns** — TypeScript strictness, component reuse, state management, routing
8. **Generate report** — List all violations with file paths, severity, and fix suggestions
9. **Apply fixes** — With user approval, fix violations automatically

---

## Critical Patterns Checklist

These are the non-negotiable patterns that every generated or audited project must follow:

### Backend Must-Haves

- [ ] **Entity base class** with Id, CreatedAt, UpdatedAt, domain events collection
- [ ] **No anemic entities** — business logic lives IN the entity, not in services
- [ ] **Value Objects** for validated types (Email, Name, etc.) with `implicit operator`
- [ ] **Repository interfaces** in Domain, implementations in Infrastructure
- [ ] **CQRS** — Commands return Result, Queries return DTOs (never entities)
- [ ] **FluentValidation** for every Command
- [ ] **Pipeline Behaviors** — Validation, Logging, Performance monitoring
- [ ] **Global Exception Middleware** — Consistent ProblemDetails responses
- [ ] **Base ApiController** with `Problem()` helper for Result → HTTP mapping
- [ ] **CancellationToken** propagated through all async chains
- [ ] **PaginatedResult<T>** for all list queries
- [ ] **Input sanitization** helper (HtmlEncode)
- [ ] **No stack traces in production** error responses

### Frontend Must-Haves

- [ ] **Zero `any` types** — strict TypeScript throughout
- [ ] **ErrorBoundary** wrapping the app
- [ ] **Lazy loading** routes with React.lazy + Suspense
- [ ] **Route guards** — ProtectedRoute + RoleGuard
- [ ] **React.memo** on list item components (cards, rows)
- [ ] **Zustand** stores with `persist` middleware and `partialize`
- [ ] **API client** with interceptors (auth token, error handling)
- [ ] **Distinctive design** — no generic AI aesthetics (see frontend-design principles)
- [ ] **i18n** ready from day one
- [ ] **CSS variables** for theming (accent colors, dark mode)
- [ ] **Image lazy loading** (`loading="lazy"`)
- [ ] **Accessible** — proper ARIA labels, focus management, keyboard navigation

---

## Design Philosophy

### Backend: "The domain is sacred"

Everything flows from the domain. When in doubt about where code belongs, ask: "Is this a business rule or an infrastructure concern?" Business rules go in Domain. Orchestration of business rules goes in Application. Everything else goes in Infrastructure.

The Result pattern (instead of throwing exceptions for expected failures) makes error handling explicit and forces callers to deal with failure cases. This is not about being pedantic — it's about making the system predictable and debuggable.

### Frontend: "Distinctive, not decorative"

Every interface should have a clear aesthetic point-of-view. This means:
- Typography that has character (not Inter, not Roboto, not Arial)
- Color palettes that are intentional (dominant color + sharp accents)
- Animations that serve purpose (staggered reveals, hover states that surprise)
- Layouts that break the grid when it makes sense

The goal is not to add complexity for its own sake — it's to make interfaces that people remember and enjoy using.

---

## Reference Files

For detailed implementation patterns and code templates, read these reference files:

- **`references/dotnet-ddd.md`** — Complete .NET patterns: Entity base class, Value Objects, CQRS handlers, Repository pattern, Pipeline Behaviors, API controller base, middleware, Program.cs configuration, EF Core setup
- **`references/react-frontend.md`** — Complete React patterns: Component templates, Zustand store patterns, API service layer, routing setup, UI component library, design system, CSS approach, testing patterns

Read the relevant reference file before generating code for that layer.
