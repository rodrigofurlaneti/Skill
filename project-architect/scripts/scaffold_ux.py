#!/usr/bin/env python3
"""
Scaffold Generator for UX/UI Design System
Generates a complete Design System structure, UI tokens, and Shell layouts.

Usage:
    python scaffold_ux.py --name MyApp --output ./output --theme dark
"""

import argparse
import os
from pathlib import Path

def create_file(path: str, content: str):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f"  Created: {path}")

def scaffold(name: str, output: str, theme: str = "dark"):
    base = Path(output) / f"{name}-design-system"
    docs = base / "docs"
    tokens = base / "tokens"
    components = base / "ui-library"

    print(f"\n🎨 Scaffolding {name} UX/UI Design System")
    print(f"   Theme: {theme}")
    print(f"   Output: {base}\n")

    # ========== Design Manifesto ==========
    create_file(str(base / "ux-ui-patterns.md"), generate_ux_strategy(name))
    
    # ========== Style Tokens (Tailwind/CSS Vars) ==========
    create_file(str(tokens / "colors.json"), generate_color_tokens())
    create_file(str(tokens / "typography.json"), generate_typography_tokens())
    create_file(str(base / "tailwind.theme.config.js"), generate_tailwind_theme())

    # ========== Documentation & Patterns ==========
    create_file(str(docs / "ACCESSIBILITY.md"), generate_a11y_guidelines())
    create_file(str(docs / "COMPONENTS.md"), generate_component_specs())

    # ========== Base UI Shells (React Templates) ==========
    create_file(str(components / "Layouts" / "MainShell.tsx"), generate_main_shell(name))
    create_file(str(components / "Glass" / "GlassCard.tsx"), generate_glass_card())
    create_file(str(components / "Navigation" / "Sidebar.tsx"), generate_sidebar_template(name))

    print(f"\n✅ UX Scaffold complete!")
    print(f"   Next steps:")
    print(f"   1. Review ux-ui-patterns.md for the 'Distinctive, not decorative' approach.")
    print(f"   2. Import tailwind.theme.config.js into your frontend project.")
    print(f"   3. Use the GlassCard.tsx for high-performance glassmorphism UI.")

# ==================== GENERATORS ====================

def generate_ux_strategy(name):
    return f"""# UX Strategy — {name}

## Design Principles
1. **Distinctive, not decorative**: Every element must serve a functional purpose.
2. **Glassmorphism Depth**: Use blur and transparency to define layers of information.
3. **Typography First**: Leverage 'Plus Jakarta Sans' for a high-tech, professional feel.

## User Flow Objectives
- Minimize cognitive load with clear hierarchies.
- Ensure actions are reachable within one click for common tasks.
"""

def generate_color_tokens():
    return """{
  "background": "hsl(220 20% 8%)",
  "surface": "hsl(220 18% 12% / 0.6)",
  "accent": {
    "blue": "hsl(217 91% 60%)",
    "violet": "hsl(263 70% 50%)",
    "emerald": "hsl(160 84% 39%)"
  },
  "border": "hsl(220 14% 20% / 0.5)"
}"""

def generate_tailwind_theme():
    return """module.exports = {
  theme: {
    extend: {
      fontFamily: {
        sans: ['Plus Jakarta Sans', 'sans-serif'],
      },
      backdropBlur: {
        glass: '12px',
      },
      colors: {
        'surface-glass': 'hsla(220, 18%, 12%, 0.6)',
      }
    }
  }
}"""

def generate_a11y_guidelines():
    return """# Accessibility (a11y) Guidelines

- **Contrast**: Maintain a 4.5:1 ratio for all text elements.
- **Keyboard**: Every interactive component must have a `focus` state.
- **ARIA**: Use `aria-label` for icon-only buttons.
"""

def generate_glass_card():
    return """import React from 'react';

export const GlassCard: React.FC<{children: React.ReactNode}> = ({ children }) => (
  <div className="glass rounded-xl p-6 border border-white/10 backdrop-blur-glass shadow-xl">
    {children}
  </div>
);"""

def generate_main_shell(name):
    return f"""import React from 'react';

export const MainShell: React.FC = () => {{
  return (
    <div className="min-h-screen bg-[hsl(var(--bg))] text-[hsl(var(--foreground))]">
      <div className="flex">
        {/* Sidebar and Navigation would go here */}
        <main className="flex-1 p-8 animate-fade-in">
          {{/* Content Slot */}}
        </main>
      </div>
    </div>
  );
}};"""

def generate_typography_tokens():
    return """{
  "headings": {
    "font": "Plus Jakarta Sans",
    "weight": "700",
    "tracking": "tight"
  },
  "body": {
    "font": "Plus Jakarta Sans",
    "weight": "400",
    "lineHeight": "1.6"
  }
}"""

def generate_component_specs():
    return """# Component Specifications

- **Buttons**: Must have hover states with `translate-y-[-2px]` and active compression.
- **Inputs**: Glowing ring on focus using `ring-2 ring-accent/50`.
- **Loading**: Use branded staggered spinners, never generic ones.
"""

def generate_sidebar_template(name):
    return f"""import React from 'react';

export const Sidebar: React.FC = () => (
  <aside className="w-64 h-screen glass border-r border-border p-4 flex flex-col">
    <div className="p-4 border-b border-border">
      <h1 className="text-xl font-bold text-accent">{name}</h1>
    </div>
    <nav className="mt-8 flex-1">
      {/* Links go here */}
    </nav>
  </aside>
);"""

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Scaffold UX/UI Design System")
    parser.add_argument("--name", required=True, help="Project name")
    parser.add_argument("--output", default=".", help="Output directory")
    parser.add_argument("--theme", default="dark", choices=["dark", "light"], help="Base theme")
    args = parser.parse_args()

    scaffold(args.name, args.output, args.theme)