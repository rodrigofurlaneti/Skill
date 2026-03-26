#!/usr/bin/env python3
"""
Scaffold Generator for .NET Clean Architecture Backend (Orchestrator Mode)
Now uses external blueprints for better maintenance and clean code.

Usage:
    python scripts/scaffold_backend.py --name MyApp --output ./output --db postgresql
"""

import argparse
import os
from pathlib import Path

# Configuração de caminhos (relativo ao skill root)
SKILL_ROOT = Path(__file__).resolve().parent.parent
BLUEPRINT_DIR = SKILL_ROOT / "blueprints"

def load_blueprint(template_path, replacements):
    """Lê um arquivo de blueprint e substitui os placeholders {{KEY}}."""
    full_path = BLUEPRINT_DIR / template_path
    if not full_path.exists():
        # Fallback para string básica caso o blueprint ainda não tenha sido criado
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

def scaffold(name: str, output: str, db: str = "sqlserver", entities: list[str] = None):
    if entities is None:
        entities = ["Task", "Project"]

    base = Path(output) / name
    src = base / "src"
    
    # Contexto global de substituição
    ctx = {"NAMESPACE": name, "DB_PROVIDER": db}

    print(f"\n🏗️  Scaffolding {name} Backend (Clean Architecture + Blueprints)")
    print(f"   Database: {db} | Entities: {', '.join(entities)}\n")

    # ========== 1. DOMAIN LAYER ==========
    domain_path = src / f"{name}.Domain"
    create_file(str(domain_path / "Common" / "Entity.cs"), 
                load_blueprint("backend/BaseEntity.cs.blueprint", ctx))
    
    for entity in entities:
        entity_ctx = {**ctx, "ENTITY_NAME": entity}
        create_file(str(domain_path / "Entities" / f"{entity}.cs"), 
                    load_blueprint("backend/Entity.cs.blueprint", entity_ctx))

    # ========== 2. APPLICATION LAYER ==========
    app_path = src / f"{name}.Application"
    create_file(str(app_path / "Common" / "Models" / "Result.cs"), 
                load_blueprint("backend/ResultPattern.cs.blueprint", ctx))
    
    for entity in entities:
        feature_ctx = {**ctx, "ENTITY_NAME": entity}
        create_file(str(app_path / "Features" / f"{entity}s" / "Commands" / f"Create{entity}Command.cs"),
                    load_blueprint("backend/CreateCommand.cs.blueprint", feature_ctx))

    # ========== 3. INFRASTRUCTURE LAYER ==========
    infra_path = src / f"{name}.Infrastructure"
    create_file(str(infra_path / "Persistence" / "AppDbContext.cs"), 
                load_blueprint("backend/AppDbContext.cs.blueprint", ctx))

    # ========== 4. INFRASTRUCTURE LAYER (extras) ==========
    create_file(str(infra_path / "Persistence" / "Repositories" / "Repository.cs"),
                load_blueprint("backend/Repository.cs.blueprint", ctx))
    create_file(str(infra_path / "InfrastructureServiceRegistration.cs"),
                load_blueprint("backend/InfrastructureDI.cs.blueprint", ctx))

    # ========== 5. API LAYER ==========
    api_path = src / f"{name}.API"
    create_file(str(api_path / "Program.cs"),
                load_blueprint("backend/Program.cs.blueprint", ctx))
    create_file(str(api_path / "Controllers" / "ApiController.cs"),
                load_blueprint("backend/ApiController.cs.blueprint", ctx))

    for entity in entities:
        entity_ctx = {**ctx, "ENTITY_NAME": entity}
        create_file(str(api_path / "Controllers" / f"{entity}sController.cs"),
                    load_blueprint("backend/EntityController.cs.blueprint", entity_ctx))

    # ========== 6. DOMAIN EXTRAS ==========
    create_file(str(domain_path / "Common" / "DomainEvent.cs"),
                load_blueprint("backend/DomainEvent.cs.blueprint", ctx))
    create_file(str(domain_path / "Common" / "DomainException.cs"),
                load_blueprint("backend/DomainException.cs.blueprint", ctx))
    create_file(str(domain_path / "Interfaces" / "IRepository.cs"),
                load_blueprint("backend/IRepository.cs.blueprint", ctx))

    # ========== 7. APPLICATION EXTRAS ==========
    create_file(str(app_path / "ApplicationServiceRegistration.cs"),
                load_blueprint("backend/ApplicationDI.cs.blueprint", ctx))

    print(f"\n✅ Backend '{name}' generated using sênior blueprints!")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Scaffold .NET Backend")
    parser.add_argument("--name", required=True)
    parser.add_argument("--output", default=".")
    parser.add_argument("--db", default="sqlserver")
    parser.add_argument("--entities", nargs="+")
    args = parser.parse_args()

    scaffold(args.name, args.output, args.db, args.entities)