#!/usr/bin/env python3
"""
Scaffold Generator for Identity & Security (Orchestrator Mode)
Uses external blueprints for authentication and JWT configuration.

Usage:
    python scripts/scaffold_auth.py --name MyApp --output ./output
"""

import argparse
import os
from pathlib import Path

SKILL_ROOT = Path(__file__).resolve().parent.parent
BLUEPRINT_DIR = SKILL_ROOT / "blueprints"

def load_blueprint(template_path, replacements):
    """Reads a blueprint file and replaces {{KEY}} placeholders."""
    full_path = BLUEPRINT_DIR / template_path
    if not full_path.exists():
        return f"// Template {template_path} not found. Add it to blueprints/ folder."

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

def scaffold(name: str, output: str):
    base = Path(output) / name
    api = base / "src" / f"{name}.API"
    infra = base / "src" / f"{name}.Infrastructure"

    ctx = {"NAMESPACE": name}

    print(f"\n🔐 Scaffolding {name} Security & Identity (Blueprint Mode)")

    # Auth Controller
    create_file(str(api / "Controllers" / "AuthController.cs"),
                load_blueprint("auth/AuthController.cs.blueprint", ctx))

    # JWT Provider
    create_file(str(infra / "Security" / "JwtProvider.cs"),
                load_blueprint("auth/JwtProvider.cs.blueprint", ctx))

    print(f"\n✅ Security scaffold complete!")
    print(f"   Patterns applied:")
    print(f"   1. JWT with RS256/HS256 and TenantId claims")
    print(f"   2. Refresh Token rotation")
    print(f"   3. AllowAnonymous on public endpoints only")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Scaffold Security & Identity")
    parser.add_argument("--name", required=True, help="Project name")
    parser.add_argument("--output", default=".", help="Output directory")
    args = parser.parse_args()
    scaffold(args.name, args.output)