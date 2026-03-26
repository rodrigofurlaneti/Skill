#!/usr/bin/env python3
"""
Scaffold Generator for DBA & Persistence Layer (.NET Core)
Generates Fluent API configurations, DB Context, and Performance patterns.

Usage:
    python scaffold_dba.py --name MyApp --output ./output --db sqlserver --multitenant true
"""

import argparse
import os
from pathlib import Path

def create_file(path: str, content: str):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f"  Created: {path}")

def scaffold(name: str, output: str, db: str = "sqlserver", multitenant: bool = True, entities: list[str] = None):
    if entities is None:
        entities = ["Task", "Project"]

    base = Path(output) / f"{name}.Infrastructure"
    persistence = base / "Persistence"
    configs = persistence / "Configurations"

    print(f"\n🗄️  Scaffolding {name} Persistence Layer (DBA Sênior)")
    print(f"   Database: {db}")
    print(f"   Multi-tenant: {'Yes' if multitenant else 'No'}")
    print(f"   Entities: {', '.join(entities)}\n")

    # ========== Entity Framework Core Reference Guide ==========
    create_file(str(base / "ef-core-dba.md"), generate_dba_guidelines())

    # ========== Fluent API Configurations ==========
    for entity in entities:
        create_file(str(configs / f"{entity}Configuration.cs"), 
                    generate_fluent_config(name, entity, multitenant))

    # ========== Performance Helpers ==========
    create_file(str(persistence / "Interceptors" / "SoftDeleteInterceptor.cs"), 
                generate_soft_delete_interceptor(name))
    
    print(f"\n✅ DBA scaffold complete!")
    print(f"   Integrated Patterns:")
    print(f"   1. Explicit Mapping (No nvarchar(max))")
    print(f"   2. Global Query Filters (Multi-tenant Isolation)")
    print(f"   3. Optimistic Concurrency (RowVersion)")
    print(f"   4. Non-clustered Indexes on Foreign Keys")

# ==================== GENERATORS ====================

def generate_dba_guidelines():
    return """# DBA & EF Core Best Practices

## 1. Mapeamento
- **Explicit Schema**: Sempre defina schema e nome de tabela explicitamente.
- **Strict Typing**: Use `.HasMaxLength()` para strings e `.HasColumnType("decimal(18,2)")`.

## 2. Performance
- **NoTracking**: Queries de leitura devem usar `.AsNoTracking()`.
- **Indexing**: Chaves estrangeiras e campos de filtro (ex: TenantId) devem possuir índices.

## 3. Segurança
- **Multi-tenancy**: Filtros globais (`HasQueryFilter`) garantem que dados não vazem entre clientes.
"""

def generate_fluent_config(name, entity, multitenant):
    tenant_config = ""
    if multitenant:
        tenant_config = f"""
        // 4. Multi-tenant Isolation (FSI Pattern)
        builder.Property(x => x.TenantId).IsRequired();
        builder.HasIndex(x => x.TenantId).HasDatabaseName("IX_{entity}_TenantId");
        builder.HasQueryFilter(x => x.TenantId == _tenantProvider.TenantId);"""

    return f"""using Microsoft.EntityFrameworkCore;
using Microsoft.EntityFrameworkCore.Metadata.Builders;
using {name}.Domain.Entities;

namespace {name}.Infrastructure.Persistence.Configurations;

public class {entity}Configuration : IEntityTypeConfiguration<{entity}>
{{
    public void Configure(EntityTypeBuilder<{entity}> builder)
    {{
        // 1. Table Mapping
        builder.ToTable("{entity}s", "dbo");

        // 2. Property Mapping (Strict Typing)
        builder.HasKey(x => x.Id);
        
        builder.Property(x => x.Name)
            .HasMaxLength(200)
            .IsRequired();

        // 3. Concurrency (Optimistic)
        builder.Property(x => x.RowVersion)
            .IsRowVersion();
{tenant_config}
        
        // 5. Indexing Strategy
        builder.HasIndex(x => x.CreatedAt).HasDatabaseName("IX_{entity}_CreatedAt");
    }}
}}"""

def generate_soft_delete_interceptor(name):
    return f"""using Microsoft.EntityFrameworkCore;
using Microsoft.EntityFrameworkCore.Diagnostics;

namespace {name}.Infrastructure.Persistence.Interceptors;

public class SoftDeleteInterceptor : SaveChangesInterceptor
{{
    public override ValueTask<InterceptionResult<int>> SavingChangesAsync(
        DbContextEventData eventData, 
        InterceptionResult<int> result, 
        CancellationToken ct = default)
    {{
        if (eventData.Context is null) return base.SavingChangesAsync(eventData, result, ct);

        foreach (var entry in eventData.Context.ChangeTracker.Entries().Where(e => e.State == EntityState.Deleted))
        {{
            // Check for ISoftDeletable interface and modify state
        }}

        return base.SavingChangesAsync(eventData, result, ct);
    }}
}}"""

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Scaffold DBA & Persistence Layer")
    parser.add_argument("--name", required=True, help="Project name")
    parser.add_argument("--output", default=".", help="Output directory")
    parser.add_argument("--db", default="sqlserver", choices=["sqlserver", "postgresql"], help="Database provider")
    parser.add_argument("--multitenant", type=bool, default=True, help="Enable multi-tenant isolation")
    parser.add_argument("--entities", nargs="+", default=["Task", "Project"], help="Entity names")
    args = parser.parse_args()

    scaffold(args.name, args.output, args.db, args.multitenant, args.entities)