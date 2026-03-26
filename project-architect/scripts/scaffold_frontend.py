#!/usr/bin/env python3
"""
Scaffold Generator for React + TypeScript Frontend
Generates a complete feature-based architecture with distinctive design.

Usage:
    python scaffold_frontend.py --name MyApp --output ./output --css tailwind
"""

import argparse
import os
from pathlib import Path

def create_file(path: str, content: str):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f"  Created: {path}")

def scaffold(name: str, output: str, css: str = "tailwind", features: list[str] = None):
    if features is None:
        features = ["dashboard", "tasks", "projects"]

    base = Path(output) / f"{name}-frontend"
    src = base / "src"
    name_lower = name.lower()
    api_url = f"http://localhost:5000/api"

    print(f"\n🎨 Scaffolding {name} Frontend (React + TypeScript)")
    print(f"   CSS: {css}")
    print(f"   Features: {', '.join(features)}")
    print(f"   Output: {base}\n")

    # ========== Root Config Files ==========
    create_file(str(base / "package.json"), generate_package_json(name_lower))
    create_file(str(base / "tsconfig.json"), generate_tsconfig())
    create_file(str(base / "vite.config.ts"), generate_vite_config())
    create_file(str(base / "index.html"), generate_index_html(name))
    create_file(str(base / ".env"), f"VITE_API_URL={api_url}")
    create_file(str(base / ".gitignore"), generate_gitignore())

    if css == "tailwind":
        create_file(str(base / "tailwind.config.js"), generate_tailwind_config())
        create_file(str(base / "postcss.config.js"), generate_postcss_config())

    # ========== Source Files ==========
    create_file(str(src / "main.tsx"), generate_main())
    create_file(str(src / "App.tsx"), generate_app(features))
    create_file(str(src / "index.css"), generate_index_css())
    create_file(str(src / "vite-env.d.ts"), '/// <reference types="vite/client" />')

    # ========== API Layer ==========
    create_file(str(src / "api" / "client.ts"), generate_api_client(name_lower))

    # ========== Store ==========
    create_file(str(src / "store" / "authStore.ts"), generate_auth_store(name_lower))
    create_file(str(src / "store" / "themeStore.ts"), generate_theme_store(name_lower))

    # ========== Types ==========
    create_file(str(src / "types" / "common.ts"), generate_common_types())
    create_file(str(src / "types" / "auth.ts"), generate_auth_types())

    # ========== Routes ==========
    create_file(str(src / "routes" / "guards.tsx"), generate_route_guards())

    # ========== Components ==========
    create_file(str(src / "components" / "ErrorBoundary.tsx"), generate_error_boundary())
    create_file(str(src / "components" / "ui" / "Button.tsx"), generate_button_component())
    create_file(str(src / "components" / "ui" / "Card.tsx"), generate_card_component())
    create_file(str(src / "components" / "ui" / "Input.tsx"), generate_input_component())
    create_file(str(src / "components" / "ui" / "Modal.tsx"), generate_modal_component())
    create_file(str(src / "components" / "ui" / "Spinner.tsx"), generate_spinner_component())
    create_file(str(src / "components" / "ui" / "Badge.tsx"), generate_badge_component())
    create_file(str(src / "components" / "ui" / "index.ts"), generate_ui_barrel())
    create_file(str(src / "components" / "layout" / "index.tsx"), generate_layout())
    create_file(str(src / "components" / "layout" / "Sidebar.tsx"), generate_sidebar(name, features))

    # ========== Pages ==========
    create_file(str(src / "pages" / "LoginPage.tsx"), generate_login_page())
    create_file(str(src / "pages" / "RegisterPage.tsx"), generate_register_page())

    for feature in features:
        cap = feature.capitalize()
        create_file(str(src / "pages" / feature / f"{cap}Page.tsx"),
                    generate_feature_page(cap))

    # ========== Test Setup ==========
    create_file(str(src / "test" / "setup.ts"), generate_test_setup())

    # ========== i18n ==========
    create_file(str(src / "i18n" / "index.ts"), generate_i18n_index())
    create_file(str(src / "i18n" / "locales" / "en.ts"), generate_locale_en(features))
    create_file(str(src / "i18n" / "locales" / "pt-BR.ts"), generate_locale_ptbr(features))

    print(f"\n✅ Frontend scaffold complete!")
    print(f"   Next steps:")
    print(f"   1. cd {base}")
    print(f"   2. npm install")
    print(f"   3. npm run dev")


# ==================== GENERATORS ====================

def generate_package_json(name):
    return f"""{{
  "name": "{name}-frontend",
  "private": true,
  "version": "1.0.0",
  "type": "module",
  "scripts": {{
    "dev": "vite",
    "build": "tsc && vite build",
    "preview": "vite preview",
    "test": "vitest",
    "test:coverage": "vitest --coverage",
    "lint": "eslint . --ext ts,tsx"
  }},
  "dependencies": {{
    "react": "^18.3.0",
    "react-dom": "^18.3.0",
    "react-router-dom": "^6.26.0",
    "zustand": "^4.5.0",
    "@tanstack/react-query": "^5.50.0",
    "axios": "^1.7.0",
    "zod": "^3.23.0",
    "lucide-react": "^0.400.0"
  }},
  "devDependencies": {{
    "@types/react": "^18.3.0",
    "@types/react-dom": "^18.3.0",
    "@vitejs/plugin-react": "^4.3.0",
    "typescript": "^5.5.0",
    "vite": "^5.4.0",
    "vitest": "^2.0.0",
    "@testing-library/react": "^16.0.0",
    "@testing-library/jest-dom": "^6.4.0",
    "tailwindcss": "^3.4.0",
    "postcss": "^8.4.0",
    "autoprefixer": "^10.4.0"
  }}
}}"""

def generate_tsconfig():
    return """{
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
}"""

def generate_vite_config():
    return """import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';
import path from 'path';

export default defineConfig({
  plugins: [react()],
  resolve: {
    alias: {
      '@': path.resolve(__dirname, './src'),
    },
  },
  build: {
    rollupOptions: {
      output: {
        manualChunks: {
          vendor: ['react', 'react-dom', 'react-router-dom'],
          state: ['zustand', '@tanstack/react-query'],
        },
      },
    },
  },
});"""

def generate_index_html(name):
    return f"""<!DOCTYPE html>
<html lang="en" class="dark">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <link rel="preconnect" href="https://fonts.googleapis.com" />
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin />
    <link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700&display=swap" rel="stylesheet" />
    <title>{name}</title>
  </head>
  <body>
    <div id="root"></div>
    <script type="module" src="/src/main.tsx"></script>
  </body>
</html>"""

def generate_gitignore():
    return """node_modules/
dist/
.env.local
.env.production.local
"""

def generate_tailwind_config():
    return """/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{js,ts,jsx,tsx}'],
  darkMode: 'class',
  theme: {
    extend: {
      fontFamily: {
        sans: ['Plus Jakarta Sans', 'system-ui', 'sans-serif'],
      },
      colors: {
        accent: 'hsl(var(--accent-hsl))',
        'accent-hover': 'hsl(var(--accent-hsl) / 0.85)',
        surface: {
          DEFAULT: 'hsl(var(--bg-surface))',
          2: 'hsl(var(--bg-surface-2))',
          3: 'hsl(var(--bg-surface-3))',
        },
        foreground: 'hsl(var(--foreground))',
        muted: 'hsl(var(--muted))',
        border: 'hsl(var(--border))',
      },
    },
  },
  plugins: [],
};"""

def generate_postcss_config():
    return """export default {
  plugins: {
    tailwindcss: {},
    autoprefixer: {},
  },
};"""

def generate_main():
    return """import React from 'react';
import ReactDOM from 'react-dom/client';
import App from './App';
import './index.css';

ReactDOM.createRoot(document.getElementById('root')!).render(
  <React.StrictMode>
    <App />
  </React.StrictMode>
);"""

def generate_app(features):
    lazy_imports = "\n".join([
        f"const {f.capitalize()}Page = lazy(() => import('@/pages/{f}/{f.capitalize()}Page'));"
        for f in features
    ])
    routes = "\n".join([
        f'                  <Route path="/{f}" element={{<{f.capitalize()}Page />}} />'
        for f in features
    ])
    return f"""import {{ lazy, Suspense }} from 'react';
import {{ BrowserRouter, Routes, Route }} from 'react-router-dom';
import {{ QueryClient, QueryClientProvider }} from '@tanstack/react-query';
import {{ ErrorBoundary }} from '@/components/ErrorBoundary';
import {{ ProtectedRoute, PublicRoute }} from '@/routes/guards';
import {{ AppLayout }} from '@/components/layout';

const LoginPage = lazy(() => import('@/pages/LoginPage'));
const RegisterPage = lazy(() => import('@/pages/RegisterPage'));
{lazy_imports}

const queryClient = new QueryClient({{
  defaultOptions: {{
    queries: {{ staleTime: 2 * 60 * 1000, retry: 1 }},
  }},
}});

const LoadingFallback = () => (
  <div className="flex items-center justify-center h-screen bg-[hsl(var(--bg))]">
    <div className="w-8 h-8 border-2 border-accent border-t-transparent rounded-full animate-spin" />
  </div>
);

export default function App() {{
  return (
    <ErrorBoundary>
      <QueryClientProvider client={{queryClient}}>
        <BrowserRouter>
          <Suspense fallback={{<LoadingFallback />}}>
            <Routes>
              <Route element={{<PublicRoute />}}>
                <Route path="/login" element={{<LoginPage />}} />
                <Route path="/register" element={{<RegisterPage />}} />
              </Route>

              <Route element={{<ProtectedRoute />}}>
                <Route element={{<AppLayout />}}>
{routes}
                </Route>
              </Route>
            </Routes>
          </Suspense>
        </BrowserRouter>
      </QueryClientProvider>
    </ErrorBoundary>
  );
}}"""

def generate_index_css():
    return """@tailwind base;
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
  font-family: 'Plus Jakarta Sans', system-ui, sans-serif;
  font-feature-settings: 'cv02', 'cv03', 'cv04', 'cv11';
  -webkit-font-smoothing: antialiased;
}

/* Glass morphism */
.glass {
  background: hsla(var(--bg-surface), 0.6);
  backdrop-filter: blur(12px);
  border: 1px solid hsla(var(--border), 0.5);
}

/* Accent glow */
.glow-accent {
  box-shadow: 0 0 20px hsla(var(--accent-hsl), 0.15);
}

/* Animations */
@keyframes fade-in {
  from { opacity: 0; transform: translateY(8px); }
  to { opacity: 1; transform: translateY(0); }
}

@keyframes slide-in {
  from { opacity: 0; transform: translateX(-12px); }
  to { opacity: 1; transform: translateX(0); }
}

.animate-fade-in {
  animation: fade-in 0.3s ease-out;
}

.animate-slide-in {
  animation: slide-in 0.25s ease-out;
}

/* Custom Scrollbar */
::-webkit-scrollbar { width: 6px; }
::-webkit-scrollbar-track { background: transparent; }
::-webkit-scrollbar-thumb {
  background: hsla(var(--muted), 0.3);
  border-radius: 3px;
}
::-webkit-scrollbar-thumb:hover {
  background: hsla(var(--muted), 0.5);
}"""

def generate_api_client(name):
    return f"""import axios from 'axios';
import {{ useAuthStore }} from '@/store/authStore';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:5000/api';

export const api = axios.create({{
  baseURL: API_BASE_URL,
  headers: {{ 'Content-Type': 'application/json' }},
}});

api.interceptors.request.use((config) => {{
  const token = useAuthStore.getState().token;
  if (token) {{
    config.headers.Authorization = `Bearer ${{token}}`;
  }}
  return config;
}});

api.interceptors.response.use(
  (response) => response,
  (error) => {{
    if (error.response?.status === 401) {{
      useAuthStore.getState().logout();
      window.location.href = '/login';
    }}

    const detail = error.response?.data?.detail
      || error.response?.data?.title
      || error.message
      || 'An unexpected error occurred';

    return Promise.reject(new Error(detail));
  }}
);"""

def generate_auth_store(name):
    return f"""import {{ create }} from 'zustand';
import {{ persist }} from 'zustand/middleware';

interface User {{
  id: string;
  email: string;
  name: string;
  role: string;
  companyId: string | null;
}}

interface AuthState {{
  user: User | null;
  token: string | null;
  isAuthenticated: boolean;
  login: (user: User, token: string) => void;
  logout: () => void;
  updateUser: (updates: Partial<User>) => void;
}}

export const useAuthStore = create<AuthState>()(
  persist(
    (set) => ({{
      user: null,
      token: null,
      isAuthenticated: false,

      login: (user, token) => set({{ user, token, isAuthenticated: true }}),
      logout: () => set({{ user: null, token: null, isAuthenticated: false }}),
      updateUser: (updates) =>
        set((state) => ({{
          user: state.user ? {{ ...state.user, ...updates }} : null,
        }})),
    }}),
    {{
      name: '{name}_auth',
      partialize: (state) => ({{
        user: state.user,
        token: state.token,
        isAuthenticated: state.isAuthenticated,
      }}),
    }}
  )
);"""

def generate_theme_store(name):
    return f"""import {{ create }} from 'zustand';
import {{ persist }} from 'zustand/middleware';

type AccentColor = 'blue' | 'violet' | 'emerald' | 'amber' | 'rose' | 'cyan';

interface ThemeState {{
  accentColor: AccentColor;
  setAccentColor: (color: AccentColor) => void;
}}

const accentMap: Record<AccentColor, string> = {{
  blue: '217 91% 60%',
  violet: '263 70% 50%',
  emerald: '160 84% 39%',
  amber: '38 92% 50%',
  rose: '347 77% 50%',
  cyan: '189 94% 43%',
}};

export const useThemeStore = create<ThemeState>()(
  persist(
    (set) => ({{
      accentColor: 'blue',
      setAccentColor: (color) => {{
        document.documentElement.style.setProperty('--accent-hsl', accentMap[color]);
        set({{ accentColor: color }});
      }},
    }}),
    {{
      name: '{name}_theme',
      partialize: (state) => ({{ accentColor: state.accentColor }}),
    }}
  )
);"""

def generate_common_types():
    return """export interface PaginatedResult<T> {
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
}"""

def generate_auth_types():
    return """export interface LoginPayload {
  email: string;
  password: string;
}

export interface RegisterPayload {
  name: string;
  email: string;
  password: string;
}

export interface AuthResponse {
  token: string;
  user: {
    id: string;
    email: string;
    name: string;
    role: string;
    companyId: string | null;
  };
}"""

def generate_route_guards():
    return """import { Navigate, Outlet } from 'react-router-dom';
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
}"""

def generate_error_boundary():
    return """import { Component, type ReactNode, type ErrorInfo } from 'react';

interface Props { children: ReactNode; fallback?: ReactNode; }
interface State { hasError: boolean; error: Error | null; }

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
            Reload
          </button>
        </div>
      );
    }
    return this.props.children;
  }
}"""

def generate_button_component():
    return """import { forwardRef, type ButtonHTMLAttributes } from 'react';

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
Button.displayName = 'Button';"""

def generate_card_component():
    return """import type { HTMLAttributes } from 'react';

interface CardProps extends HTMLAttributes<HTMLDivElement> {
  variant?: 'default' | 'glass';
}

export function Card({ variant = 'default', className = '', children, ...props }: CardProps) {
  const base = variant === 'glass'
    ? 'glass rounded-xl p-4'
    : 'bg-surface rounded-xl border border-border p-4';

  return (
    <div className={`${base} ${className}`} {...props}>
      {children}
    </div>
  );
}"""

def generate_input_component():
    return """import { forwardRef, type InputHTMLAttributes } from 'react';

interface InputProps extends InputHTMLAttributes<HTMLInputElement> {
  label?: string;
  error?: string;
}

export const Input = forwardRef<HTMLInputElement, InputProps>(
  ({ label, error, className = '', id, ...props }, ref) => (
    <div className="flex flex-col gap-1.5">
      {label && (
        <label htmlFor={id} className="text-sm font-medium text-foreground">
          {label}
        </label>
      )}
      <input
        ref={ref}
        id={id}
        className={`h-10 px-3 rounded-lg bg-surface-2 border border-border text-foreground
          placeholder:text-muted focus:outline-none focus:ring-2 focus:ring-accent/50
          focus:border-accent transition-all duration-200
          ${error ? 'border-red-500 focus:ring-red-500/50' : ''}
          ${className}`}
        {...props}
      />
      {error && <p className="text-xs text-red-400">{error}</p>}
    </div>
  )
);
Input.displayName = 'Input';"""

def generate_modal_component():
    return """import { useEffect, type ReactNode } from 'react';

interface ModalProps {
  isOpen: boolean;
  onClose: () => void;
  title: string;
  children: ReactNode;
}

export function Modal({ isOpen, onClose, title, children }: ModalProps) {
  useEffect(() => {
    const handleEsc = (e: KeyboardEvent) => {
      if (e.key === 'Escape') onClose();
    };
    if (isOpen) document.addEventListener('keydown', handleEsc);
    return () => document.removeEventListener('keydown', handleEsc);
  }, [isOpen, onClose]);

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center">
      <div className="absolute inset-0 bg-black/60 backdrop-blur-sm" onClick={onClose} />
      <div className="relative glass rounded-xl p-6 w-full max-w-md animate-fade-in">
        <h2 className="text-lg font-semibold mb-4">{title}</h2>
        {children}
      </div>
    </div>
  );
}"""

def generate_spinner_component():
    return """interface SpinnerProps {
  size?: 'sm' | 'md' | 'lg';
}

const sizes = { sm: 'w-4 h-4', md: 'w-6 h-6', lg: 'w-8 h-8' };

export function Spinner({ size = 'md' }: SpinnerProps) {
  return (
    <div className={`${sizes[size]} border-2 border-accent border-t-transparent rounded-full animate-spin`} />
  );
}"""

def generate_badge_component():
    return """interface BadgeProps {
  children: React.ReactNode;
  variant?: 'default' | 'success' | 'warning' | 'error' | 'info';
  className?: string;
}

const variants = {
  default: 'bg-surface-2 text-foreground',
  success: 'bg-emerald-500/15 text-emerald-400',
  warning: 'bg-amber-500/15 text-amber-400',
  error: 'bg-red-500/15 text-red-400',
  info: 'bg-blue-500/15 text-blue-400',
};

export function Badge({ children, variant = 'default', className = '' }: BadgeProps) {
  return (
    <span className={`inline-flex items-center px-2 py-0.5 rounded-md text-xs font-medium ${variants[variant]} ${className}`}>
      {children}
    </span>
  );
}"""

def generate_ui_barrel():
    return """export { Button } from './Button';
export { Card } from './Card';
export { Input } from './Input';
export { Modal } from './Modal';
export { Spinner } from './Spinner';
export { Badge } from './Badge';"""

def generate_layout():
    return """import { Outlet } from 'react-router-dom';
import { Sidebar } from './Sidebar';

export function AppLayout() {
  return (
    <div className="flex h-screen overflow-hidden">
      <Sidebar />
      <main className="flex-1 overflow-y-auto p-6">
        <div className="max-w-7xl mx-auto animate-fade-in">
          <Outlet />
        </div>
      </main>
    </div>
  );
}"""

def generate_sidebar(name, features):
    nav_items = ",\n".join([
        f"    {{ label: '{f.capitalize()}', path: '/{f}', icon: '📋' }}"
        for f in features
    ])
    return f"""import {{ NavLink }} from 'react-router-dom';
import {{ useAuthStore }} from '@/store/authStore';

const navItems = [
{nav_items}
];

export function Sidebar() {{
  const user = useAuthStore((s) => s.user);
  const logout = useAuthStore((s) => s.logout);

  return (
    <aside className="w-64 h-screen bg-surface border-r border-border flex flex-col">
      <div className="p-4 border-b border-border">
        <h1 className="text-lg font-bold text-accent">{name}</h1>
      </div>

      <nav className="flex-1 p-3 space-y-1">
        {{navItems.map((item) => (
          <NavLink
            key={{item.path}}
            to={{item.path}}
            className={{({{ isActive }}) =>
              `flex items-center gap-3 px-3 py-2 rounded-lg text-sm transition-all duration-200
              ${{isActive
                ? 'bg-accent/10 text-accent font-medium'
                : 'text-muted hover:text-foreground hover:bg-surface-2'}}`
            }}
          >
            <span>{{item.icon}}</span>
            <span>{{item.label}}</span>
          </NavLink>
        ))}}
      </nav>

      <div className="p-4 border-t border-border">
        <div className="flex items-center gap-3">
          <div className="w-8 h-8 rounded-full bg-accent/20 flex items-center justify-center text-sm font-medium text-accent">
            {{user?.name?.charAt(0) || '?'}}
          </div>
          <div className="flex-1 min-w-0">
            <p className="text-sm font-medium truncate">{{user?.name}}</p>
            <p className="text-xs text-muted truncate">{{user?.email}}</p>
          </div>
          <button onClick={{logout}} className="text-muted hover:text-red-400 transition" title="Logout">
            ⬅
          </button>
        </div>
      </div>
    </aside>
  );
}}"""

def generate_login_page():
    return """import { useState } from 'react';
import { Link } from 'react-router-dom';
import { Button } from '@/components/ui/Button';
import { Input } from '@/components/ui/Input';

export default function LoginPage() {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    // TODO: Implement login
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-[hsl(var(--bg))]">
      <div className="w-full max-w-sm glass rounded-xl p-8 animate-fade-in">
        <h1 className="text-2xl font-bold text-center mb-6">Welcome Back</h1>
        <form onSubmit={handleSubmit} className="space-y-4">
          <Input label="Email" type="email" value={email} onChange={(e) => setEmail(e.target.value)} />
          <Input label="Password" type="password" value={password} onChange={(e) => setPassword(e.target.value)} />
          <Button type="submit" className="w-full">Sign In</Button>
        </form>
        <p className="text-center text-sm text-muted mt-4">
          Don't have an account? <Link to="/register" className="text-accent hover:underline">Sign Up</Link>
        </p>
      </div>
    </div>
  );
}"""

def generate_register_page():
    return """import { useState } from 'react';
import { Link } from 'react-router-dom';
import { Button } from '@/components/ui/Button';
import { Input } from '@/components/ui/Input';

export default function RegisterPage() {
  const [name, setName] = useState('');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    // TODO: Implement registration
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-[hsl(var(--bg))]">
      <div className="w-full max-w-sm glass rounded-xl p-8 animate-fade-in">
        <h1 className="text-2xl font-bold text-center mb-6">Create Account</h1>
        <form onSubmit={handleSubmit} className="space-y-4">
          <Input label="Name" value={name} onChange={(e) => setName(e.target.value)} />
          <Input label="Email" type="email" value={email} onChange={(e) => setEmail(e.target.value)} />
          <Input label="Password" type="password" value={password} onChange={(e) => setPassword(e.target.value)} />
          <Button type="submit" className="w-full">Create Account</Button>
        </form>
        <p className="text-center text-sm text-muted mt-4">
          Already have an account? <Link to="/login" className="text-accent hover:underline">Sign In</Link>
        </p>
      </div>
    </div>
  );
}"""

def generate_feature_page(feature_name):
    return f"""import {{ Card }} from '@/components/ui/Card';

export default function {feature_name}Page() {{
  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-bold">{feature_name}</h1>
      </div>

      <Card>
        <p className="text-muted">
          {feature_name} page content goes here. Replace this with your feature implementation.
        </p>
      </Card>
    </div>
  );
}}"""

def generate_test_setup():
    return """import '@testing-library/jest-dom';

class MockIntersectionObserver {
  observe = vi.fn();
  unobserve = vi.fn();
  disconnect = vi.fn();
}

Object.defineProperty(window, 'IntersectionObserver', {
  writable: true,
  value: MockIntersectionObserver,
});"""

def generate_i18n_index():
    return """import en from './locales/en';
import ptBR from './locales/pt-BR';

type Locale = 'en' | 'pt-BR';
type Translations = typeof en;

const locales: Record<Locale, Translations> = { en, 'pt-BR': ptBR };

function getNestedValue(obj: Record<string, unknown>, path: string): string {
  const value = path.split('.').reduce<unknown>((acc, key) => {
    if (acc && typeof acc === 'object') return (acc as Record<string, unknown>)[key];
    return undefined;
  }, obj);
  return typeof value === 'string' ? value : path;
}

export function useT() {
  const locale: Locale = (localStorage.getItem('locale') as Locale) || detectBrowserLocale();
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
  return 'en';
}"""

def generate_locale_en(features):
    nav_items = ",\n".join([f'    {f}: "{f.capitalize()}"' for f in features])
    return f"""export default {{
  nav: {{
{nav_items}
  }},
  auth: {{
    login: {{
      title: 'Welcome Back',
      submit: 'Sign In',
      noAccount: "Don't have an account?",
      signUp: 'Sign Up',
    }},
    register: {{
      title: 'Create Account',
      submit: 'Create Account',
      hasAccount: 'Already have an account?',
      signIn: 'Sign In',
    }},
  }},
  common: {{
    loading: 'Loading...',
    error: 'Something went wrong',
    save: 'Save',
    cancel: 'Cancel',
    delete: 'Delete',
    edit: 'Edit',
    create: 'Create',
    search: 'Search...',
  }},
}};"""

def generate_locale_ptbr(features):
    translations = {"dashboard": "Painel", "tasks": "Tarefas", "projects": "Projetos"}
    nav_items = ",\n".join([f'    {f}: "{translations.get(f, f.capitalize())}"' for f in features])
    return f"""export default {{
  nav: {{
{nav_items}
  }},
  auth: {{
    login: {{
      title: 'Bem-vindo de volta',
      submit: 'Entrar',
      noAccount: 'Não tem uma conta?',
      signUp: 'Cadastre-se',
    }},
    register: {{
      title: 'Criar Conta',
      submit: 'Criar Conta',
      hasAccount: 'Já tem uma conta?',
      signIn: 'Entrar',
    }},
  }},
  common: {{
    loading: 'Carregando...',
    error: 'Algo deu errado',
    save: 'Salvar',
    cancel: 'Cancelar',
    delete: 'Excluir',
    edit: 'Editar',
    create: 'Criar',
    search: 'Buscar...',
  }},
}};"""


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Scaffold React + TypeScript Frontend")
    parser.add_argument("--name", required=True, help="Project name (e.g., MyApp)")
    parser.add_argument("--output", default=".", help="Output directory")
    parser.add_argument("--css", default="tailwind", choices=["tailwind", "styled"], help="CSS approach")
    parser.add_argument("--features", nargs="+", default=["dashboard", "tasks", "projects"], help="Feature names")
    args = parser.parse_args()

    scaffold(args.name, args.output, args.css, args.features)
