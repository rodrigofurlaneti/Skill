#!/usr/bin/env python3
"""
Scaffold Generator for .NET Clean Architecture Backend (Orchestrator Mode)
Master Orchestrator for Multi-tenant SaaS Projects.

Usage:
    python scripts/scaffold_backend.py --name MyApp --output ./output --db mysql
"""

import argparse
import os
import sys
from pathlib import Path

# Configuração de caminhos (relativo ao skill root)
SKILL_ROOT = Path(__file__).resolve().parent.parent
BLUEPRINT_DIR = SKILL_ROOT / "blueprints"

def load_blueprint(template_path, replacements):
    """Lê um arquivo de blueprint e substitui os placeholders {{KEY}}."""
    full_path = BLUEPRINT_DIR / template_path
    if not full_path.exists():
        print(f"⚠️  Warning: Blueprint {template_path} not found at {full_path}")
        return f"// Template {template_path} not found. Add it to blueprints/ folder."
        
    with open(full_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    for key, value in replacements.items():
        content = content.replace(f"{{{{{key}}}}}", str(value))
    return content

def create_file(path: Path, content: str):
    """Cria o arquivo e os diretórios pai se não existirem."""
    os.makedirs(path.parent, exist_ok=True)
    with open(path, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f"  Created: {path.relative_to(path.parents[3] if len(path.parents) > 3 else path.parents[0])}")

def scaffold(name: str, output: str, db: str = "mysql", extra_entities: list[str] = None):
    # Core Entities que TODO projeto seu deve ter (O padrão que definimos)
    core_entities = ["Company", "SubscriptionPlan", "User", "UserSettings", "CompanyInvite", "Notification"]
    
    # Entidades de negócio específicas do projeto atual
    business_entities = extra_entities if extra_entities else ["Task", "Project"]
    
    all_entities = core_entities + business_entities

    base = Path(output) / name
    src = base / "src"
    
    # Contexto global de substituição
    ctx = {"NAMESPACE": name, "DB_PROVIDER": db}

    print(f"\n🏗️  Scaffolding {name} Backend (Clean Architecture + Multi-tenant SaaS)")
    print(f"   Database: {db}")
    print(f"   Core Entities: {', '.join(core_entities)}")
    print(f"   Business Entities: {', '.join(business_entities)}\n")

    # ========== 1. DOMAIN LAYER ==========
    domain_path = src / f"{name}.Domain"
    
    # Common & Base
    create_file(domain_path / "Common" / "Entity.cs", load_blueprint("backend/BaseEntity.cs.blueprint", ctx))
    create_file(domain_path / "Common" / "DomainEvent.cs", load_blueprint("backend/DomainEvent.cs.blueprint", ctx))
    create_file(domain_path / "Common" / "DomainException.cs", load_blueprint("backend/DomainException.cs.blueprint", ctx))
    create_file(domain_path / "Interfaces" / "IRepository.cs", load_blueprint("backend/IRepository.cs.blueprint", ctx))
    create_file(domain_path / "Interfaces" / "IAggregateRoot.cs", "// Marker Interface\nnamespace {{NAMESPACE}}.Domain.Interfaces;\npublic interface IAggregateRoot {}")

    # Entities (Core + Business)
    for entity in all_entities:
        entity_ctx = {**ctx, "ENTITY_NAME": entity}
        # Tenta carregar um blueprint específico (ex: Company.cs.blueprint) 
        # ou usa o genérico Entity.cs.blueprint
        blueprint_file = f"backend/Domain/Entities/{entity}.cs.blueprint"
        if not (BLUEPRINT_DIR / blueprint_file).exists():
            blueprint_file = "backend/Entity.cs.blueprint"
            
        create_file(domain_path / "Entities" / f"{entity}.cs", load_blueprint(blueprint_file, entity_ctx))

    # ========== 2. APPLICATION LAYER ==========
    app_path = src / f"{name}.Application"
    create_file(app_path / "Common" / "Models" / "Result.cs", load_blueprint("backend/ResultPattern.cs.blueprint", ctx))
    create_file(app_path / "ApplicationServiceRegistration.cs", load_blueprint("backend/ApplicationDI.cs.blueprint", ctx))
    
    # Commands for Business Entities
    for entity in business_entities:
        feature_ctx = {**ctx, "ENTITY_NAME": entity}
        create_file(app_path / "Features" / f"{entity}s" / "Commands" / f"Create{entity}Command.cs",
                    load_blueprint("backend/CreateCommand.cs.blueprint", feature_ctx))

    # ========== 3. INFRASTRUCTURE LAYER ==========
    infra_path = src / f"{name}.Infrastructure"
    
    # Persistence & Multi-tenancy
    create_file(infra_path / "Persistence" / "AppDbContext.cs", load_blueprint("backend/AppDbContext.cs.blueprint", ctx))
    create_file(infra_path / "Persistence" / "Repositories" / "Repository.cs", load_blueprint("backend/Repository.cs.blueprint", ctx))
    create_file(infra_path / "Persistence" / "Interceptors" / "AuditInterceptor.cs", load_blueprint("backend/AuditInterceptor.cs.blueprint", ctx))
    create_file(infra_path / "MultiTenancy" / "TenantMiddleware.cs", load_blueprint("backend/TenantMiddleware.cs.blueprint", ctx))
    create_file(infra_path / "InfrastructureServiceRegistration.cs", load_blueprint("backend/InfrastructureDI.cs.blueprint", ctx))

    # ========== 4. API LAYER ==========
    api_path = src / f"{name}.API"
    create_file(api_path / "Program.cs", load_blueprint("backend/Program.cs.blueprint", ctx))
    create_file(api_path / "Controllers" / "ApiController.cs", load_blueprint("backend/ApiController.cs.blueprint", ctx))

    # Controllers for Business Entities
    for entity in business_entities:
        entity_ctx = {**ctx, "ENTITY_NAME": entity}
        create_file(api_path / "Controllers" / f"{entity}sController.cs",
                    load_blueprint("backend/EntityController.cs.blueprint", entity_ctx))

    print(f"\n✅ Senior Backend Architecture for '{name}' generated successfully!")
    print(f"🚀 Path: {base.resolve()}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Scaffold .NET Backend Architect")
    parser.add_argument("--name", required=True, help="Project name (e.g. UpTask)")
    parser.add_argument("--output", default="./output", help="Output directory")
    parser.add_argument("--db", default="mysql", help="Database provider (mysql, postgresql, sqlserver)")
    parser.add_argument("--entities", nargs="+", help="Extra business entities")
    
    args = parser.parse_args()
    scaffold(args.name, args.output, args.db, args.entities)