# React + TypeScript Frontend Reference

This reference contains all the code patterns and templates for generating a production-grade React frontend with distinctive design, strict TypeScript, and modern architecture.

## Table of Contents

1. [Project Setup](#project-setup)
2. [Component Architecture](#component-architecture)
3. [State Management](#state-management)
4. [API Layer](#api-layer)
5. [Routing](#routing)
6. [UI Component Library](#ui-component-library)
7. [Design System](#design-system)
8. [Internationalization](#internationalization)
9. [Performance Patterns](#performance-patterns)
10. [Testing Patterns](#testing-patterns)

---

## Project Setup

### Vite Configuration

```bash
npm create vite@latest {name}-frontend -- --template react-ts
cd {name}-frontend
npm install react-router-dom zustand @tanstack/react-query axios zod
npm install -D tailwindcss postcss autoprefixer @types/react @types/react-dom
npx tailwindcss init -p
```

### tsconfig.json — Strict Mode

```json
{
  "compilerOptions": {
    "target": "ES2020",
    "useDefineForClassFields": true,
    "lib": ["ES2020", "DOM", "DOM.Iterable"],
    "module": "ESNext",
    "skipLibCheck": true,
    "moduleResolution": "bundler",
    "allowImportingTsExtensions": true,
    "isolatedModules": true,
    "moduleDetection": "force",
    "noEmit": true,
    "jsx": "react-jsx",
    "strict": true,
    "noUnusedLocals": true,
    "noUnusedParameters": true,
    "noFallthroughCasesInSwitch": true,
    "paths": {
      "@/*": ["./src/*"]
    }
  },
  "include": ["src"]
}
```

### Package.json Scripts

```json
{
  "scripts": {
    "dev": "vite",
    "build": "tsc && vite build",
    "lint": "eslint . --ext ts,tsx --report-unused-disable-directives --max-warnings 0",
    "preview": "vite preview",
    "test": "vitest",
    "test:coverage": "vitest --coverage"
  }
}
```

---

## Component Architecture

### File Organization

Each feature gets its own folder under `pages/`. Feature-specific components live inside that folder. Shared components live in `components/ui/` and `components/layout/`.

```
src/pages/tasks/
├── TasksPage.tsx              ← Main page component
├── TaskDetailPage.tsx         ← Detail view
└── components/
    ├── TaskItem.tsx            ← Feature-specific component
    ├── TaskFilters.tsx
    ├── CreateTaskModal.tsx
    └── __tests__/
        └── TaskItem.test.tsx
```

### Component Template — Typed Props (NEVER use `any`)

```tsx
import { memo, useCallback, useMemo } from 'react';
import type { Task, Priority, TaskStatus } from '@/types/task';

interface TaskItemProps {
  task: Task;
  onComplete: (taskId: string) => void;
  onSelect: (task: Task) => void;
  isSelected?: boolean;
}

export const TaskItem = memo(function TaskItem({
  task,
  onComplete,
  onSelect,
  isSelected = false,
}: TaskItemProps) {
  const handleComplete = useCallback(() => {
    onComplete(task.id);
  }, [task.id, onComplete]);

  const priorityColor = useMemo(() => {
    const colors: Record<Priority, string> = {
      Low: 'bg-emerald-500',
      Medium: 'bg-amber-500',
      High: 'bg-orange-500',
      Critical: 'bg-red-500',
    };
    return colors[task.priority];
  }, [task.priority]);

  const isOverdue = task.dueDate
    ? new Date(task.dueDate) < new Date() && task.status !== 'Completed'
    : false;

  return (
    <div
      className={`group relative flex items-center gap-3 rounded-lg border p-3
        transition-all duration-200 hover:-translate-y-0.5 hover:shadow-md
        ${isSelected ? 'border-accent ring-1 ring-accent/30' : 'border-border'}
        ${isOverdue ? 'border-red-500/50' : ''}
        ${task.status === 'Completed' ? 'opacity-60' : ''}`}
      onClick={() => onSelect(task)}
      role="button"
      tabIndex={0}
      aria-label={`Task: ${task.title}`}
    >
      <button
        onClick={(e) => { e.stopPropagation(); handleComplete(); }}
        className="shrink-0 w-5 h-5 rounded-full border-2 border-muted
          hover:border-accent transition-colors"
        aria-label={`Mark "${task.title}" as complete`}
      />

      <div className="flex-1 min-w-0">
        <p className="text-sm font-medium truncate">{task.title}</p>
        {task.dueDate && (
          <p className={`text-xs mt-0.5 ${isOverdue ? 'text-red-400' : 'text-muted'}`}>
            Due {new Date(task.dueDate).toLocaleDateString()}
          </p>
        )}
      </div>

      <span className={`w-2 h-2 rounded-full shrink-0 ${priorityColor}`} />
    </div>
  );
});
```

### Type Definitions — One File Per Domain

```typescript
// src/types/task.ts
export type TaskStatus = 'Pending' | 'InProgress' | 'InReview' | 'Completed' | 'Cancelled';
export type Priority = 'Low' | 'Medium' | 'High' | 'Critical';

export interface Task {
  id: string;
  title: string;
  description: string | null;
  status: TaskStatus;
  priority: Priority;
  dueDate: string | null;
  completedAt: string | null;
  projectId: string;
  assigneeId: string | null;
  isOverdue: boolean;
  createdAt: string;
}

export interface CreateTaskPayload {
  title: string;
  description?: string;
  projectId: string;
  priority: Priority;
  dueDate?: string;
}

export interface UpdateTaskPayload {
  title?: string;
  description?: string;
  priority?: Priority;
  dueDate?: string;
  status?: TaskStatus;
}

// src/types/common.ts
export interface PaginatedResult<T> {
  items: T[];
  totalCount: number;
  pageNumber: number;
  pageSize: number;
  totalPages: number;
  hasPreviousPage: boolean;
  hasNextPage: boolean;
}

export interface ApiError {
  status: number;
  title: string;
  detail: string;
  instance?: string;
}
```

---

## State Management

### Zustand Store Pattern

Each store manages one concern. Use `persist` for data that survives page reloads. Use `partialize` to exclude functions from storage.

```typescript
// src/store/authStore.ts
import { create } from 'zustand';
import { persist } from 'zustand/middleware';

interface User {
  id: string;
  email: string;
  name: string;
  role: string;
  companyId: string | null;
}

interface AuthState {
  user: User | null;
  token: string | null;
  isAuthenticated: boolean;
  login: (user: User, token: string) => void;
  logout: () => void;
  updateUser: (updates: Partial<User>) => void;
}

export const useAuthStore = create<AuthState>()(
  persist(
    (set) => ({
      user: null,
      token: null,
      isAuthenticated: false,

      login: (user, token) =>
        set({ user, token, isAuthenticated: true }),

      logout: () =>
        set({ user: null, token: null, isAuthenticated: false }),

      updateUser: (updates) =>
        set((state) => ({
          user: state.user ? { ...state.user, ...updates } : null,
        })),
    }),
    {
      name: '{name}_auth',
      partialize: (state) => ({
        user: state.user,
        token: state.token,
        isAuthenticated: state.isAuthenticated,
      }),
    }
  )
);
```

```typescript
// src/store/themeStore.ts
import { create } from 'zustand';
import { persist } from 'zustand/middleware';

type AccentColor = 'blue' | 'violet' | 'emerald' | 'amber' | 'rose' | 'cyan';

interface ThemeState {
  accentColor: AccentColor;
  isDarkMode: boolean;
  setAccentColor: (color: AccentColor) => void;
  toggleDarkMode: () => void;
}

const accentMap: Record<AccentColor, string> = {
  blue: '217 91% 60%',
  violet: '263 70% 50%',
  emerald: '160 84% 39%',
  amber: '38 92% 50%',
  rose: '347 77% 50%',
  cyan: '189 94% 43%',
};

export const useThemeStore = create<ThemeState>()(
  persist(
    (set) => ({
      accentColor: 'blue',
      isDarkMode: true,

      setAccentColor: (color) => {
        document.documentElement.style.setProperty('--accent-hsl', accentMap[color]);
        set({ accentColor: color });
      },

      toggleDarkMode: () =>
        set((state) => {
          const newMode = !state.isDarkMode;
          document.documentElement.classList.toggle('dark', newMode);
          return { isDarkMode: newMode };
        }),
    }),
    {
      name: '{name}_theme',
      partialize: (state) => ({
        accentColor: state.accentColor,
        isDarkMode: state.isDarkMode,
      }),
    }
  )
);
```

---

## API Layer

### HTTP Client with Interceptors

```typescript
// src/api/client.ts
import axios from 'axios';
import { useAuthStore } from '@/store/authStore';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:5000/api';

export const api = axios.create({
  baseURL: API_BASE_URL,
  headers: { 'Content-Type': 'application/json' },
});

// Request interceptor — adds auth token from Zustand (NOT localStorage directly)
api.interceptors.request.use((config) => {
  const token = useAuthStore.getState().token;
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// Response interceptor — handles 401 globally
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      useAuthStore.getState().logout();
      window.location.href = '/login';
    }

    // Extract ProblemDetails if available
    const detail = error.response?.data?.detail
      || error.response?.data?.title
      || error.message
      || 'An unexpected error occurred';

    return Promise.reject(new Error(detail));
  }
);
```

### Service Layer Pattern

One service file per domain entity. Services are pure functions that return typed data.

```typescript
// src/api/tasks.service.ts
import { api } from './client';
import type { Task, CreateTaskPayload, UpdateTaskPayload } from '@/types/task';
import type { PaginatedResult } from '@/types/common';

export const tasksApi = {
  getByProject: (projectId: string, page = 1, pageSize = 20) =>
    api.get<PaginatedResult<Task>>(`/tasks/project/${projectId}`, {
      params: { page, pageSize },
    }).then((r) => r.data),

  getById: (id: string) =>
    api.get<Task>(`/tasks/${id}`).then((r) => r.data),

  create: (data: CreateTaskPayload) =>
    api.post<string>('/tasks', data).then((r) => r.data),

  update: (id: string, data: UpdateTaskPayload) =>
    api.put<void>(`/tasks/${id}`, data),

  delete: (id: string) =>
    api.delete<void>(`/tasks/${id}`),

  complete: (id: string) =>
    api.patch<void>(`/tasks/${id}/complete`),
};
```

### React Query Integration

```tsx
// Inside a page component
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { tasksApi } from '@/api/tasks.service';

function TasksPage() {
  const queryClient = useQueryClient();

  const { data, isLoading, error } = useQuery({
    queryKey: ['tasks', projectId, page],
    queryFn: () => tasksApi.getByProject(projectId, page),
    staleTime: 2 * 60 * 1000, // 2 minutes
  });

  const createMutation = useMutation({
    mutationFn: (payload: CreateTaskPayload) => tasksApi.create(payload),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['tasks'] });
    },
    onError: (error: Error) => {
      // Show toast notification
    },
  });
}
```

---

## Routing

### App.tsx with Lazy Loading and Error Boundary

```tsx
import { lazy, Suspense } from 'react';
import { BrowserRouter, Routes, Route } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { ErrorBoundary } from '@/components/ErrorBoundary';
import { ProtectedRoute, PublicRoute, RoleGuard } from '@/routes/guards';
import { AppLayout } from '@/components/layout';

// Lazy load all pages — splits the bundle per route
const LoginPage = lazy(() => import('@/pages/LoginPage'));
const RegisterPage = lazy(() => import('@/pages/RegisterPage'));
const DashboardPage = lazy(() => import('@/pages/dashboard/DashboardPage'));
const ProjectsPage = lazy(() => import('@/pages/ProjectsPage'));
const TasksPage = lazy(() => import('@/pages/tasks/TasksPage'));
const TeamPage = lazy(() => import('@/pages/TeamPage'));
const ProfilePage = lazy(() => import('@/pages/profile/ProfilePage'));

const queryClient = new QueryClient({
  defaultOptions: {
    queries: { staleTime: 2 * 60 * 1000, retry: 1 },
  },
});

const LoadingFallback = () => (
  <div className="flex items-center justify-center h-screen">
    <div className="w-8 h-8 border-2 border-accent border-t-transparent rounded-full animate-spin" />
  </div>
);

export default function App() {
  return (
    <ErrorBoundary>
      <QueryClientProvider client={queryClient}>
        <BrowserRouter>
          <Suspense fallback={<LoadingFallback />}>
            <Routes>
              {/* Public routes — redirect to dashboard if already logged in */}
              <Route element={<PublicRoute />}>
                <Route path="/login" element={<LoginPage />} />
                <Route path="/register" element={<RegisterPage />} />
              </Route>

              {/* Protected routes — require authentication */}
              <Route element={<ProtectedRoute />}>
                <Route element={<AppLayout />}>
                  <Route path="/" element={<DashboardPage />} />
                  <Route path="/projects" element={<ProjectsPage />} />
                  <Route path="/tasks" element={<TasksPage />} />
                  <Route path="/profile" element={<ProfilePage />} />

                  {/* Role-protected routes */}
                  <Route element={<RoleGuard allowedRoles={['Owner', 'Admin']} />}>
                    <Route path="/team" element={<TeamPage />} />
                  </Route>
                </Route>
              </Route>
            </Routes>
          </Suspense>
        </BrowserRouter>
      </QueryClientProvider>
    </ErrorBoundary>
  );
}
```

### Route Guards

```tsx
// src/routes/guards.tsx
import { Navigate, Outlet } from 'react-router-dom';
import { useAuthStore } from '@/store/authStore';

export function ProtectedRoute() {
  const isAuthenticated = useAuthStore((s) => s.isAuthenticated);
  return isAuthenticated ? <Outlet /> : <Navigate to="/login" replace />;
}

export function PublicRoute() {
  const isAuthenticated = useAuthStore((s) => s.isAuthenticated);
  return isAuthenticated ? <Navigate to="/" replace /> : <Outlet />;
}

interface RoleGuardProps {
  allowedRoles: string[];
  fallback?: React.ReactNode;
}

export function RoleGuard({ allowedRoles, fallback }: RoleGuardProps) {
  const role = useAuthStore((s) => s.user?.role);

  if (!role || !allowedRoles.includes(role)) {
    return fallback ? <>{fallback}</> : <Navigate to="/" replace />;
  }

  return <Outlet />;
}
```

### Error Boundary

```tsx
// src/components/ErrorBoundary.tsx
import { Component, type ReactNode, type ErrorInfo } from 'react';

interface Props {
  children: ReactNode;
  fallback?: ReactNode;
}

interface State {
  hasError: boolean;
  error: Error | null;
}

export class ErrorBoundary extends Component<Props, State> {
  state: State = { hasError: false, error: null };

  static getDerivedStateFromError(error: Error): State {
    return { hasError: true, error };
  }

  componentDidCatch(error: Error, info: ErrorInfo) {
    console.error('ErrorBoundary caught:', error, info);
  }

  render() {
    if (this.state.hasError) {
      return this.props.fallback || (
        <div className="flex flex-col items-center justify-center h-screen gap-4">
          <h1 className="text-2xl font-bold text-red-400">Something went wrong</h1>
          <p className="text-muted max-w-md text-center">
            {this.state.error?.message || 'An unexpected error occurred.'}
          </p>
          <button
            onClick={() => window.location.reload()}
            className="px-4 py-2 bg-accent text-white rounded-lg hover:opacity-90 transition"
          >
            Reload Page
          </button>
        </div>
      );
    }
    return this.props.children;
  }
}
```

---

## UI Component Library

### Button Component

```tsx
// src/components/ui/Button.tsx
import { forwardRef, type ButtonHTMLAttributes } from 'react';

type Variant = 'primary' | 'secondary' | 'ghost' | 'destructive' | 'outline';
type Size = 'sm' | 'md' | 'lg' | 'icon';

interface ButtonProps extends ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: Variant;
  size?: Size;
  isLoading?: boolean;
}

const variantStyles: Record<Variant, string> = {
  primary: 'bg-accent text-white hover:opacity-90 focus:ring-2 focus:ring-accent/50',
  secondary: 'bg-surface-2 text-foreground hover:bg-surface-3',
  ghost: 'text-foreground hover:bg-surface-2',
  destructive: 'bg-red-600 text-white hover:bg-red-700',
  outline: 'border border-border text-foreground hover:bg-surface-2',
};

const sizeStyles: Record<Size, string> = {
  sm: 'h-8 px-3 text-xs',
  md: 'h-10 px-4 text-sm',
  lg: 'h-12 px-6 text-base',
  icon: 'h-10 w-10',
};

export const Button = forwardRef<HTMLButtonElement, ButtonProps>(
  ({ variant = 'primary', size = 'md', isLoading, children, className = '', disabled, ...props }, ref) => (
    <button
      ref={ref}
      disabled={disabled || isLoading}
      className={`inline-flex items-center justify-center gap-2 rounded-lg font-medium
        transition-all duration-200 disabled:opacity-50 disabled:cursor-not-allowed
        ${variantStyles[variant]} ${sizeStyles[size]} ${className}`}
      {...props}
    >
      {isLoading && (
        <span className="w-4 h-4 border-2 border-current border-t-transparent rounded-full animate-spin" />
      )}
      {children}
    </button>
  )
);
Button.displayName = 'Button';
```

### Card, Modal, Input, Badge

Follow the same pattern: typed props, forwardRef where applicable, variant system, consistent spacing, accessible attributes (aria-label, role, tabIndex).

---

## Design System

### CSS Variables and Theming

```css
/* src/index.css */
@tailwind base;
@tailwind components;
@tailwind utilities;

:root {
  --accent-hsl: 217 91% 60%;
  --bg: 220 20% 8%;
  --bg-surface: 220 18% 12%;
  --bg-surface-2: 220 16% 16%;
  --bg-surface-3: 220 14% 20%;
  --foreground: 220 10% 92%;
  --muted: 220 10% 55%;
  --border: 220 14% 20%;
}

body {
  background-color: hsl(var(--bg));
  color: hsl(var(--foreground));
  font-feature-settings: 'cv02', 'cv03', 'cv04', 'cv11';
}

/* Glass morphism utility */
.glass {
  background: hsla(var(--bg-surface), 0.6);
  backdrop-filter: blur(12px);
  border: 1px solid hsla(var(--border), 0.5);
}

/* Accent glow */
.glow-accent {
  box-shadow: 0 0 20px hsla(var(--accent-hsl), 0.15);
}

/* Smooth animations */
@keyframes fade-in {
  from { opacity: 0; transform: translateY(8px); }
  to { opacity: 1; transform: translateY(0); }
}

.animate-fade-in {
  animation: fade-in 0.3s ease-out;
}

/* Custom scrollbar */
::-webkit-scrollbar { width: 6px; }
::-webkit-scrollbar-track { background: transparent; }
::-webkit-scrollbar-thumb {
  background: hsla(var(--muted), 0.3);
  border-radius: 3px;
}
::-webkit-scrollbar-thumb:hover {
  background: hsla(var(--muted), 0.5);
}
```

### Design Principles — What Makes It Distinctive

The goal is to create interfaces that feel intentional and memorable, not generic. Here are the concrete principles:

1. **Typography** — Load a distinctive Google Font (not Inter, Roboto, or Arial). Pair a display font for headings with a refined body font. Use CSS `font-feature-settings` for ligatures and alternate glyphs.

2. **Color** — Use HSL with CSS variables. One dominant accent color that permeates the entire UI. Sharp contrast between surface layers (3-4 levels of depth). Never use more than 3 colors in a palette.

3. **Motion** — Staggered fade-in on page load (use `animation-delay`). Hover states that lift elements (`transform: translateY(-2px)`). Smooth transitions on every interactive element. Loading states with branded spinners, not generic ones.

4. **Spatial Composition** — Generous padding inside cards (p-4 minimum). Consistent gap system (gap-3 for tight, gap-6 for sections). Border-radius consistency (rounded-lg everywhere, or rounded-xl everywhere — pick one). Subtle border separators.

5. **Atmosphere** — Ambient gradient glows behind hero sections. Subtle noise textures or grain overlays. Glass morphism for floating elements. Accent-colored shadows (not just gray).

---

## Internationalization

### Custom i18n System (Lightweight Alternative to i18next)

```typescript
// src/i18n/index.ts
import ptBR from './locales/pt-BR';
import en from './locales/en';
import es from './locales/es';
import { useLanguageStore } from '@/store/languageStore';

type Locale = 'pt-BR' | 'en' | 'es';
type Translations = typeof ptBR;

const locales: Record<Locale, Translations> = { 'pt-BR': ptBR, en, es };

function getNestedValue(obj: Record<string, unknown>, path: string): string {
  const value = path.split('.').reduce<unknown>((acc, key) => {
    if (acc && typeof acc === 'object') return (acc as Record<string, unknown>)[key];
    return undefined;
  }, obj);
  return typeof value === 'string' ? value : path;
}

export function useT() {
  const locale = useLanguageStore((s) => s.locale);
  const translations = locales[locale];

  return (key: string, vars?: Record<string, string | number>): string => {
    let text = getNestedValue(translations as unknown as Record<string, unknown>, key);
    if (vars) {
      Object.entries(vars).forEach(([k, v]) => {
        text = text.replace(`{{${k}}}`, String(v));
      });
    }
    return text;
  };
}

export function detectBrowserLocale(): Locale {
  const lang = navigator.language;
  if (lang.startsWith('pt')) return 'pt-BR';
  if (lang.startsWith('es')) return 'es';
  return 'en';
}
```

---

## Performance Patterns

### Memoization Strategy

Apply `React.memo` to any component that renders inside a list (cards, rows, items). Use `useCallback` for event handlers passed as props. Use `useMemo` for expensive computations (filtering, sorting, mapping).

```tsx
// Memoize list items
export const TaskCard = memo(function TaskCard({ task, onSelect }: TaskCardProps) {
  // ...
});

// Memoize callbacks in parent
const handleSelect = useCallback((task: Task) => {
  setSelectedTask(task);
}, []);

// Memoize filtered data
const filteredTasks = useMemo(
  () => tasks.filter((t) => t.status === activeFilter),
  [tasks, activeFilter]
);
```

### Lazy Loading Strategy

Every page-level route should be lazy loaded. Heavy components (charts, modals with complex forms) can also be lazy loaded.

```tsx
const TaskChart = lazy(() => import('./components/TaskChart'));
```

### Image Optimization

All `<img>` tags must include `loading="lazy"` and explicit dimensions.

```tsx
<img src={avatarUrl} alt={name} loading="lazy" width={40} height={40} />
```

---

## Testing Patterns

### Vitest + React Testing Library

```typescript
// src/test/setup.ts
import '@testing-library/jest-dom';

// Mock IntersectionObserver
class MockIntersectionObserver {
  observe = vi.fn();
  unobserve = vi.fn();
  disconnect = vi.fn();
}
Object.defineProperty(window, 'IntersectionObserver', {
  writable: true,
  value: MockIntersectionObserver,
});
```

### Component Test Template

```tsx
import { render, screen, fireEvent } from '@testing-library/react';
import { describe, it, expect, vi } from 'vitest';
import { Button } from '../Button';

describe('Button', () => {
  it('renders with correct text', () => {
    render(<Button>Click me</Button>);
    expect(screen.getByRole('button', { name: /click me/i })).toBeInTheDocument();
  });

  it('calls onClick when clicked', () => {
    const onClick = vi.fn();
    render(<Button onClick={onClick}>Click</Button>);
    fireEvent.click(screen.getByRole('button'));
    expect(onClick).toHaveBeenCalledOnce();
  });

  it('shows loading spinner when isLoading', () => {
    render(<Button isLoading>Submit</Button>);
    expect(screen.getByRole('button')).toBeDisabled();
  });

  it('applies variant styles', () => {
    const { container } = render(<Button variant="destructive">Delete</Button>);
    expect(container.firstChild).toHaveClass('bg-red-600');
  });
});
```

### Store Test Template

```typescript
import { describe, it, expect, beforeEach } from 'vitest';
import { useAuthStore } from '../authStore';

describe('authStore', () => {
  beforeEach(() => {
    useAuthStore.setState({
      user: null,
      token: null,
      isAuthenticated: false,
    });
  });

  it('should login correctly', () => {
    const user = { id: '1', email: 'test@test.com', name: 'Test', role: 'Member', companyId: null };
    useAuthStore.getState().login(user, 'jwt-token');

    const state = useAuthStore.getState();
    expect(state.isAuthenticated).toBe(true);
    expect(state.user).toEqual(user);
    expect(state.token).toBe('jwt-token');
  });

  it('should logout correctly', () => {
    useAuthStore.getState().login(
      { id: '1', email: 'test@test.com', name: 'Test', role: 'Member', companyId: null },
      'token'
    );
    useAuthStore.getState().logout();

    const state = useAuthStore.getState();
    expect(state.isAuthenticated).toBe(false);
    expect(state.user).toBeNull();
  });
});
```
