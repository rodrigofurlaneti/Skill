#!/usr/bin/env python3
"""
Scaffold Generator for React + TypeScript Frontend (Orchestrator Mode)
Uses senior-level blueprints for UI/UX and State Management.

Usage:
    python scripts/scaffold_frontend.py --name MyApp --output ./output
"""

import argparse
import os
from pathlib import Path

SKILL_ROOT = Path(__file__).resolve().parent.parent
BLUEPRINT_DIR = SKILL_ROOT / "blueprints" / "frontend"

def load_blueprint(template_path, replacements):
    full_path = BLUEPRINT_DIR / template_path
    if not full_path.exists():
        return f"// Template {template_path} not found in blueprints/frontend/"
        
    with open(full_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    for key, value in replacements.items():
        content = content.replace(f"{{{{{key}}}}}", str(value))
    return content

def create_file(path: str, content: str):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f"  Created: {path}")

def scaffold(name: str, output: str, features: list[str] = None):
    if features is None:
        features = ["dashboard", "tasks"]

    base = Path(output) / f"{name}-frontend"
    src = base / "src"
    ctx = {"NAME": name, "NAME_LOWER": name.lower()}

    print(f"\n🎨 Scaffolding {name} Frontend (React + Glassmorphism UX)")

    # ========== 1. CONFIGURAÇÕES BASE ==========
    create_file(str(base / "package.json"), load_blueprint("package.json.blueprint", ctx))
    create_file(str(base / "tailwind.config.js"), load_blueprint("tailwind.config.js.blueprint", ctx))
    create_file(str(src / "index.css"), load_blueprint("index.css.blueprint", ctx))

    # ========== 2. CORE & STATE ==========
    create_file(str(src / "store" / "authStore.ts"), load_blueprint("authStore.ts.blueprint", ctx))
    create_file(str(src / "api" / "client.ts"), load_blueprint("api_client.ts.blueprint", ctx))

    # ========== 3. COMPONENTS & UI ==========
    ui_components = ["Button", "Card", "Input", "Modal"]
    for comp in ui_components:
        create_file(str(src / "components" / "ui" / f"{comp}.tsx"), 
                    load_blueprint(f"ui/{comp}.tsx.blueprint", ctx))

    # ========== 4. APP SHELL ==========
    create_file(str(src / "App.tsx"), load_blueprint("App.tsx.blueprint", ctx))

    # ========== 5. PAGES & FEATURES ==========
    for feature in features:
        feature_ctx = {**ctx, "FEATURE_NAME": feature, "FEATURE_CAP": feature.capitalize()}
        create_file(str(src / "pages" / feature / f"{feature.capitalize()}Page.tsx"),
                    load_blueprint("Page.tsx.blueprint", feature_ctx))

    print(f"\n✅ Frontend '{name}' generated with distinctive UI tokens!")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--name", required=True)
    parser.add_argument("--output", default=".")
    parser.add_argument("--features", nargs="+")
    args = parser.parse_args()

    scaffold(args.name, args.output, args.features)