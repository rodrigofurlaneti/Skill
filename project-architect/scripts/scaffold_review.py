#!/usr/bin/env python3
"""
Scaffold Generator for Code Review & Architecture Governance (Orchestrator Mode)
Enforces DDD, Clean Arch boundaries and PR standards using external blueprints.

Usage:
    python scripts/scaffold_review.py --name MyApp --output ./output
"""

import argparse
import os
from pathlib import Path

# Configuração de caminhos para os Blueprints
BLUEPRINT_DIR = Path("project-architect/blueprints/review")

def load_blueprint(template_path, replacements):
    """Lê o blueprint e injeta as variáveis do projeto."""
    full_path = BLUEPRINT_DIR / template_path
    if not full_path.exists():
        return f"# Template {template_path} not found. Please create it in blueprints/review/"
        
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
    github = base / ".github"
    tests = base / "tests" / f"{name}.Architecture.Tests"
    
    ctx = {"NAME": name}

    print(f"\n🕵️‍♂️ Scaffolding {name} Governance (Tech Lead & Code Review)")

    # ========== 1. GOVERNANÇA DE REPOSITÓRIO ==========
    # Gera o template de Pull Request para o GitHub
    create_file(str(github / "PULL_REQUEST_TEMPLATE.md"), 
                load_blueprint("pull_request.md.blueprint", ctx))

    # Gera o Guia de Revisão para o time
    create_file(str(base / "CODE_REVIEW_GUIDELINES.md"), 
                load_blueprint("review_guidelines.md.blueprint", ctx))

    # ========== 2. TESTES DE ARQUITETURA (NETARCHTEST) ==========
    # Garante que as camadas não se cruzem (ex: Domain não depende de Infra)
    create_file(str(tests / f"{name}.Architecture.Tests.csproj"), 
                load_blueprint("ArchTests.csproj.blueprint", ctx))
                
    create_file(str(tests / "ArchitectureTests.cs"), 
                load_blueprint("ArchitectureTests.cs.blueprint", ctx))

    print(f"\n✅ Governance scaffold complete for '{name}'!")
    print(f"   Tech Lead Tip: Run 'dotnet test' to enforce architectural boundaries.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Scaffold Code Review & Governance")
    parser.add_argument("--name", required=True, help="Project name")
    parser.add_argument("--output", default=".", help="Output directory")
    args = parser.parse_args()

    scaffold(args.name, args.output)